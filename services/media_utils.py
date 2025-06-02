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

# def add_subtitles(video_path, subtitle_path, output_path):
#     """Add subtitles to a video using FFmpeg"""
#     if not output_path:
#         output_path = os.path.join(TEMP_DIR, f"sub_{os.path.basename(video_path)}")
    
#     try:
#         command = [
#             "ffmpeg",
#             "-i", video_path,  # Input video
#             "-vf", "subtitles=" + subtitle_path,  # Add subtitles filter
#             "-c:a", "copy",  # Copy audio without re-encoding
#             "-y",  # Overwrite output file if it exists
#             output_path  # Output video
#         ]

#         subprocess.run(command, check=True)
#         return output_path
#     except Exception as e:
#         print(f"Error adding subtitles: {e}")
#         return None

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