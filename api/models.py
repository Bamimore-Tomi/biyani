from typing import Optional
from pydantic import BaseModel , Field, validator, HttpUrl,EmailStr
from fastapi import Query, HTTPException
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, Field
from tronapi import Tron

@dataclass
class CreateWallet:
    callback :  HttpUrl = Query(..., description='The URL the notification will be sent to. It **must** be a valid URL.')
    address : str = Query(...,description='Enter a valid **TRX address** where assests received will be sent to.')
    email : EmailStr = Query(None,description='Email address to send payment notifications to.')
    post : Optional[int] = Query(None,description='Set this to 1 if you wish to receive the callback as a POST request (default: GET)')
    @validator('address')
    def is_valid_address(cls,address):
        tron = Tron()
        result = tron.trx.validate_address(address)
        if result.get('result')==True:
            return address
        else:
            raise HTTPException(status_code=418, detail=result.get('message')+' in TRX address')
class CreateWalletResponse(BaseModel):
    output_address : str=Field(...,description='A valid TRX wallet address where that will sent to clients for payment.')
    input_address : str = Field(..., description='A valid TRX where assets recieved in the Output address will be sent to i.e the wallet address you entered when making this request.')
    