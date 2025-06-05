from fastapi import HTTPException,status
from models import User
from schemas import UserCreate,UserLogin
from config import user_collection
from core import hash_password,verify_password
collection = user_collection()
async def get_user_by_username(username: str)-> User | None:
    try:
        user = await collection.find_one({"username": username})
        if user:
            return User(**user)
        return None
    except Exception as e:
        print("Error fetching user by username")
        return None

async def get_user_by_email(email: str)-> User | None:
    try:
        user = await collection.find_one({"email": email})
        if user:
            return User(**user)
        return None
    except Exception as e:
        print("Error fetching user by email")
        return None
async def create_user(user:UserCreate) ->User:
    exitsting_user = await get_user_by_username(user.username)
    if exitsting_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    if user.email:
        exitsting_email = await get_user_by_email(user.email)
        if exitsting_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    hashed_password = hash_password(user.password)
    new_user = user.model_dump()
    new_user["password"] = hashed_password
    try:
        result = await collection.insert_one(new_user)
        created_user = await collection.find_one({"_id": result.inserted_id})
        if created_user:
            return  User(**created_user)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server error while creating user"
            )
    except Exception as e:
        print("Error creating user:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error while creating user"
        )

async def authenticate_user(user:UserLogin) ->User|None:
    try:
        userDB = await get_user_by_username(user.username)
        if not userDB:
            return None
        if not verify_password(user.password,userDB.password):
            return None
        return userDB
    except Exception as e:
      return None