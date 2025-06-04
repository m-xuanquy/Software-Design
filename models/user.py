from pydantic import BaseModel, Field,EmailStr,ConfigDict
from datetime import datetime
from bson import ObjectId
from typing import Optional
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
PyObjectId = Annotated[str,BeforeValidator(str)]
class User(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    username: str =Field(...,min_length=3, max_length=50)
    password: str 
    email: EmailStr| None = None
    fullName:str|None = None
    avatar:str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    model_config =ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId:str}
    )
