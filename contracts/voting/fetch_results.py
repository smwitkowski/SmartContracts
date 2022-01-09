from algosdk import account
from algosdk.v2client import indexer
from akita_inu_asa_utils import *


if __name__ == '__main__':
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = get_algod_client(algod_token, algod_address)

    app_id = 57276974
    addr = '4KGP34APJG2JI6Q3AVVKMNWP4JZYMRBO3M3KK24BKJCKSLRPL3AKVCCGWI'


    # read app global state

    results = algod_client.account_info(addr)
    apps_created = results['created-apps']
    for app in apps_created:
        if app['id'] == app_id:
            print(f"global_state for app_id {app_id}: ", app['params']['global-state'])



    myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8980")

    app = myindexer.applications(57265803)

    app_global_state = app['application']['params']['global-state']

    print(json.dumps(app_global_state, indent=4))

    results = algod_client.account_info(addr)
    apps_created = results['created-apps']
    for app in apps_created :
        if app['id'] == app_id :
            print(f"global_state for app_id {app_id}: ", app['params']['global-state'])