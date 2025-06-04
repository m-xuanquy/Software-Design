from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from services import get_user_by_username
from models import UserInDB
from schemas import TokenData
from core import verify_token
from jose import JWTError
security = HTTPBearer()

async def get_current_user(credentials:HTTPAuthorizationCredentials =Depends(security))->UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(credentials.credentials,"access")
        if payload is None:
            raise credentials_exception
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

