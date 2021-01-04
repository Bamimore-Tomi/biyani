# [Biyani](https://biyani.herokuapp.com/docs)
A cryptocurrency payment processing  platform. You have a plaform that accepts cypto as a method of payment and you have a wallet address for the crypto assest you have chosen to accept; how to you know when a user makes payment on your platform to your wallet address ? Biyan present a viable a secure solution. 

# Testing Information
The application is divided mainly into two parts:
* core
* api

The **core** handles wallet creation and payment processing while the API exposes some functionality of the core. Currently, the application can only process payments in Tron(TRX).
Feel free to add functionality for other crypto assets in the format of trx.py.
* To test the app locally, install the requirements and run with `uvicorn api:app --reload`. You have to create your own .env file to store app secrets and other sensitive keys.

Check out the documentation @ <https://biyani.herokuapp.com/docs>
