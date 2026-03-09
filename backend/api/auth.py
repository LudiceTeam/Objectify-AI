from jose import JWTError,jwt
from datetime import timedelta,datetime
import os
from dotenv import load_dotenv


load_dotenv()


secret_key = os.getenv("SECRET_KEY")
refresh_token_key = os.getenv("REFRESH_SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
access_token_exp_min = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
resfresh_token_exp_days = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

def create_access_token(data: dict):
    """Генерирует короткоживущий access token."""
    to_encode = data.copy()
    expire = datetime.now(datetime.timezone.utc) + timedelta(minutes=access_token_exp_min)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Генерирует долгоживущий refresh token."""
    to_encode = data.copy()
    expire = datetime.now(datetime.timezone.utc) + timedelta(days=resfresh_token_exp_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, refresh_token_key, algorithm=algorithm)
    return encoded_jwt