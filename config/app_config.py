import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
CAMB_KEY = os.getenv("CAMB_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
TOGETHER_KEY = os.getenv("TOGETHER_KEY")
GROQ_KEY = os.getenv("GROQ_KEY")

# Media settings
OUTPUT_DIR = "media"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)