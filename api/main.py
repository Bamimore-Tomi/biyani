from typing import Optional
from fastapi import FastAPI, Query,Depends
from fastapi.exceptions import RequestValidationError
from models import CreateWallet , CreateWalletResponse
from core import Wallet

app = FastAPI(title='Biyani')


@app.get('/')
def home():
    return 'This is the begining of Biyani'
@app.get('/trx/create',response_model=CreateWalletResponse)
def create_trx(input: CreateWallet = Depends(CreateWallet)):
    wallet = Wallet(callback=input.callback,input_wallet=input.address,
                    payment_notification_email=input.email,post=input.post)
    response = {
        'input_address':input.address,
        'output_address':wallet.address
    }
    return response
