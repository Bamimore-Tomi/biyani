from typing import Optional
from threading import Thread

from fastapi import FastAPI, Query,Depends
from fastapi.exceptions import RequestValidationError
from starlette.responses import StreamingResponse
from .models import CreateWallet , CreateWalletResponse
from .meta import tags_metadata

from core import Wallet
from core import EventLoop

#thread = Thread(target=EventLoop().trx_event_loop)
#thread.start()

app = FastAPI(title='Biyani',
                description='Testing version of a crypto payment platfrom to enable merchants seamlessly recieve payments.',
                openapi_tags=tags_metadata)

@app.get('/')
def home():
    return 'This is the begining of Biyani'
@app.get('/trx/create',response_model=CreateWalletResponse,tags=['Tron'])
def create_trx(input: CreateWallet = Depends(CreateWallet)):
    wallet = Wallet(callback=input.callback,input_address=input.address,
                    notification_email=input.email)
    response = {
        'input_address':input.address,
        'output_address':wallet.address,
        'qr_code':wallet.get_qr_code()
    }
    return response