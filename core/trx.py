import os, base64,time,io
from typing import Optional

from tronapi import Tron
from tronapi.common.account import PrivateKey

from dotenv import load_dotenv
import pymongo
import qrcode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

load_dotenv()
client = pymongo.MongoClient(os.getenv('DB_URL'))
db = client[os.getenv('DB_NAME')]

class Base:
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
    def _validate_address(self,wallet):
        tron = Tron()
        validate = tron.trx.validate_address(wallet)
        if validate.get('result')==False:
            raise ValueError(validate.get('message'))


class Wallet(Base):
    def __init__(self,address : Optional[str]=None,**kwargs):
        self.address = address
        self.kwargs = kwargs
        if self.address==None:
            self._create_wallet()
        else:
            super()._validate_address(self.address)
            self.load_wallet()

    def _create_wallet(self):
        tron = Tron()
        self.account = tron.create_account
        self.address = self.account.address.base58
        fernet_key = super()._generate_fernet_key(os.getenv('MASTER'),os.getenv('SALT'))
        self.encrypted_private_key = super()._encrypt_private_key(self.account.private_key,fernet_key)
        self._save_wallet()

    def load_wallet(self):
        self.wallet = db.generated_trx_wallet.find_one({'wallet_address.base58':self.address})
        if self.wallet==None:
            raise ValueError('This wallet is not registered here.')
        self.encrypted_private_key = self.wallet.get('encrypted_private_key')
        self.callback = self.wallet.get('callback')
        self.input_address = self.wallet.get('input_address')
    def get_balance(self):
        tron = Tron()
        return tron.fromSun(tron.trx.get_balance(self.address))
    def get_qr_code(self):
        img = qrcode.make(self.address)
        imgByteArr = io.BytesIO()
        img.save(imgByteArr,format=img.format)
        imgByteArr = imgByteArr.getvalue()
        return base64.encodebytes(imgByteArr)
    def __str__(self):
        return self.address
    def _save_wallet(self):
        if db is None:
            raise ValueError('db object can not be None')
        data = {
        'encrypted_private_key':self.encrypted_private_key,
        'public_key':self.account.public_key,'wallet_address':self.account.address,
        'wallet_account_balance':0.0,
        'transactions':[],
        'date_generated':time.time()}
        data.update(self.kwargs)
        db.generated_trx_wallet.insert_one(data)
        return 1
    def send(self,reciever_address,amount:Optional[float]='max'):
        if amount=='max':
            amount = self.get_balance()
        transaction = Transaction(self.encrypted_private_key,reciever_address)
        send = transaction.send_trx(float(amount))
        return send
    

class Transaction(Base):
    def __init__(self,sender_private_key:str,reciever_address:str):
        ##encrypted private key######
        self.reciever_address = reciever_address
        fernet_key = super()._generate_fernet_key(os.getenv('MASTER'),os.getenv('SALT'))
        self.private_key = super()._decrypt_private_key(sender_private_key,fernet_key)
    def send_trx(self,amount:float):
        tron = Tron()
        tron.private_key = self.private_key
        tron.default_address = tron.address.from_private_key(tron.private_key)['base58']
        super()._validate_address(self.reciever_address)
        try:
            transaction = tron.trx.send(self.reciever_address, amount)
            return transaction
        except Exception as e:
            return {'result':False,'message':'Transaction Failed','verbose':e}