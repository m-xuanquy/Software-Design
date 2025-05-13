import os
import cloudinary
from dotenv import load_dotenv

# Load environment variables if not already loaded
load_dotenv()

def cloudinary_config():
    """Configure and return Cloudinary instance"""
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )
    
    return cloudinary

# Initialize Cloudinary when module is imported
cloudinary_instance = cloudinary_config()