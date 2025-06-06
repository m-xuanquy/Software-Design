from fastapi import HTTPException, status
from models import User
from schemas import VideoUpLoadRequest,SocialPlatform
from services.SocialNetword import upload_video_to_youtube
async def upload_video(user:User,upload_request:VideoUpLoadRequest):
    if upload_request.platform == SocialPlatform.GOOGLE:
        if not user.social_credentials or 'google' not in user.social_credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google credentials are not available for the user."
            )
        return await upload_video_to_youtube(user, upload_request)
        