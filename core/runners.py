import os
import logging
from multiprocessing import Process

from tronapi import Tron
from dotenv import load_dotenv
import pymongo
import requests
from core import Wallet
load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.ERROR)
class EventLoop:
    def __init__(self):
        self.db = pymongo.MongoClient(os.getenv('DB_URL'))[os.getenv('DB_NAME')]
    def trx_event_loop(self):
        client = Tron()
        while True:
            all_wallets = [i['wallet_address']['hex'] for i in self.db.generated_trx_wallet.find({})]
            #Get the last confirmed block
            last_block = client.trx.get_confirmed_current_block()
            try:
                last_transactions = last_block.get('transactions')
                last_recorded_transaction = range(1)
                for i in last_transactions:
                    values = i.get('raw_data').get('contract')[0].get('parameter').get('value')
                    if values.get('to_address') in all_wallets:
                        block_id = last_block.get('blockID')
                        to_address = values.get('to_address')
                        if i!=last_recorded_transaction:
                            last_recorded_transaction = i
                            p = Process(target=trx_notification,args=(self.db,to_address,block_id,i))
                            p.start()
            except Exception as e:
                ####################Error Protocal#########################
                last_block_checked = last_block.get('blockID')
                self.db.trx_wallet_exception.insert_one({'type':'System Shutdown','message':f'System Shutdown at {last_block_checked}','data':str(e)})
                logging.error(e,exc_info=True)

def trx_notification(db,wallet_address:str,block_id:str,transaction:dict):
    #db.generated_trx_wallet.find_one({'transaction': {'$elemMatch': {'txID':'cf3fd86d2fb3959ba382fa5dd2ae8fd982c392b71fe362597e7829a495540d79l'}}})
    #db.generated_trx_wallet.find_one({'transactions': {'$elemMatch': {'txID':r}}})
    client = Tron()
    wallet_address = client.address.from_hex(wallet_address).decode()
    transaction['block_id']=block_id
    write_transaction = db.generated_trx_wallet.update_one({'wallet_address.base58':wallet_address}, 
                        {'$addToSet':{'transactions':transaction}})

    wallet = Wallet(wallet_address)
    send = wallet.send(wallet.input_address)
    if send.get('result'):
        data = {'status':'ok','input_address':wallet.input_address,'output_address':wallet.address,
        'amount':str(wallet.get_balance()),
        'input_transaction':transaction,'output_transaction':send}
        try:
            #db.trx_wallet_exception
            requests.post(wallet.callback,json=data)
        except Exception as e:
            db.trx_wallet_exception.insert_one({'type':f'callback exception for {wallet.callback}','data':data,'message':str(e)})
            logger.error(e,exc_info=True)
    else:
        try:
            db.trx_wallet_exception.insert_one({'type':'transaction failed','data':transaction,'message':str(send)})
        except Exception as e:
            logger.error(e,exc_info=True)


if __name__=='__main__':
    EventLoop().trx_event_loop()