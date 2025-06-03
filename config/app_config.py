import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
CAMB_KEY = os.getenv("CAMB_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
TOGETHER_KEY = os.getenv("TOGETHER_KEY")
GROQ_KEY = os.getenv("GROQ_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Media settings
OUTPUT_DIR = "media"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

#AUTH
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY")