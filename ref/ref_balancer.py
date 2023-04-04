from flask import Flask, jsonify, request
from kafka import KafkaProducer, KafkaConsumer
import json

app = Flask(__name__)

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

consumer = KafkaConsumer(
    'transactions', # Kafka topic to consume messages from
    bootstrap_servers=['localhost:9092'],
    enable_auto_commit=True,
    group_id='my-group')

bank_servers = ['http://localhost:5001', 'http://localhost:5002']
current_server = 0

def send_transaction(data):
    # send the transaction data to the Kafka topic
    producer.send('transactions', json.dumps(data).encode())

@app.route('/balance', methods=['GET'])
def get_balance():
    account_number = request.args.get('account_number')
    server_url = bank_servers[current_server]

    # robin round
    current_server = (current_server + 1) % len(bank_servers)
    
    return jsonify(requests.get(f'{server_url}/balance?account_number={account_number}').json())

@app.route('/credit', methods=['POST'])
def credit_account():
    data = json.loads(request.data)
    send_transaction(data)
    return jsonify({'status': 'success'})

@app.route('/debit', methods=['POST'])
def debit_account():
    data = json.loads(request.data)
    send_transaction(data)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run()