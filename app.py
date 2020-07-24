
from flask import Flask, request, redirect
from flask_cors import CORS
from account import account
import json

app = Flask(__name__)
CORS(app)


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


@app.route('/redirect/fullapp')
def redirect_fullapp():
    return redirect("http://192.168.1.4:5000/home")


if __name__ == '__main__':
    app.run()
