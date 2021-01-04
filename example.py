import requests
import base64

b = {
    'callback':'http://56400c5508ca.ngrok.io/client/trx-testing',
    'address':'TB4zCj53RrzHBVwZBsaaaSHQKiixuNwW7D'
}
url = "https://biyani.herokuapp.com​/trx/create"
req = requests.get(url,params=b).json()
new_wallet_address = req.get('output_address')
print(new_wallet_address)
##Get QR code string to bytes
a = req.get('qr_code').encode()
png_btyes =  base64.b64decode(a)
with open('test.png','wb') as f:
    f.write(png_btyes)