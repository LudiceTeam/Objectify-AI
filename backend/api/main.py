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
from database.main_core import register


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


class AuthorizeData(BaseModel):
    username:str
    password:str

async def register(req:AuthorizeData,x_signature:str = Header(...),x_timestamp:str = Header(...)):
    if not verify_signature(req.model_dump(),x_signature,x_timestamp):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,detail = "Invalid signature")
    try:
        try_reg:bool = await register(req.username,req.password)
        if not try_reg:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,detail = "User already existst")
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,detail = f"Server error : {e}")
    





######## RUN ######## 

if __name__ == "__main__":
    uvicorn.run(app,host = "0.0.0.0",port = 8080)