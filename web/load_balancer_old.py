from flask import Flask, jsonify, request

app = Flask(__name__)

incomes = [
    { 'description': 'salary', 'amount': 5000 }
]

# Read-only requests:
# GET /accounts/{accountId} : retrieve the account details, including the current balance, for the account with the specified accountId.
# GET /accounts/{accountId}/transactions : retrieve the transaction history for the account with the specified accountId.
# Transactional requests:
# POST /accounts : create a new bank account.
# POST /accounts/{accountId}/credits : add funds to the account with the specified accountId.
# POST /accounts/{accountId}/debits : withdraw funds from the account with the specified accountId.



@app.route("/")
def hello_world():
	return "hiiii there"

@app.route('/accounts/<account_id>')
def get_account_info(account_id):
    return "get acc info"

@app.route('/accounts/<account_id>/transactions')
def get_transaction_history(account_id):
	return "get_transaction_history"