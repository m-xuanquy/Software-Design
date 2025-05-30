import cloudinary
import cloudinary.uploader
import os
from datetime import datetime
from typing import Optional, Dict
from config import media_collection
from models.media import MediaModel, MediaType

async def upload_media(file_path: str, folder: str = "media", resource_type: str = "auto", 
                 prompt: str = None, metadata: Dict = None) -> Dict:
    """
    Upload media to Cloudinary and save metadata to MongoDB
    
    Args:
        file_path: Path to local file
        folder: Cloudinary folder
        resource_type: auto, image, video, raw
        prompt: Media prompt
        description: Media description
        metadata: Additional metadata
        
    Returns:
        Dictionary with upload result and database ID
    """
    # Get filename for the title if not provided
    if not prompt:
        prompt = os.path.basename(file_path)
    
    # Upload to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(
            file_path,
            folder=folder,
            resource_type=resource_type,
            unique_filename=True
        )
        print(f"Uploaded {file_path} to Cloudinary")
    except Exception as e:
        raise Exception(f"Failed to upload media to Cloudinary: {str(e)}")

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
        prompt=prompt,
        media_type=media_type,
        url=upload_result["secure_url"],
        public_id=upload_result["public_id"],
        metadata=metadata or {},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Insert into MongoDB
    if not media_collection:
        raise Exception("Media collection is not initialized")
    try:
        media_dict = media_doc.model_dump(by_alias=True)
        result = await media_collection().insert_one(media_dict)
        print(f"Inserted media document into MongoDB with ID {result.inserted_id}")
    except Exception as e:
        raise Exception(f"Failed to insert media into MongoDB: {str(e)}")

    return {
        "id": str(result.inserted_id),
        "public_id": upload_result["public_id"],
        "url": upload_result["secure_url"],
        "media_type": media_type
    }

async def delete_media(public_id: str):
    """Delete media from Cloudinary and MongoDB"""
    # Delete from Cloudinary
    result = cloudinary.uploader.destroy(public_id)
    
    # Delete from MongoDB
    await media_collection().delete_one({"public_id": public_id})
    
    return result