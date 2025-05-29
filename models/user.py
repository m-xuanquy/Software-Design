from pydantic import BaseModel, Field,EmailStr
from datetime import datetime
from typing import Optional
from pyobjectid import PyObjectId
from bson import ObjectId

class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str =Field(...,min_length=3, max_length=50)
    hashed_password: str 
    email: EmailStr| None = None
    fullName:str|None = None
    avatar:str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserInDB(User):
    pass