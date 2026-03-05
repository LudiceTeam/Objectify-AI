from fastapi import Depends,HTTPException,Request,FastAPI,Header,status
from pydantic import BaseModel
import uvicorn
import json
import hmac
import hashlib
import asyncio
import os
from dotenv import load_dotenv
import time


load_dotenv()



app = FastAPI()



######## SECURITY ######## 
def verify_signature(data:dict,rec_signature,x_timestamp:str) -> bool:
    if time.time() - int(x_timestamp) > 300:
        return False
    KEY = os.getenv("signature")
    data_to_verify = data.copy()
    data_to_verify.pop("signature",None)
    data_str = json.dumps(data_to_verify,sort_keys = True,separators = (',',':'))
    expected = hmac.new(KEY.encode(),data_str.encode(),hashlib.sha256).hexdigest()
    return hmac.compare_digest(rec_signature,expected)
async def safe_get(req:Request):
    try:
        api = req.headers.get("X-API-KEY")
        if not api or not hmac.compare_digest(api,os.getenv("api")):
            raise HTTPException(status_code = 401,detail = "Invalid API key")
    except Exception as e:
        raise HTTPException(status_code = 401,detail = "Invalid api key")


######## ROUTES ######## 

@app.get("/")
async def main():
    return "OBJECTIFY-AI API"





######## RUN ######## 

if __name__ == "__main__":
    uvicorn.run(app,host = "0.0.0.0",port = 8080)