from models import PyObjectId
from pydantic import BaseModel,EmailStr,Field,field_validator,ConfigDict
from typing import Optional,Any
from bson import ObjectId
import re
from datetime import datetime
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    def __str__(self):
        return str(self)
class UserBase(BaseModel):
    username:str = Field(...,min_length=3, max_length=50)
    email:EmailStr | None = None
    fullName:str | None = None

    @field_validator('username')
    def username_alphanumeric(cls, v):
        if not re.match("^[a-zA-Z0-9_]+$", v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v
class UserCreate(UserBase):
    password:str = Field(..., min_length=6, max_length=128)
    @field_validator('password')
    def validate_password(cls,v):
        if len(v) < 6 or len(v) > 128:
            raise ValueError('Password must be at least 6 and at most 128 characters long')
        return v
class UserLogin(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    fullName: Optional[str] = None
    avatar: Optional[str] = None
class UserResponse(UserBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    id: str = Field( alias="_id")
    username: str
    email: str|None = None
    fullName: str|None = None
    avatar: str|None = None
    created_at: datetime

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=128)
    @field_validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v