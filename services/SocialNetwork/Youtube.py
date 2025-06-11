from services.Media import check_and_refresh_google_credentials
from models import User
from schemas import VideoUpLoadRequest,VideoStatsResponse
from googleapiclient.discovery import build,Resource
from googleapiclient.http import MediaFileUpload
from fastapi import HTTPException, status
async def get_youtube_service(user:User) -> Resource:
    credentials = await check_and_refresh_google_credentials(user)
    return build(
        'youtube',
        'v3',
        credentials=credentials
    )
async def upload_video_to_youtube(user:User,upload_request:VideoUpLoadRequest)->str:
    try:
        youtube_service = await get_youtube_service(user)
        body={
            'snippet': {
                'title': upload_request.title,
                'description': upload_request.description,
                'tags': upload_request.tags,
            },
            'status': {
                'privacyStatus': upload_request.privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        video_path='./media/test.mp4'  # Replace with the actual path to the video file
        media = MediaFileUpload(
            video_path,
            chunksize=1024 * 1024,  # 1 MB chunks
            resumable=True,
            mimetype='video/mp4'
        )
        insert_request = youtube_service.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        response= insert_request.execute()
        print(response)
        video_id =response['id']
        return f'https://www.youtube.com/watch?v={video_id}'
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video to YouTube: {str(e)}"
        )
async def get_youtube_video_stats(user:User,video_id:str)->VideoStatsResponse:
    try:
        youtube_service = await get_youtube_service(user)
        request =youtube_service.videos().list(
            part='statistics,snippet',
            id=video_id
        )
        response = request.execute()
        if not response['items']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        video_data = response['items'][0]
        stats = video_data['statistics']
        snippet = video_data['snippet']
        return VideoStatsResponse(
            platform='google',
            platform_video_id=video_id,
            title=snippet.get('title', ''),
            description=snippet.get('description', ''),
            privacy_status=snippet.get('privacyStatus', 'private'),
            platform_url=f'https://www.youtube.com/watch?v={video_id}',
            view_count=int(stats.get('viewCount', 0)),
            like_count=int(stats.get('likeCount', 0)),
            comment_count=int(stats.get('commentCount', 0)),
            created_at=snippet.get('publishedAt')
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get YouTube video stats: {str(e)}"
        )
        
    



















    

