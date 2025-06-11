from fastapi import APIRouter, HTTPException, Depends, Query, File, UploadFile, Form
from typing import Optional
from schemas import MediaCreate, MediaUpdate, MediaResponse, MediaListResponse, MediaDelete
from services import get_media_by_id, get_media_by_user, update_media, delete_media, upload_media
from api.deps import get_current_user
from models.media import MediaType
import os
from uuid import uuid4
from config import TEMP_DIR

router = APIRouter(prefix="/media", tags=["Media"])

@router.post("/upload", response_model=MediaResponse)
async def upload_media_endpoint(
    file: UploadFile = File(...),
    prompt: str = Form(...),
    media_type: MediaType = Form(...),
    current_user = Depends(get_current_user)
):
    """Upload media file to Cloudinary and save metadata to MongoDB"""
    # Save uploaded file temporarily
    temp_file = os.path.join(TEMP_DIR, f"{uuid4()}_{file.filename}")
    
    try:
        with open(temp_file, "wb") as f:
            f.write(await file.read())
        
        # Determine folder and resource type based on media type
        folder_map = {
            MediaType.IMAGE: ("images", "image"),
            MediaType.AUDIO: ("audio", "auto"),
            MediaType.VIDEO: ("videos", "video"),
            MediaType.TEXT: ("text", "raw")
        }
        
        folder, resource_type = folder_map.get(media_type, ("media", "auto"))
        
        # Upload to Cloudinary and save to MongoDB
        result = await upload_media(
            file_path=temp_file,
            user_id=str(current_user.id),
            folder=folder,
            resource_type=resource_type,
            prompt=prompt,
            metadata={"original_filename": file.filename}
        )
        
        # Get the saved media from database
        media = await get_media_by_id(result["id"])
        return MediaResponse(**media)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

@router.post("/create", response_model=MediaResponse)
async def create_media_endpoint(
    media_create: MediaCreate,
    current_user = Depends(get_current_user)
):
    """Create media metadata record (for text-only media or external URLs)"""
    try:
        # For text media, we don't need to upload a file
        if media_create.media_type == MediaType.TEXT:
            # Create a text file with the prompt content
            temp_file = os.path.join(TEMP_DIR, f"{uuid4()}.txt")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(media_create.content)
            
            result = await upload_media(
                file_path=temp_file,
                user_id=str(current_user.id),
                folder="text",
                resource_type="raw",
                prompt=media_create.content,
                metadata=media_create.metadata
            )
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            # Get the saved media from database
            media = await get_media_by_id(result["id"])
            return MediaResponse(**media)
        else:
            raise HTTPException(
                status_code=400, 
                detail="For non-text media, please use the /upload endpoint with a file"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create media error: {str(e)}")

@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: str,
    current_user = Depends(get_current_user)
):
    """Get media by ID"""
    media = await get_media_by_id(media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check if user owns the media
    if media["user_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this media")
    
    return MediaResponse(**media)

@router.get("/", response_model=MediaListResponse)
async def get_user_media(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    media_type: Optional[MediaType] = Query(None, description="Filter by media type"),
    current_user = Depends(get_current_user)
):
    """Get current user's media with pagination and optional filtering"""
    result = await get_media_by_user(str(current_user.id), page, size, media_type)
    
    media_responses = [MediaResponse(**media) for media in result["media"]]
    
    return MediaListResponse(
        media=media_responses,
        total=result["total"],
        page=result["page"],
        size=result["size"]
    )

@router.put("/{media_id}", response_model=MediaResponse)
async def update_media_endpoint(
    media_id: str,
    media_update: MediaUpdate,
    current_user = Depends(get_current_user)
):
    """Update media metadata"""
    # Filter out None values
    update_data = {k: v for k, v in media_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")
    
    updated_media = await update_media(media_id, str(current_user.id), update_data)
    if not updated_media:
        raise HTTPException(status_code=404, detail="Media not found or not authorized")
    
    return MediaResponse(**updated_media)

@router.delete("/{media_id}", response_model=MediaDelete)
async def delete_media_endpoint(
    media_id: str,
    current_user = Depends(get_current_user)
):
    """Delete media"""
    success = await delete_media(media_id, str(current_user.id))
    
    if not success:
        raise HTTPException(status_code=404, detail="Media not found or not authorized")
    
    return MediaDelete(
        success=True,
        message="Media deleted successfully"
    )