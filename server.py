#python -m fastapi dev .\main.py
#python -m uvicorn main:api --reload
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes.media import router as media_router
import uvicorn
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
api = FastAPI(
    title="Media Processing API",
    description="API for processing media files with AI",
    version="1.0.0"
)

# Add CORS middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
api.include_router(media_router)

# Request logging middleware
@api.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

@api.get("/")
def index():
    return {
        "app": "Media Processing API",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run("server:api", host="0.0.0.0", port=8000, reload=True)