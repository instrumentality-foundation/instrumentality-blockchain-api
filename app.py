
from flask import Flask, request, redirect
from flask_cors import CORS
from account import account
import json

app = Flask(__name__)
cors = CORS(app, resources={
    r"/*":
        {
            "origins": ['http://localhost:4200', 'http://localhost:8000'],
            "supports_credentials": "true"
        }
})


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/account/create/<acc_name>/<domain_name>')
def account_create(acc_name: str, domain_name: str):
    return account.create(acc_name, domain_name)


@app.route('/account/auth', methods=['POST'])
def account_auth():
    req_body = request.get_json()

    return account.auth(req_body['username'], req_body['privateKey'])


@app.route('/account/verify', methods=['POST'])
def account_verify():
    req_body = request.get_json()

    return account.verify(req_body['username'], req_body['token'])


if __name__ == '__main__':
    app.run()
