from pyteal import *

from akita_inu_asa_utils import opt_in_app_signed_txn, wait_for_txn_confirmation

from algosdk.future import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod

# user declared account mnemonics
creator_mnemonic = "obey aware hedgehog clarify shield ten catch another trash pact start seat bargain stereo bomb doll cage raise canoe water radio doctor crawl above ensure"
user_mnemonic = "provide afraid kite cotton famous glow subway pigeon mechanic pluck frequent base saddle rely unusual strategy pelican oven father planet want dune nominee able seminar"

# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


def wait_for_confirmation(client, txid):
    last_round = client.status().get("last-round")
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print(
        "Transaction {} confirmed in round {}.".format(
            txid, txinfo.get("confirmed-round")
        )
    )
    return txinfo

def cast_vote(client, private_key, index, vote):

    app_args = [b'vote', vote.encode()]

    sender = account.address_from_private_key(private_key)

    params = client.suggested_params()

    params.flat_fee = True
    params.fee = 1000

    # Signed, sealed, delivered, I'm yours!
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args)
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    client.send_transactions([signed_txn])
    wait_for_confirmation(client, tx_id)

if __name__ == '__main__':

    creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)
    user_private_key = get_private_key_from_mnemonic(creator_mnemonic)
    user_public_address = mnemonic.to_public_key(creator_mnemonic)

    voting_app_id = 57278074

    client = algod.AlgodClient(algod_token, algod_address)
    #
    # signed_txn, txn_id = opt_in_app_signed_txn(user_private_key,
    #                       user_public_address,
    #                       client.suggested_params(),
    #                       voting_app_id,
    #                       foreign_assets=None,
    #                       app_args=None)
    #
    # client.send_transactions([signed_txn])
    #
    # wait_for_txn_confirmation(client, txn_id, 5)

    cast_vote(client, user_private_key, voting_app_id, 'Yes')