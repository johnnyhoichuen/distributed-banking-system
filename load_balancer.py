import json

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from flask import Flask, jsonify, request
import config
from config import APIType, Currency, ERROR_CODES
from marshmallow import Schema, fields

# TODO: add robin round mechanism
read_only_server = '5001'
general_server = '5002'
bank_servers_port = [read_only_server, general_server]
current_server = 0

# add tag in kafka value to specify which machine should work

def create_app(producer: KafkaProducer):
    app = Flask(__name__)

    # read-only operations

    @app.route('/accounts/<account_id>')
    def get_account_info(account_id):
        str(account_id) if not isinstance(account_id, str) else account_id

        key = APIType.ACC_INFO.value  # has to be bytes
        headers = [
            ("account_id", str(account_id).encode('utf-8'))
        ]

        # always select read_only_server
        value = read_only_server.encode('utf-8')

        producer.send(topic=config.read_topic, key=key, value=value, headers=headers)

        return "message sent"

    @app.route('/accounts/<account_id>/transactions')
    def get_transaction_history(account_id):
        account_id = str(account_id) if not isinstance(account_id, str) else account_id

        key = APIType.TRAN_HISTORY.value
        headers = [
            ("account_id", str(account_id).encode('utf-8'))
        ]

        # always select read_only_server
        value = read_only_server.encode('utf-8')

        producer.send(topic=config.read_topic, key=key, value=value, headers=headers)

        return "getting txn history"

    # transaction related operations

    # TODO: create account
    @app.route('/accounts', methods=['POST'])
    def create_account():
        data = request.get_json()
        print(data)

        # TODO: check account holder info




        data_byte = json.dumps(data).encode('utf-8') # format json body as bytes

        key = APIType.NEW_ACC.value
        headers = [
            ('data', data_byte)
        ]

        # server selection thru robin round
        global current_server
        current_server = (current_server + 1) % len(bank_servers_port)
        value = bank_servers_port[current_server].encode('utf-8')

        producer.send(topic=config.transaction_topic, key=key, value=value, headers=headers)

        return 'create acc'

    @app.route('/accounts/<account_id>/credits', methods=['POST'])
    def add_funds(account_id):
        data = request.get_json()  # data: amount, currency
        data['account_id'] = account_id
        data_str = json.dumps(data)

        key = APIType.ADD_FUND.value

        # server selection thru robin round
        global current_server
        current_server = (current_server + 1) % len(bank_servers_port)
        value = bank_servers_port[current_server].encode('utf-8')

        # send errors to server
        error_code = ''.encode('utf-8')
        if data['currency'] not in Currency:
            key = APIType.ERROR.value
            error_code = ERROR_CODES['100'].encode('utf-8')

        if int(data['amount']) <= 0:
            key = APIType.ERROR.value
            error_code = ERROR_CODES['101'].encode('utf-8')

        headers = [
            ('data', data_str.encode('utf-8')),
            ('error', error_code)
        ]

        producer.send(topic=config.transaction_topic, key=key, value=value, headers=headers)

        return 'add funds'

    @app.route('/accounts/<account_id>/debits', methods=['POST'])
    def withdraw_funds(account_id):
        data = request.get_json()  # data: amount, currency
        data['account_id'] = account_id
        data_str = json.dumps(data)

        key = APIType.ADD_FUND.value

        # server selection thru robin round
        global current_server
        current_server = (current_server + 1) % len(bank_servers_port)
        value = bank_servers_port[current_server].encode('utf-8')

        # send errors to server
        error_code = ''.encode('utf-8')
        if data['currency'] not in Currency:
            key = APIType.ERROR.value
            error_code = ERROR_CODES['100'].encode('utf-8')

        if int(data['amount']) <= 0:
            key = APIType.ERROR.value
            error_code = ERROR_CODES['101'].encode('utf-8')

        headers = [
            ('data', data_str.encode('utf-8')),
            ('error', error_code)
        ]

        producer.send(topic=config.transaction_topic, key=key, value=value, headers=headers)

        return 'withdraw funds'

    return app


if __name__ == "__main__":
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

    # create topics
    admin_client = KafkaAdminClient(bootstrap_servers="localhost:9092")
    current_topics = admin_client.list_topics()

    # add topic if needed
    topic_list = [NewTopic(name=config.read_topic, num_partitions=1, replication_factor=1),
                  NewTopic(name=config.transaction_topic, num_partitions=1, replication_factor=1)]

    # TODO: check if current topics contains topics in topic_list

    # run load balancer
    app = create_app(producer)
    app.run(host="127.0.0.1", port=5000, debug=True)
