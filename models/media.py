from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict
from bson import ObjectId
from enum import Enum
from .pyobjectid import PyObjectId

# Media type enum
class MediaType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"

# Media model for MongoDB
class MediaModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    prompt: str
    # description: Optional[str] = None
    media_type: MediaType
    url: str  # Cloudinary URL
    public_id: str  # Cloudinary public ID
    metadata: Optional[Dict] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }