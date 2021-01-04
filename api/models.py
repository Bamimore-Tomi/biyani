from typing import Optional
from pydantic import BaseModel , Field, validator, HttpUrl,EmailStr
from fastapi import Query, HTTPException
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, Field
from tronapi import Tron
from starlette.responses import StreamingResponse

@dataclass
class CreateWallet:
    callback :  HttpUrl = Query(..., description='Callback URL where payment notifications will be posted to. It **must** be a valid URL.e.g\n `http://example.com/payment/callback/?invoice=1234&nonce=randomstring` which allows a post request.')
    address : str = Query(...,description='Enter a valid **TRX wallet address** where TRX received will be sent to.')
    email : EmailStr = Query(None,description='Email address to send payment notifications to.')
    @validator('address')
    def is_valid_address(cls,address):
        tron = Tron()
        result = tron.trx.validate_address(address)
        if result.get('result')==True:
            return address
        else:
            raise HTTPException(status_code=418, detail=result.get('message'))

class CreateWalletResponse(BaseModel):
    output_address : str=Field(...,description='A valid wallet address where **clients(users)** can send assests to.')
    input_address : str = Field(..., description='A valid wallet address where assets recieved in the Output address will be sent to.')
    qr_code : bytes = Field(...,description='Convert str to bytes then decode bytes with base64 to get png header bytes to get which can be written to a .png file.')
    