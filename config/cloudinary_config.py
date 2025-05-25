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
    # Check if configuration is successful
    if all([
        cloudinary.config().cloud_name,
        cloudinary.config().api_key,
        cloudinary.config().api_secret
    ]):
        print("Successfully connected to Cloudinary.")
    else:
        print("Failed to connect to Cloudinary. Please check your environment variables.")
    return cloudinary

# Initialize Cloudinary when module is imported
cloudinary_instance = cloudinary_config()