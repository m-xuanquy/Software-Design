import subprocess
import os
import tempfile
from config import TEMP_DIR
import cloudinary
import cloudinary.uploader
from datetime import datetime
from typing import Optional, Dict
from config import media_collection
from models.media import MediaModel, MediaType
from bson import ObjectId

media_colt = media_collection()

async def upload_media(file_path: str, user_id: str, folder: str = "media", resource_type: str = "auto", 
                 prompt: str = None, metadata: Dict = None) -> Dict:
    """
    Upload media to Cloudinary and save metadata to MongoDB
    
    Args:
        file_path: Path to local file
        user_id: ID of the user uploading the media
        folder: Cloudinary folder
        resource_type: auto, image, video, raw
        prompt: Media prompt
        metadata: Additional metadata
        
    Returns:
        Dictionary with upload result and database ID
    """
    # Get filename for the prompt if not provided
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
        user_id=user_id,
        content=prompt,
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

async def get_media_by_id(media_id: str) -> Optional[Dict]:
    """Get media by ID"""
    try:
        from bson import ObjectId
        media = await media_collection().find_one({"_id": ObjectId(media_id)})
        if media:
            media["id"] = str(media["_id"])
            media["user_id"] = str(media["user_id"])
            del media["_id"]
        return media
    except Exception as e:
        print(f"Error getting media: {e}")
        return None

async def get_media_by_user(user_id: str, page: int = 1, size: int = 10, media_type: Optional[MediaType] = None) -> Dict:
    """Get media by user ID with pagination and optional filtering"""
    try:
        from bson import ObjectId
        skip = (page - 1) * size
        
        # Build query filter
        query_filter = {"user_id": ObjectId(user_id)}
        if media_type:
            query_filter["media_type"] = media_type.value
        
        # Get total count
        total = await media_collection().count_documents(query_filter)
        
        # Get media with pagination
        cursor = media_collection().find(query_filter).skip(skip).limit(size).sort("created_at", -1)
        media_list = []
        
        async for media in cursor:
            media["id"] = str(media["_id"])
            media["user_id"] = str(media["user_id"])
            del media["_id"]
            media_list.append(media)
            
        return {
            "media": media_list,
            "total": total,
            "page": page,
            "size": size
        }
    except Exception as e:
        print(f"Error getting user media: {e}")
        return {"media": [], "total": 0, "page": page, "size": size}

async def update_media(media_id: str, user_id: str, update_data: Dict) -> Optional[Dict]:
    """Update media metadata"""
    try:
        from bson import ObjectId
        
        # Add updated timestamp
        update_data["updated_at"] = datetime.now()
        
        result = await media_collection().update_one(
            {"_id": ObjectId(media_id), "user_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await get_media_by_id(media_id)
        return None
    except Exception as e:
        print(f"Error updating media: {e}")
        return None

async def delete_media(media_id: str, user_id: str) -> bool:
    """Delete media from Cloudinary and MongoDB"""
    try:
        from bson import ObjectId
        
        # Get media to get public_id
        media = await media_collection().find_one({"_id": ObjectId(media_id), "user_id": ObjectId(user_id)})
        if not media:
            return False
            
        # Delete from Cloudinary
        cloudinary.uploader.destroy(media["public_id"])
        
        # Delete from MongoDB
        result = await media_collection().delete_one({"_id": ObjectId(media_id), "user_id": ObjectId(user_id)})
        
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting media: {e}")
        return False

def create_video(image_path, audio_path, output_path=None):
    """Create a video from an image and audio using FFmpeg"""
    if not output_path:
        output_path = os.path.join(TEMP_DIR, f"{os.path.splitext(os.path.basename(image_path))[0]}.mp4")
    
    try:
        command = [
            "ffmpeg",
            "-loop", "1",  # Loop the image
            "-i", image_path,  # Input image
            "-i", audio_path,  # Input audio
            "-c:v", "libx264",  # Video codec
            "-tune", "stillimage",  # Optimize for still images
            "-c:a", "aac",  # Audio codec
            "-b:a", "192k",  # Audio bitrate
            "-pix_fmt", "yuv420p",  # Pixel format
            "-shortest",  # Match video duration to audio
            "-y",  # Overwrite output file if it exists
            output_path  # Output file
        ]

        subprocess.run(command, check=True)
        return output_path
    except Exception as e:
        print(f"Error creating video: {e}")
        return None

def add_subtitles(video_path, subtitle_path, output_path=None):
    """Add subtitles to a video using FFmpeg"""
    if not output_path:
        output_path = os.path.join(TEMP_DIR, f"sub_{os.path.basename(video_path)}")
    
    try:
        # Convert paths to absolute paths with forward slashes
        video_path_abs = video_path.replace('\\', '/')
        subtitle_path_abs = subtitle_path.replace('\\', '/')
        output_path_abs = output_path.replace('\\', '/')
        
        command = [
            "ffmpeg",
            "-i", video_path_abs,  # Input video
            "-vf", f"subtitles='{subtitle_path_abs}'",  # Quote the subtitle path
            "-c:a", "copy",  # Copy audio without re-encoding
            "-y",  # Overwrite output file if it exists
            output_path_abs  # Output video
        ]

        print(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)
        return output_path
    except Exception as e:
        print(f"Error adding subtitles: {e}")
        return None

def upload_video_to_cloud(video_path, title=None, description=None):
    """Create video and upload to Cloudinary"""
    # Upload to Cloudinary
    result = upload_media(
        video_path, 
        folder="videos",
        resource_type="video",
        title=title,
        description=description
    )
    
    # Clean up temporary file
    if os.path.exists(video_path) and video_path.startswith(TEMP_DIR):
        os.remove(video_path)
        
    return result

async def get_media_by_id(media_id: str) -> Optional[MediaModel]:
    try:
        media =await media_colt.find_one({"_id": ObjectId(media_id)})
        if media:
            return MediaModel(**media)
        return None
    except Exception as e:
        print(f"Error fetching media by ID {media_id}: {e}")
        return None