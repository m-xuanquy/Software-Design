import subprocess
import os
import tempfile
from services.cloudinary import upload_media
from config import TEMP_DIR

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