from fastapi import APIRouter,Depends,HTTPException,status,Form
from schemas import VideoUpLoadRequest,VideoStatsResponse,GoogleVideoStatsResponse,FacebookVideoStatsResponse
from models import User
from api.deps import get_current_user
from services.SocialNetwork import upload_video,get_video_stats
from typing import Union,Optional
router = APIRouter(prefix="/social", tags=["Social Media"])
@router.post("/upload-video",response_model=str)
async def upload_video_to_social(upload_request: VideoUpLoadRequest=Form(...), user: User = Depends(get_current_user)):
    try:
        result = await upload_video(user,upload_request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        ) 
    
@router.get("/video-stats",response_model=Union[GoogleVideoStatsResponse,FacebookVideoStatsResponse])
async def get_video_statstic(user:User =Depends(get_current_user),platform:str="",video_id:str=""):
    try:
        if not platform or not video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform and video ID are required."
            )

        return await get_video_stats(user,video_id,platform)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve video statistics: {str(e)}"
        )