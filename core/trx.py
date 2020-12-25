import os, base64,time
from typing import Optional

from tronapi import Tron
from tronapi.common.account import PrivateKey

from dotenv import load_dotenv
import pymongo

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

load_dotenv()
client = pymongo.MongoClient(os.getenv('DB_URL'))
db = client[os.getenv('DB_NAME')]

class Wallet:
    def __init__(self,info:dict):
        self.info=info
        self._create_wallet()
    def _create_wallet(self):
        tron = Tron()
        self.account = tron.create_account
        self.address = self.account.address.base58
        fernet_key = self._generate_fernet_key(os.getenv('MASTER'),os.getenv('SALT'))
        encrypted_private_key = self._encrypt_private_key(self.account.private_key,fernet_key)
        self._save_wallet(encrypted_private_key)
    def _generate_fernet_key(self,master_key:str,salt:str):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        return key.decode("utf-8")
    def _encrypt_private_key(self,private_key:str,fernet_key:str):
        encryptor = Fernet(fernet_key)
        hash = encryptor.encrypt(private_key.encode())
        return hash.decode()
    def _decrypt_private_key(self,hash, key):
        decryptor = Fernet(key)
        private_key = decryptor.decrypt(hash.encode())
        return private_key.decode()
    def __str__(self):
        return self.address
    def _save_wallet(self,encrypted_private_key:str):
        if db is None:
            raise ValueError('db object can not be None')
        db.generated_trx_wallet.insert_one({'reciever_wallet':self.info.get('reciever_wallet'),
        'reciever_email':self.info.get('reciever_email'),
        'reciever_chat_id':self.info.get('reciever_chat_id'),
        'sender_email':self.info.get('sender_email'),
        'sender_chat_id':self.info.get('sender_chat_id'),
        'encrypted_private_key':encrypted_private_key,
        'public_key':self.account.public_key,'wallet_address':self.account.address,
        'wallet_account_balance':0.0,
        'transactions':[],
        'date_generated':time.time()})
        return 1
class Transaction:
    def __init__(self):
        pass