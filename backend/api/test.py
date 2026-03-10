import requests
import os
from dotenv import load_dotenv
import json
import time
import hmac
import hashlib


load_dotenv()

ref_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpdmFuNCIsImV4cCI6MTc3NzQ5NTc0MSwidHlwZSI6InJlZnJlc2gifQ.vOg7cAYKDMlwzcbC_ekRuo9V8UmN_B9QWjGyGjl0hb8","token_type"

def req1():
    URL = "http://0.0.0.0:8081/register"   # замени на свой адрес
    SECRET_KEY = os.getenv("signature")    # это значение должно совпадать с .env -> signature

    data = {
        "username": "ivan4",
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

def req2():
    acces_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpdmFuNCIsImRhdGUiOiIyMDI2LTAzLTEwIiwiZXhwIjoxNzczMTc3NTQxLCJ0eXBlIjoiYWNjZXNzIn0.S_YTMR7obXdD8NoKGo3GmLZfBccOOkJq56xwyP6opIo"
    api_key = os.getenv("api")



    url = "http://0.0.0.0:8081/identify"

    headers = {
        "Authorization": f"Bearer {acces_token}",
        "X-API-KEY":api_key,
    }

    with open("image.jpg", "rb") as f:
        files = {
            "image": ("image.jpg", f, "image/jpeg")
        }

        response = requests.post(url, headers=headers, files=files)
        print(response.status_code)
        print(response.text)


req2()