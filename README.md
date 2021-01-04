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

#How to use the application
- You query (get request) the <coin>/create endpoint of the application and with valid  `address`(parent wallet) and `callback` url which are required parameters. The response contains an new wallet address. 
- This new wallet address is shared with users of your platform (clients) to make payments to. 
- Once payment is made to the new wallet address by the user(client); a post request is made by our systems to your callback url (ensure you include the https protocol and a  nonce parameter in your callback url to ensure the callback data originates from our servers).
- Once the payment made to the new address is confirmed, the assets are immediately transeferred to the parent wallet and the transcation is completed.
