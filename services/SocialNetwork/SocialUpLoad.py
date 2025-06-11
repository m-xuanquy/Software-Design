from fastapi import HTTPException, status
from models import User
from schemas import VideoUpLoadRequest,SocialPlatform
from services.SocialNetwork import upload_video_to_youtube,get_youtube_video_stats
async def upload_video(user:User,upload_request:VideoUpLoadRequest):
    if upload_request.platform == SocialPlatform.GOOGLE:
        if not user.social_credentials or 'google' not in user.social_credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google credentials are not available for the user."
            )
        return await upload_video_to_youtube(user, upload_request)

async def get_video_stats(user:User,video_id:str,platform:SocialPlatform):
    if platform==SocialPlatform.GOOGLE:
        return await get_youtube_video_stats(user, video_id)
    
        