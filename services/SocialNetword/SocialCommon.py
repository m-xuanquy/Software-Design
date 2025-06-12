from fastapi import HTTPException, status
from models import User
from schemas import VideoUpLoadRequest,SocialPlatform
from .Youtube import upload_video_to_youtube, get_youtube_video_stats
from .Facebook import upload_video_to_facebook, get_facebook_video_stats
async def upload_video(user:User,upload_request:VideoUpLoadRequest):
    if upload_request.platform == SocialPlatform.GOOGLE:
        if not user.social_credentials or 'google' not in user.social_credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google credentials are not available for the user."
            )
        return await upload_video_to_youtube(user, upload_request)
    elif upload_request.platform == SocialPlatform.FACEBOOK:
        if not user.social_credentials or 'facebook' not in user.social_credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Facebook credentials are not available for the user."
            )
        page_id ="" #this should be passed in the upload_request or fetched from user credentials
        return await upload_video_to_facebook(user,page_id, upload_request)

async def get_video_stats(user:User,video_id:str,platform:SocialPlatform):
    if platform==SocialPlatform.GOOGLE:
        return await get_youtube_video_stats(user, video_id)
    elif platform==SocialPlatform.FACEBOOK:
        return await get_facebook_video_stats(user, video_id)
    
        