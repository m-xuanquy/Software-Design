from passlib.context import CryptContext
from jose import jwt,JWSError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import app_config
ACCESS_TOKEN_EXPIRE_MINUTES = app_config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = app_config.REFRESH_TOKEN_EXPIRE_DAYS
AUTH_SECRET_KEY = app_config.AUTH_SECRET_KEY
ALGORITHM = app_config.ALGORITHM
pwd_context =CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password:str,hashed_password:str)->bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data:Dict[str,Any])->str:
    to_encode= data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire,"type": "access"})
    encoded_jwt = jwt.encode(to_encode, AUTH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data:Dict[str,Any])->str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire,"type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, AUTH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def verify_token(token,token_type:str ="access") ->Dict[str,Any]|None:
    try:
        payload = jwt.decode(token,AUTH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        exp =payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.now():
            return None
        return payload
    except JWSError:
        return None


