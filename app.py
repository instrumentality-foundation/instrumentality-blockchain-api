
from flask import Flask
from flask_cors import CORS
from account import account

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/account/create/<acc_name>/<domain_name>')
def account_create(acc_name: str, domain_name: str):
    return account.create(acc_name, domain_name)


if __name__ == '__main__':
    app.run()
