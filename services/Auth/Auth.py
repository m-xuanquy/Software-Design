from models import UserInDB

from config import user_collection

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