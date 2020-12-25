import os

from huey import SqliteHuey, crontab
from tronapi import Tron
from dotenv import load_dotenv
import pymongo

load_dotenv()

db = pymongo.MongoClient(os.getenv('DB_URL'))[os.getenv('DB_NAME')]
huey = SqliteHuey()

@huey.task(priority=1, name='event listner')
def event_listner(owner_address,to_address):
    tron = Tron()
    last_confirmed = tron.trx.get_confirmed_current_block().get('transactions')
    for i in last_confirmed:
        values = i.get('raw_data').get('contract')[0].get('parameter').get('value')
        if values.get('owner_address')==owner_address and values.get('to_address')==to_address:
            return 'found'
            break
    return 'not found'

@huey.task()
def add(a, b):
    print('running')
    return a + b

@huey.periodic_task(crontab(minute='*/1'))
def every_three_minutes():
    db.test.insert_one({'result':'This task runs every three minutes'})

every_three_minutes()