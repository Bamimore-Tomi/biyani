import os
from functools import wraps
from multiprocessing import Process

from tronapi import Tron
from dotenv import load_dotenv
import pymongo
import requests
from core import Wallet
load_dotenv()

db = pymongo.MongoClient(os.getenv('DB_URL'))[os.getenv('DB_NAME')]
def runner():
    tron = Tron()
    while True:
        all_address = [i['wallet_address']['hex'] for i in db.generated_trx_wallet.find({})]
        last_confirmed = tron.trx.get_confirmed_current_block().get('transactions')
        for i in last_confirmed:
            values = i.get('raw_data').get('contract')[0].get('parameter').get('value')            
            if values.get('to_address') in all_address:
                print(i)
                return i
        
class EventLoop:
    def __init__(self):
        self.db = db
    def trx_event_loop(self):
        client = Tron()
        while True:
            all_wallets = [i['wallet_address']['hex'] for i in db.generated_trx_wallet.find({})]
            #Get the last confirmed block
            last_block = client.trx.get_confirmed_current_block()
            last_transactions = last_block.get('transactions')
            for i in last_transactions:
                values = i.get('raw_data').get('contract')[0].get('parameter').get('value')
                if values.get('to_address') in all_wallets:
                    block_id = last_block.get('blockID')
                    to_address = values.get('to_address')
                    p = Process(target=trx_notification,args=(to_address,block_id,i))
                    p.start()

def trx_notification(wallet_address:str,block_id:str,transaction:dict):
    #db.generated_trx_wallet.find_one({'transaction': {'$elemMatch': {'txID':'cf3fd86d2fb3959ba382fa5dd2ae8fd982c392b71fe362597e7829a495540d79l'}}})
    #db.generated_trx_wallet.update_one({'wallet_address.base58':'TEKtkGz9zD6gvj3Pyp3CUekX4bm9FAiVvG'}, {'$push':{'transactions':k}})
    #db.generated_trx_wallet.find_one({'transactions': {'$elemMatch': {'txID':r}}})
    client = Tron()
    wallet_address = client.address.from_hex(wallet_address).decode()
    transaction['block_id']=block_id
    write_transaction = db.generated_trx_wallet.update_one({'wallet_address.base58':wallet_address}, 
                        {'$addToSet':{'transactions':transaction}})

    wallet = Wallet(wallet_address)
    send = wallet.send(wallet.input_address)
    if send.get('result'):
        data = {'status':'ok','input_transaction':transaction,'output_transaction':send}
        try:
            #db.trx_wallet_exception
            requests.post(wallet.callback,json=data)
        except Exception as exception:
            db.trx_wallet_exception.insert_one({'type':'callback exception','message':exception,'data':data})
    else:
        try:
            db.trx_wallet_exception.insert_one({'type':'transaction failed','message':send,'data':transaction})
        except:
            pass


if __name__=='__main__':
    EventLoop().trx_event_loop()