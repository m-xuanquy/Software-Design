from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict
from models.media import MediaType

# Schema for creating new media
class MediaCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500, description="Prompt or text content for the media")
    media_type: MediaType = Field(..., description="Type of media")
    metadata: Optional[Dict] = Field(default={}, description="Additional metadata")

# Schema for updating media
class MediaUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=500, description="Prompt or text content for the media")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")

# Schema for media response
class MediaResponse(BaseModel):
    id: str = Field(..., description="Media ID")
    user_id: str = Field(..., description="User ID who owns the media")
    content: str = Field(..., description="Prompt or text content for the media")
    media_type: MediaType = Field(..., description="Type of media")
    url: str = Field(..., description="Cloudinary URL")
    public_id: str = Field(..., description="Cloudinary public ID")
    metadata: Dict = Field(default={}, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# Schema for media list response
class MediaListResponse(BaseModel):
    media: list[MediaResponse]
    total: int
    page: int
    size: int

# Schema for deleting media
class MediaDelete(BaseModel):
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Deletion message")