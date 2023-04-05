import json
from datetime import datetime
from kafka import KafkaConsumer
from flask import Flask, jsonify, request
import argparse
from pymongo import MongoClient
from bson.objectid import ObjectId

import config
from config import APIType

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--topics', nargs='+', type=str)
	parser.add_argument('--port', type=str)
	args = parser.parse_args()

	# setup mongo
	print('setting up mongo')
	client = MongoClient(config.mongoUrl)
	# print(client.list_database_names())
	db = client['oslDB']
	# print(f'collection names: {db.list_collection_names()}\n')
	# print(db.accountHolders.find_one({"_id": ObjectId("642a9358d08ee9ba0d8b8b7e")}))
	# print('db search finished')

	# set up kafka consumer
	port = args.port
	topics = args.topics
	print('available topics: ')
	[print(topic) for topic in topics]
	print('\n')

	# topics subscription
	consumer = KafkaConsumer(bootstrap_servers=['localhost:9092'])
	consumer.subscribe(topics)

	# will be triggered if there's message available
	for message in consumer:
		# skip if not selected by load balancer
		load_balancer_selection = message.value.decode('utf-8')
		if load_balancer_selection != port:
			continue

		# read-only API requests
		if message.key == APIType.ACC_INFO.value:
			# print(f'acc info: {message}') # type = ConsumerRecord
			account_id = message.headers[0][1].decode('utf-8')
			obj = db.accounts.find_one({"_id": ObjectId(account_id)}) # access db
			print(obj)
		elif message.key == APIType.TRAN_HISTORY.value:
			account_id = message.headers[0][1].decode('utf-8')
			obj = db.transactions.find_one({"account_id": ObjectId(account_id)})
			print(obj)

		# transaction related API requests
		elif message.key == APIType.NEW_ACC.value:
			# convert message.headers ('data') into json
			header_json = json.loads(message.headers[0][1].decode('utf-8'))

			# get account holder email
			user_email = header_json['account_holder']['email']
			user = db.accountHolders.find_one({'email': user_email})

			account_holder = header_json['account_holder']
			account_holder["_id"] = ObjectId()
			# header_json['account_holder'] = account_holder # update header
			# print(header_json)

			# create account holder if not exist
			if user is None:
				print('user does not exist, creating account holder')
				db.accountHolders.insert_one(account_holder)
			# else:
			# 	print('user exists, continue')

			# create account
			db.accounts.insert_one(
				{
					'_id': ObjectId(),
					'holder': account_holder["_id"],
					'currency': header_json['currency'],
					'balance': 0
				}
			)

		elif message.key == APIType.ADD_FUND.value or message.key == APIType.WITHDRAW_FUND.value:
			str_data = message.headers[0][1].decode('utf-8')
			obj = json.loads(str_data)
			account_id = ObjectId(obj['account_id'])
			# print(f'data_json, type: {type(json.loads(str_data))}, {json.loads(str_data)}')  # json

			# check if account exist in the accounts db
			account = db.accounts.find_one({'_id': account_id})
			if account is None:
				print('account does not exist!!')
			else:
				# setup transaction record according to API type
				if message.key == APIType.ADD_FUND.value:
					# construct transaction record
					txn = {
						'transaction_id': ObjectId(),
						'type': 'deposit',
						'amount': float(obj['amount']),
						'timestamp': datetime.utcnow()
					}

					# add funds to account
					db.accounts.update_one(
						{'_id': account_id},
						{'$inc': {'balance': float(obj['amount'])}}
					)
				elif message.key == APIType.WITHDRAW_FUND.value:
					# construct transaction record
					txn = {
						'transaction_id': ObjectId(),
						'type': 'withdrawal',
						'amount': float(obj['amount']),
						'timestamp': datetime.utcnow()
					}

					# withdrawal
					db.accounts.update_one(
						{'_id': account_id},
						{'$inc': {'balance': -float(obj['amount'])}}
					)

				# update transaction record to transactions history of the account
				txn_query = {'account_id': account_id}
				transaction_history = db.transactions.find_one(txn_query)
				if transaction_history is None:
					# create new txn record, new account with no txn record
					print('txn history does not exist, create new object')

					txn_record = {
						'_id': ObjectId(),
						'holder': account_id,
						'currency': obj['currency'],
						'transactions': [
							txn
						]
					}

					db.transactions.insert_one(
						txn_record
					)
				else:
					# add to transactions array
					db.transactions.update_one(
						{'account_id': account_id},
						{'$push': {'transactions': txn}}
					)

		if message.key == APIType.ERROR.value:
			print('errors occur!!')
			str_data = message.headers[1][1].decode('utf-8')
			print(message.headers[1][1].decode('utf-8'))

			# obj = json.loads(str_data)
			print(f'Send this error to client: {str_data}')