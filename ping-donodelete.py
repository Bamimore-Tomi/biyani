import requests
import time

url = "https://biyani.herokuapp.com/"
while True:
    req = requests.get(url)
    print(req.status_code)
    time.sleep(1500)