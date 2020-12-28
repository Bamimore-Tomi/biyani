import os
from functools import wraps
from tronapi import Tron
from dotenv import load_dotenv
import pymongo

load_dotenv()

#db = pymongo.MongoClient(os.getenv('DB_URL'))[os.getenv('DB_NAME')]
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
        
#runner()

from multiprocessing import Process
import time
def a():
    a = time.sleep(10)
    print('I am good')
def v():
    p = Process(target=a)
    p.start()
    print('I am V')

if __name__=='__main__':
    v()