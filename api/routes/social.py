from fastapi import APIRouter,Depends,HTTPException,status,Form
from schemas import VideoUpLoadRequest
from models import User
from api.deps import get_current_user
from services.SocialNetword import upload_video
router = APIRouter(prefix="/social", tags=["Social Media"])
@router.post("/upload-video",response_model=str)
async def upload_video_to_social(upload_request: VideoUpLoadRequest=Form(...), user: User = Depends(get_current_user)):
    try:
        result = await upload_video(user,upload_request=upload_request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        ) 
