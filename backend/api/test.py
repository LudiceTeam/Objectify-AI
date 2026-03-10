import requests
import os
from dotenv import load_dotenv
import json
import time
import hmac
import hashlib


load_dotenv()


async def hash_psw(psw:str) -> str:
    pass


URL = "http://0.0.0.0:8081/register"   # замени на свой адрес
SECRET_KEY = os.getenv("signature")    # это значение должно совпадать с .env -> signature

data = {
    "username": "ivan3",
    "password": "123456789"
}

# timestamp
x_timestamp = str(int(time.time()))

# JSON строка должна быть собрана точно так же, как на сервере
data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))

# HMAC-SHA256 signature
x_signature = hmac.new(
    SECRET_KEY.encode(),
    data_str.encode(),
    hashlib.sha256
).hexdigest()

headers = {
    "x-signature": x_signature,
    "x-timestamp": x_timestamp,
    "Content-Type": "application/json"
}

response = requests.post(URL, json=data, headers=headers)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)
