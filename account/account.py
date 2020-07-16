"""
This library handles account creation and management
"""

from iroha import Iroha, IrohaCrypto, IrohaGrpc
import json

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

