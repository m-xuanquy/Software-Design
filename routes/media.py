from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import os
from uuid import uuid4
from typing import Optional
import tempfile
from config import OUTPUT_DIR
from services.text_generation import generate_text
from services.text_to_speech import generate_speech
from services.text_to_image import generate_image
from services.speech_to_text import transcribe_audio, convert_to_srt
from services.media_utils import create_video, add_subtitles
from services.cloudinary import upload_media

router = APIRouter(prefix="/media", tags=["media"])

@router.post("/generate-text")
async def generate_text_endpoint(prompt: str = Form(...), max_length: int = Form(100)):
    """Generate text from a prompt"""
    try:
        generated_text = generate_text(prompt, max_length)
        return {"text": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation error: {str(e)}")

@router.post("/tts")
async def text_to_speech(text: str = Form(...), voice: str = Form("Fritz-PlayAI")):
    """Convert text to speech"""
    output_file = os.path.join(OUTPUT_DIR, f"{uuid4()}.wav")
    try:
        result_file = generate_speech(text, output_file, voice)
        return FileResponse(result_file, media_type="audio/wav", filename="speech.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

@router.post("/generate-image")
async def generate_image_endpoint(prompt: str = Form(...)):
    """Generate image from text prompt"""
    output_file = os.path.join(OUTPUT_DIR, f"{uuid4()}.png")
    try:
        result_file = generate_image(prompt, output_file)
        upload_media(result_file, folder="images", resource_type="image", prompt=prompt)

        return FileResponse(result_file, media_type="image/png", filename="image.png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation error: {str(e)}")

@router.post("/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...), create_srt: bool = Form(False)):
    """Transcribe audio to text"""
    # Save uploaded file temporarily
    temp_file = os.path.join(OUTPUT_DIR, f"{uuid4()}.wav")
    with open(temp_file, "wb") as f:
        f.write(await file.read())
    
    try:
        if create_srt:
            srt_file = os.path.join(OUTPUT_DIR, f"{uuid4()}.srt")
            transcription = transcribe_audio(temp_file, srt_file)
            return FileResponse(srt_file, media_type="text/plain", filename="transcription.srt")
            
        else:
            transcription = transcribe_audio(temp_file)
            return {"text": transcription.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

@router.post("/create-video")
async def create_video_endpoint(
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    is_add_subtitles: bool = Form(False)
):
    """Create video from image and audio"""
    # Create temp files with specific file extensions
    temp_image = os.path.join(OUTPUT_DIR, f"{uuid4()}.png")
    temp_audio = os.path.join(OUTPUT_DIR, f"{uuid4()}.wav")
    temp_files = [temp_image, temp_audio]
    
    try:
        # Save uploaded files
        with open(temp_image, "wb") as f:
            f.write(await image.read())
        with open(temp_audio, "wb") as f:
            f.write(await audio.read())
        
        # Create video
        output_video = os.path.join(OUTPUT_DIR, f"{uuid4()}.mp4")
        temp_files.append(output_video)
        result_file = create_video(temp_image, temp_audio, output_video)
        
        if result_file is None:
            raise HTTPException(status_code=500, detail="Failed to create video")
        
        if is_add_subtitles:
            # Create SRT file
            srt_file = os.path.join(OUTPUT_DIR, f"{uuid4()}.srt")
            temp_files.append(srt_file)
            transcription = transcribe_audio(temp_audio, srt_file)
            
            # Add subtitles
            output_with_subs = os.path.join(OUTPUT_DIR, f"{uuid4()}_subtitled.mp4")
            temp_files.append(output_with_subs)
            
            result_file = add_subtitles(output_video, srt_file, output_with_subs)
            if result_file is None:
                raise HTTPException(status_code=500, detail="Failed to add subtitles")

        upload_media(result_file, folder="videos", resource_type="video", prompt=image.filename) 

        return FileResponse(result_file, media_type="video/mp4", filename="output.mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video creation error: {str(e)}")
    finally:
        # Clean up all temp files except the result file
        for f in temp_files:
            if os.path.exists(f) and f != result_file:
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"Error deleting temporary file {f}: {e}")