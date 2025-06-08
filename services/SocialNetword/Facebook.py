from schemas import VideoUpLoadRequest,FacebookVideoStatsResponse
from models import User
from services import check_facebook_credentials, get_media_by_id
from fastapi import HTTPException, status
import json
from schemas import SocialPlatform
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
            "privacy": "{\"value\":\"EVERYONE\"}"
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
        
async def get_facebook_video_stats(user: User, video_id: str) -> FacebookVideoStatsResponse:
    try:
        page_id="page_id"  # Replace with actual page ID or fetch from user input
        access_token = await check_facebook_credentials(user)
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
        video_info = await get_video_basic_info(video_id, page_access_token)
        reactions = await get_video_creations(video_id, page_access_token)
        comments = await get_video_comments(video_id, page_access_token)
        shares = await get_video_shares(video_id, page_access_token)
        view_count = await get_video_view_count(video_id, page_access_token)
        return FacebookVideoStatsResponse(
            platform=SocialPlatform.FACEBOOK,
            platform_video_id=video_id,
            title=video_info.get("title", ""),
            description=video_info.get("description", ""),
            privacy_status=video_info.get("privacy_status", "UNKNOWN"),
            platform_url=video_info.get("permalink_url",f"https://www.facebook.com/{video_id}"),
            created_at=video_info.get("created_at"),
            view_count=view_count,
            reaction_count=reactions,
            share_count=shares,
            comment_count= comments
        )
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch video stats from Facebook: {e.detail}"
        )


async def get_video_basic_info(video_id: str, access_token: str) -> dict:
    try:
        url = f"https://graph.facebook.com/v23.0/{video_id}"
        params = {
            "access_token": access_token,
            "fields": "title,description,created_time,privacy,permalink_url"
        }
        response = requests.get(url, params=params)
        data = response.json()
        if "error" in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error fetching video info: {data['error']['message']}"
            )
        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "created_at": data.get("created_time"),
            "privacy_status": data.get("privacy", {}).get("value", "SELF"),
            "platform_url": data.get("permalink_url", "")
        }
    except Exception as e:
        return{}
    
async def get_video_view_count(video_id: str, access_token: str) -> int:
    try:
        url = f"https://graph.facebook.com/v23.0/{video_id}/insights"
        params = {
            "access_token": access_token,
            "metric": "post_video_views",
        }
        response = requests.get(url, params=params)
        data = response.json()
        if "data" in data and not data.get("error"):
            return data["data"][0]["values"][0]["value"]
        return 0
    except Exception as e:
        return 0

async def get_video_creations(video_id: str, access_token: str) -> dict:
    reaction_types =["LIKE", "LOVE", "WOW", "HAHA", "SAD", "ANGRY","CARE"]
    reactions ={}
    for reaction_type in reaction_types:
        try:
            reactions_url = f"https://graph.facebook.com/v23.0/{video_id}/reactions"
            params = {
                "access_token": access_token,
                "type": reaction_type,
                "limit": 0  ,
                "summary": "total_count"
            }
            response = requests.get(reactions_url, params=params)
            data = response.json()
            print(f"Reaction data for {reaction_type}: {data}")  # Debugging line
            if "summary" in data:
                reactions[reaction_type.lower()] = data["summary"].get("total_count", 0)
            else:
                reactions[reaction_type.lower()] = 0
        except Exception as e:
            reactions[reaction_type.lower()] = 0
    return reactions
async def get_video_comments(video_id: str, access_token: str) -> int:
    try:
        comments_url = f"https://graph.facebook.com/v23.0/{video_id}/comments"
        params = {
            "access_token": access_token,
            "summary": "total_count",
            "limit": 0  
        }
        response = requests.get(comments_url, params=params)
        data = response.json()
        if "summary" in data:
            return data["summary"].get("total_count", 0)
        return 0
    except Exception as e:
        return 0
    
async def get_video_shares(video_id: str, access_token: str) -> int:
    try:
        shares_url = f"https://graph.facebook.com/v23.0/{video_id}"
        params = {
            "access_token": access_token,
            "fields": "shares"
        }
        response = requests.get(shares_url, params=params)
        data = response.json()
        if "shares" in data:
            return data["shares"].get("count", 0)
        return 0
    except Exception as e:
        return 0
