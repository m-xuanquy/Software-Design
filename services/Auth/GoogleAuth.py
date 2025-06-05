from fastapi import HTTPException,status
from google.auth.transport import requests
from config import user_collection
from models import User
from services import get_user_by_email,get_user_by_username
from config import app_config
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from typing import Dict,Any
import string
import random
from core import hash_password
GOOGLE_CLIENT_ID = app_config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = app_config.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = app_config.GOOGLE_REDIRECT_URI
# def get_google_auth_url():
#     flow = Flow.from_client_config(
#         {
#             "web":{
#                 "client_id":GOOGLE_CLIENT_ID,
#                 "client_secret":GOOGLE_CLIENT_SECRET,
#                 "auth_uri":"https://accounts.google.com/o/oauth2/auth",
#                 "token_uri":"https://oauth2.googleapis.com/token",
#                 "redirect_uris":[GOOGLE_REDIRECT_URI],
#             }
#         },
#         scopes=["openid", "email", "profile"]
#     )
#     flow.redirect_uri = GOOGLE_REDIRECT_URI
#     authorization_url,state =flow.authorization_url(
#         access_type="offline",
#         include_granted_scopes="true"
#     )
#     return authorization_url, state
# async def handle_google_callback(code:str)->User:
#     try:
#         flow = Flow.from_client_config(
#         {
#             "web":{
#                 "client_id":GOOGLE_CLIENT_ID,
#                 "client_secret":GOOGLE_CLIENT_SECRET,
#                 "auth_uri":"https://accounts.google.com/o/oauth2/auth",
#                 "token_uri":"https://oauth2.googleapis.com/token",
#                 "redirect_uris":[GOOGLE_REDIRECT_URI],
#             }
#         },
#         scopes=["openid", "email", "profile"])
#         flow.redirect_uri = GOOGLE_REDIRECT_URI
#         flow.fetch_token(code=code)
#         credentials = flow.credentials
#         idinfo = id_token.verify_oauth2_token(
#             credentials.id_token,
#             requests.Request(),
#             GOOGLE_CLIENT_ID
#         )
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid Google token: {}".format(str(e))
#         )
collection = user_collection()
async def verify_google_token(token:str)->Dict[str,Any]:
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        if idinfo["iss"] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError("Wrong issuer.")
        return idinfo
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google token: {}".format(str(e))
        )
async def process_google_user(idinfo:Dict[str,Any])->User:
    email = idinfo.get("email")
    name = idinfo.get("name")
    picture = idinfo.get("picture")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is not provided by Google"
        )
    existing_user = await get_user_by_email(email)
    if existing_user:
        return existing_user
    else:
        username = await generate_username(email,name)
        new_user = {
            "username":username,
            "email":email,
            "fullName":name,
            "avatar":picture,
            "password":hash_password(generate_password()),
        }
        result = await collection.insert_one(new_user)
        created_user = await collection.find_one({"_id": result.inserted_id})
        if created_user:
            return User(**created_user)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server error while creating user"
            )
def generate_password()->str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(alphabet) for i in range(16))

async def generate_username(email:str,name:str = None)->str:
    if name:
        base_username = name.lower().replace(" ", "_")
    else:
        base_username = email.split("@")[0].lower()
    base_username = "".join(c for c in base_username if c.isalnum or c == "_")
    if len(base_username) < 3:
        base_username = f"user_{base_username}"
    count =1
    username = base_username
    while True:
        existing=await get_user_by_username(base_username)
        if not existing:
            break
        username = f"{base_username}_{count}"
        count += 1
    return username