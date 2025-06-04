from fastapi import HTTPException,status
from models import UserInDB
from schemas import UserCreate,UserLogin
from config import user_collection
from core import hash_password,verify_password
from typing import Dict, Any
collection = user_collection()
async def get_user_by_username(username: str)-> UserInDB | None:
    try:
        user = await collection.find_one({"username": username})
        if user:
            return UserInDB(**user)
        return None
    except Exception as e:
        print("Error fetching user by username")
        return None

async def get_user_by_email(email: str)-> UserInDB | None:
    try:
        user = await collection.find_one({"email": email})
        if user:
            return UserInDB(**user)
        return None
    except Exception as e:
        print("Error fetching user by email")
        return None
async def create_user(user:UserCreate) ->UserInDB:
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
    print("Hashed Password:", hashed_password)
    user_dict ={
        "username":user.username,
        "hashed_password":hashed_password,
        "email": user.email,
        "fullName": user.fullName,
        "avatar": None,
    }
    try:
        result = await collection.insert_one(user_dict)
        created_user = await collection.find_one({"_id": result.inserted_id})
        if created_user:
            return  UserInDB(**created_user)
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

async def authenticate_user(user:UserLogin) ->Dict[str, Any]:
    try:
        userDB = await get_user_by_username(user.username)
        if not userDB:
            return {"success": False, "message": "User not found"}
        if not verify_password(user.password,userDB.hashed_password):
            return {"success": False, "message": "Invalid password"}
        return {"success": True, "user": userDB}
    except Exception as e:
        return {"success": False, "message": "An error authenticate the user"}