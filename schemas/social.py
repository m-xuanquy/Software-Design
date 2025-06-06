from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict,Any,Optional, List
from datetime import datetime
class SocialPlatform(str,Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"

class SocialAuthResponse (BaseModel):
    platform:SocialPlatform
    authorized:bool
    authorization_url:Optional[str] = None
    platform_info:Optional[Dict[str, Any]] = None


class VideoUpLoadRequest (BaseModel):
    media_id:str
    platform: SocialPlatform
    title: str
    description: Optional[str] = ""
    tags: Optional[List[str]] = []
    privacy_status:str = Field(default="private")

class VideoUploadResponse(BaseModel):
    platform:SocialPlatform
    platform_video_id: str
    title: str
    description: Optional[str] = ""
    privacy_status: str
    platform_url:str
    view_count: Optional[int] = 0
    like_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    created_at: datetime
    
class VideoStatsResponse(BaseModel):
    platform: SocialPlatform
    platform_video_id: str
    view_count: Optional[int] = 0
    like_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    last_updated: datetime