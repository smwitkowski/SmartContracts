from algosdk import account
from akita_inu_asa_utils import *
from pyteal import compileTeal, Mode
from contracts import *
import base64
import datetime

creator_mnemonic = "provide afraid kite cotton famous glow subway pigeon mechanic pluck frequent base saddle rely unusual strategy pelican oven father planet want dune nominee able seminar"

def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key

def create_ballot(
        client,
        private_key,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
        app_args
):

    creator = account.address_from_private_key(private_key)

    on_complete = transaction.OnComplete.NoOpOC.real

    params = client.suggested_params()

    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        creator,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
        app_args,
    )

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_txn_confirmation(client, tx_id, 5)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id:", app_id)



# convert 64 bit integer i to byte string
def intToBytes(i):
    return i.to_bytes(8, "big")

def main():

    # initialize an algodClient

    #developer_config = load_developer_config()

    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = get_algod_client(algod_token, algod_address)

    # Generate account to deploy from
    # mnemonic, private_key, public_address = generate_new_account()


    private_key = get_private_key_from_mnemonic(creator_mnemonic)

    approval_program_ast = approval_program()
    approval_program_teal = compileTeal(
        approval_program_ast, mode=Mode.Application, version=5
    )
    approval_program_compiled = compile_program(algod_client, approval_program_teal)

    clear_state_program_ast = clear_state_program()
    clear_state_program_teal = compileTeal(
        clear_state_program_ast, mode=Mode.Application, version=5
    )
    clear_state_program_compiled = compile_program(
        algod_client, clear_state_program_teal
    )

    # TODO Make global_ints dynamic according to what's on the ballot
    global_ints = 6
    global_bytes = 1
    global_schema = transaction.StateSchema(global_ints, global_bytes)

    local_ints = 0
    local_bytes = 1
    local_schema = transaction.StateSchema(local_ints, local_bytes)


    # TODO change these to datetimes
    # TODO make these arguments to be loaded in a config
    status = algod_client.status()
    regBegin = status["last-round"] + 1
    regEnd = regBegin + 5
    voteBegin = regEnd + 5
    voteEnd = voteBegin + 300

    # create list of bytes for app args
    app_args = [
        intToBytes(regBegin),
        intToBytes(regEnd),
        intToBytes(voteBegin),
        intToBytes(voteEnd),
    ]

    create_ballot(
        client = algod_client,
        private_key = private_key,
        approval_program = approval_program_compiled,
        clear_program = clear_state_program_compiled,
        global_schema = global_schema,
        local_schema = local_schema,
        app_args = app_args
    )

if __name__ == "__main__":
    main()
