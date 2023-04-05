# chmod +x boostrap.sh && ./boostrap.sh

# retrieve the account details, including the current balance, for the account with the specified accountId.
curl localhost:5000/accounts/642aa567d08ee9ba0d8b8b82

# retrieve the transaction history for the account with the specified accountId.
curl localhost:5000/accounts/642aa567d08ee9ba0d8b8b82/transactions



# create a new bank account
curl -X POST -H "Content-Type: application/json" -d '{
    "currency": "USDT",
    "account_holder": {
      "name": "Jane Doe",
      "email": "jane@eg.com",
      "address": {
        "line_1": "789 New St.",
        "line_2": "",
        "city": "Singapore",
        "zip_code": "000000"
      },
      "phone_number": "88889999"
    }
}' http://localhost:5000/accounts

# add funds to the account with the specified accountId.
curl -X POST -H "Content-Type: application/json" -d '{
    "amount": 0.1,
    "currency": "BTC"
}' http://localhost:5000/accounts/642aa567d08ee9ba0d8b8b82/credits

# withdraw funds from the account with the specified accountId.
curl -X POST -H "Content-Type: application/json" -d '{
    "amount": 0.1,
    "currency": "BTC"
}' http://localhost:5000/accounts/642aa567d08ee9ba0d8b8b82/debits


