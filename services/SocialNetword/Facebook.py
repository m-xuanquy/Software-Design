from schemas import VideoUpLoadRequest
from models import User
from services import check_facebook_credentials, get_media_by_id
from fastapi import HTTPException, status
import json
import requests
async def upload_video_to_facebook(user: User,page_id:str, upload_request: VideoUpLoadRequest) -> str:
    try:
        access_token =await check_facebook_credentials(user)
        if not user.social_credentials or 'facebook' not in user.social_credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not have Facebook credentials"
            )
        page = await get_page_by_pageid(user, page_id)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )
        page_access_token = page.get('access_token')
        if not page_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page access token not found"
            )
        media = await get_media_by_id(upload_request.media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found"
            )
        media_url = media.url
        upload_url=f"https://graph.facebook.com/v23.0/{page_id}/videos"
        upload_data ={
            "title": upload_request.title,
            "description": upload_request.description,
            "file_url": media_url,
            "access_token": page_access_token,
            "privacy": "SELF"  # Default to SELF, can be changed based on requirements
        }
        # privacy_mapping = {
        #     "public": {"value": "EVERYONE"},
        #     "private": {"value": "SELF"},
        #     "friends": {"value": "ALL_FRIENDS"}
        # }
        # privacy_status = upload_request.privacy_status.lower()
        # if privacy_status in privacy_mapping:
        #     upload_data["privacy"] = json.dumps(privacy_mapping[privacy_status])

        if upload_request.tags:
            upload_data["tags"] = ",".join(upload_request.tags)
        
        response = requests.post(upload_url, data=upload_data)
        result = response.json()
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error uploading video to Facebook: {result['error']['message']}"
            )
        video_id = result.get("id")
        if not video_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Video upload failed, no video ID returned"
            )
        return f"https://www.facebook.com/{video_id}"
    except HTTPException as e:
        raise  HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video to Facebook: {e.detail}"
        )
async def get_page_by_pageid(user:User,page_id:str):
    for page in user.social_credentials.get('facebook', {}).get('pages', []):
        if page.get('id') == page_id:
            return page