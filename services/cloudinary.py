import cloudinary
import cloudinary.uploader
import os
from datetime import datetime
from typing import Optional, Dict
from config import media_collection
from db.models.media import MediaModel, MediaType

def upload_media(file_path: str, folder: str = "media", resource_type: str = "auto", 
                 title: str = None, description: str = None, metadata: Dict = None) -> Dict:
    """
    Upload media to Cloudinary and save metadata to MongoDB
    
    Args:
        file_path: Path to local file
        folder: Cloudinary folder
        resource_type: auto, image, video, raw
        title: Media title
        description: Media description
        metadata: Additional metadata
        
    Returns:
        Dictionary with upload result and database ID
    """
    # Get filename for the title if not provided
    if not title:
        title = os.path.basename(file_path)
    
    # Upload to Cloudinary
    upload_result = cloudinary.uploader.upload(
        file_path,
        folder=folder,
        resource_type=resource_type,
        unique_filename=True
    )
    
    # Determine media type
    media_type = MediaType.TEXT
    if resource_type == "image" or (resource_type == "auto" and upload_result.get("resource_type") == "image"):
        media_type = MediaType.IMAGE
    elif resource_type == "video" or (resource_type == "auto" and upload_result.get("resource_type") == "video"):
        media_type = MediaType.VIDEO
    elif upload_result.get("format") in ["mp3", "wav", "ogg"]:
        media_type = MediaType.AUDIO
    
    # Create media document
    media_doc = MediaModel(
        title=title,
        description=description,
        media_type=media_type,
        url=upload_result["secure_url"],
        public_id=upload_result["public_id"],
        metadata=metadata or {},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into MongoDB
    result = media_collection.insert_one(media_doc.dict(by_alias=True))
    
    return {
        "id": str(result.inserted_id),
        "public_id": upload_result["public_id"],
        "url": upload_result["secure_url"],
        "media_type": media_type
    }

def delete_media(public_id: str):
    """Delete media from Cloudinary and MongoDB"""
    # Delete from Cloudinary
    result = cloudinary.uploader.destroy(public_id)
    
    # Delete from MongoDB
    media_collection.delete_one({"public_id": public_id})
    
    return result