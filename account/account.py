"""
This library handles account creation and management
"""

from iroha import Iroha, IrohaCrypto, IrohaGrpc
import json
from binascii import Error
import redis
from secrets import token_hex
from datetime import timedelta
from flask import make_response


# Private file with credentials
from private import constants


def create(acc_name, domain_name):
    """
    This route creates a new private key, derives the public key and then sends it
    back to the requester in a json form.

    Parameters
    ----------
    acc_name : str
        The name of the account to be created. Must be unique.
    domain_name : str
        The name of the domain where the account should be register.

    Returns
    -------
    response : json
        A response containing the created keys.
    """
    private_key = IrohaCrypto.private_key().decode('utf-8')
    public_key = IrohaCrypto.derive_public_key(private_key).decode('utf-8')
    iroha_network = IrohaGrpc(constants.iroha_network)
    iroha_client = constants.iroha_client

    # Defining the account creation transaction
    new_account_tx = iroha_client.transaction([
        iroha_client.command(
            'CreateAccount',
            account_name=acc_name,
            domain_id=domain_name,
            public_key=public_key
        )
    ])

    # Signing the transaction with the instrumentality private key
    IrohaCrypto.sign_transaction(new_account_tx, constants.private_key)

    # Sending the transaction to be validated by the peers
    iroha_network.send_tx(new_account_tx)

    encoder = json.encoder.JSONEncoder()
    response = {}

    for status in iroha_network.tx_status_stream(new_account_tx):
        if status[0] == "STATEFUL_VALIDATION_FAILED":
            response['status'] = 'error'
            # Checking which error we got
            # First error: Couldn't create account. Internal error.
            if status[2] == 1:
                response['msg'] = "Couldn't create account. Internal error."
                response['code'] = "500"
                return encoder.encode(response), 500
            # Second error: No such permissions
            elif status[2] == 2:
                response['msg'] = "The node doesn't have permission to create accounts."
                response['code'] = "403"
                return encoder.encode(response), 403
            # Third error: No such domain
            elif status[2] == 3:
                response['msg'] = "There is no such domain."
                response['code'] = "404"
                return encoder.encode(response), 404
            # Fourth error: Account already exists
            elif status[2] == 4:
                response['msg'] = "Account with this name already exists."
                response['code'] = "403"
                return encoder.encode(response), 403
        elif status[0] == "COMMITTED":
            response['status'] = "success"
            response['private_key'] = private_key
            response['public_key'] = public_key
            response['msg'] = "Transaction written in ledger."
            response['code'] = 200
            return encoder.encode(response), 200


def auth(account_name, private_key):
    """
    This method is used to authenticate an existing user on the blockchain. Since Iroha expect an account_name when
    retrieving and account we first try to retrieve it be name. If the name doesn't exist we throw a 404 response.
    If the name exists we go ahead and check the private key. Since the account name is easily guessable or obtainable,
    we must use the private key to make sure that only the account owner can authenticate.

    :param str account_name: Unique name of the account
    :param str private_key:
    :return: JSON response, status code
    """

    # Gethering tools
    iroha_net = IrohaGrpc(constants.iroha_network)
    response = {}
    encoder = json.encoder.JSONEncoder()

    # Defining the query
    new_query = constants.iroha_client.query(
        'GetSignatories',
        account_id=account_name
    )

    # Signing the query and sending it to network
    IrohaCrypto.sign_query(new_query, constants.private_key)
    iroha_response = iroha_net.send_query(new_query)
    keys = iroha_response.signatories_response.keys

    if not keys:
        response['status'] = 'error'
        response['msg'] = 'Account not found.'
        return encoder.encode(response), 404

    public_key = keys[0]

    # Verify if private key generates the same public key as the one from network
    try:
        if IrohaCrypto.derive_public_key(private_key).decode('utf-8') != public_key:
            response['status'] = 'error'
            response['msg'] = "Authentication failed. Private key did not match."
            return encoder.encode(response), 403
        else:
            response['status'] = 'success'
            response['msg'] = "Authentication successful."

            # Generate a token and save in redis alongside public key
            # The token will expire in 3 days
            r = redis.Redis(constants.redis_network, '6379', db=0)

            t = r.get(account_name)
            if not t:
                token = token_hex(32)
                r.setex(account_name, timedelta(days=1), token)
                response['token'] = token
            else:
                response['token'] = t.decode('utf-8')

            return encoder.encode(response), 200
    except Error as err:
        response['status'] = 'error'
        response['msg'] = str(err)
        return encoder.encode(response), 403


def verify(account_name, token):
    """
    This method verifies if some account can be authenticated in main application.
    A token is generated in the redis database after a successful verification of the
    private key.

    If that token is still in the database (it hasn't expired) then allow authentication.

    :param str account_name:  The unique name of the account on the chain.
    :param str token: A token string
    :return: True if account has unexpired token in redis. Otherwise False.
    """

    response = {}
    encoder = json.encoder.JSONEncoder()

    r = redis.Redis(constants.redis_network, '6379')
    t = ''
    if r.get(account_name):
        t = r.get(account_name).decode('utf-8')

    if not t:
        response['status'] = 'error'
        response['msg'] = 'Not authorized to access this route'

        return encoder.encode(response), 401
    elif token == t:
        response['status'] = 'success'
        response['msg'] = 'Authorization succeeded'

        return encoder.encode(response), 200
    else:
        response['status'] = 'error'
        response['msg'] = 'Not authorized to access this route'

        return encoder.encode(response), 401
