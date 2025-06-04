from pydantic import BaseModel, Field,EmailStr,ConfigDict
from datetime import datetime
from bson import ObjectId
from typing import Optional,Any
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

class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    username: str =Field(...,min_length=3, max_length=50)
    hashed_password: str 
    email: EmailStr| None = None
    fullName:str|None = None
    avatar:str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    # class Config:
    #     validate_by_name = True
    #     arbitrary_types_allowed = True
    #     json_encoders = {ObjectId: str}
    

class UserInDB(User):
    pass