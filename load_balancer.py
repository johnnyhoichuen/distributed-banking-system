import json
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from flask import Flask, request
import config
from config import APIType, Currency, ERROR_CODES

# robin round mechanism
# will be sent as kafka 'value' to specify which server should work
read_only_server = '5001'
general_server = '5002'
bank_servers_port = [read_only_server, general_server]
current_server = 0  # 0 to (len(bank_servers_port) - 1)

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

        key = APIType.TRAN_HISTORY.value # assign API type
        headers = [
            ("account_id", str(account_id).encode('utf-8'))
        ]

        # always select read_only_server
        value = read_only_server.encode('utf-8')

        producer.send(topic=config.read_topic, key=key, value=value, headers=headers)

        return "getting txn history"

    # transaction related operations

    @app.route('/accounts', methods=['POST'])
    def create_account():
        # format json body as bytes
        data = request.get_json()
        data_byte = json.dumps(data).encode('utf-8')

        key = APIType.NEW_ACC.value # assign API type

        # server selection thru robin round
        global current_server
        current_server = (current_server + 1) % len(bank_servers_port)
        value = bank_servers_port[current_server].encode('utf-8')

        # check account holder info
        # send errors to server
        error_code = ''.encode('utf-8')
        if data['currency'] not in Currency:
            key = APIType.ERROR.value
            error_code = ERROR_CODES['100'].encode('utf-8')
            print(f'currency error: {error_code}')

        # check user's name
        user_name = str(data['account_holder']['name'])
        user_name = user_name.replace(" ", "")
        if not user_name.isalpha():
            print(f'name: {user_name}, is alpha: {user_name.isalpha()}')

            key = APIType.ERROR.value
            error_code = ERROR_CODES['102'].encode('utf-8')
            print(f'account holder name error: {error_code}')

        headers = [
            ('data', data_byte),
            ('error', error_code)
        ]

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

        if float(data['amount']) <= 0:
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

        key = APIType.WITHDRAW_FUND.value

        # server selection thru robin round
        global current_server
        current_server = (current_server + 1) % len(bank_servers_port)
        value = bank_servers_port[current_server].encode('utf-8')

        # send errors to server
        error_code = ''.encode('utf-8')
        if data['currency'] not in Currency:
            key = APIType.ERROR.value
            error_code = ERROR_CODES['100'].encode('utf-8')

        if float(data['amount']) <= 0:
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
    # setup kafka producer
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

    # list out current topics
    admin_client = KafkaAdminClient(bootstrap_servers="localhost:9092")
    current_topics = admin_client.list_topics()
    # print(current_topics)

    # create kafka topics if needed
    required_topics = [config.read_topic, config.transaction_topic]
    topic_list = []
    for required_topic in required_topics:
        if required_topic not in current_topics:
            topic_list.append(NewTopic(name=required_topic, num_partitions=1, replication_factor=1))
    # print(topic_list)

    if topic_list:
        admin_client.create_topics(topic_list)
    else:
        print('all required topics exist')

    # run load balancer
    app = create_app(producer)
    app.run(host="127.0.0.1", port=5000, debug=True)
