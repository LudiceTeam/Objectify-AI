from fastapi import Depends,HTTPException,Request,FastAPI,Header,status
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from pydantic import BaseModel
from config import PROJECT_ROOT
import uvicorn
import json
import hmac
import hashlib
import asyncio
import os
from dotenv import load_dotenv
import time
from backend.database.main_core import register,login,get_user_free_trial_end_date,set_sub_to_something,is_user_subbed
from slowapi import Limiter,_rate_limit_exceeded_handler
from slowapi.util import get_remote_address


load_dotenv()



app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.add_middleware(HTTPSRedirectMiddleware)



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
    

@limiter.limit("20/minute")
@app.post("/register")
async def register_api(request:Request,req:AuthorizeData,x_signature:str = Header(...),x_timestamp:str = Header(...)):
    if not verify_signature(req.model_dump(),x_signature,x_timestamp):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,detail = "Invalid signature")
    try:
        try_reg:bool = await register(req.username,req.password)
        if not try_reg:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,detail = "User already existst")
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,detail = f"Server error : {e}")
    
@limiter.limit("20/minute")
@app.post("/login")
async def login_api(request:Request,req:AuthorizeData,x_signature:str = Header(...),x_timestamp:str = Header(...)):
    if not verify_signature(req.model_dump(),x_signature,x_timestamp):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,detail = "Invalid signature")
    try:
        try_reg:bool = await login(req.username,req.password)
        if not try_reg:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,detail = "Wrong data")
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,detail = f"Server error : {e}")

class UsernameOnly(BaseModel):
    username:str

@limiter.limit("20/minute")
@app.get("/get/{username}/date",dependencies=[Depends(safe_get)])
async def get_user_date_end_api(request:Request,username:str):
    pass




######## RUN ######## 

if __name__ == "__main__":
    uvicorn.run(app,host = "0.0.0.0",port = 8080)