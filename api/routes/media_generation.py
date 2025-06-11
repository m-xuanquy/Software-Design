from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import os
from uuid import uuid4
from typing import Optional
import tempfile
# from config import OUTPUT_DIR
from config import TEMP_DIR
from services import generate_text, generate_speech, generate_image, transcribe_audio, convert_to_srt, create_video, add_subtitles, upload_media
from typing import Literal

router = APIRouter(prefix="/media", tags=["Media Generation"])

@router.post("/generate-text")
async def generate_text_endpoint(model: Literal["deepseek", "gemini"] = Form(...), prompt: str = Form(...), max_length: int = Form(100)):
    """Generate text from a prompt"""
    try:
        generated_text = generate_text(model, prompt, max_length)
        return {"text": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation error: {str(e)}")

@router.post("/tts")
async def text_to_speech(text: str = Form(...), voice: str = Form("Fritz-PlayAI")):
    """Convert text to speech"""
    output_file = os.path.join(TEMP_DIR, f"{uuid4()}.wav")
    try:
        result_file = generate_speech(text, output_file, voice)
        return FileResponse(result_file, media_type="audio/wav", filename="speech.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(output_file) and output_file.startswith(TEMP_DIR):
            os.remove(output_file)

@router.post("/generate-image")
async def generate_image_endpoint(model: Literal["flux", "gemini"] = Form(...),prompt: str = Form(...)):
    """Generate image from text prompt"""
    output_file = os.path.join(TEMP_DIR, f"{uuid4()}.png")
    try:
        result_file = generate_image(model, prompt, output_file)
        return FileResponse(result_file, media_type="image/png", filename="image.png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation error: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(output_file) and output_file.startswith(TEMP_DIR):
            os.remove(output_file)

@router.post("/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...), create_srt: bool = Form(False)):
    """Transcribe audio to text"""
    # Save uploaded file temporarily
    temp_file = os.path.join(TEMP_DIR, f"{uuid4()}.wav")
    with open(temp_file, "wb") as f:
        f.write(await file.read())
    
    try:
        if create_srt:
            srt_file = os.path.join(TEMP_DIR, f"{uuid4()}.srt")
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
    temp_image = os.path.join(TEMP_DIR, f"{uuid4()}.png")
    temp_audio = os.path.join(TEMP_DIR, f"{uuid4()}.wav")
    temp_files = [temp_image, temp_audio]
    
    try:
        # Save uploaded files
        with open(temp_image, "wb") as f:
            f.write(await image.read())
        with open(temp_audio, "wb") as f:
            f.write(await audio.read())
        
        # Create video
        output_video = os.path.join(TEMP_DIR, f"{uuid4()}.mp4")
        temp_files.append(output_video)
        result_file = create_video(temp_image, temp_audio, output_video)
        
        if result_file is None:
            raise HTTPException(status_code=500, detail="Failed to create video")
        
        if is_add_subtitles:
            # Create SRT file
            srt_file = os.path.join(TEMP_DIR, f"{uuid4()}.srt")
            temp_files.append(srt_file)
            transcription = transcribe_audio(temp_audio, srt_file)
            
            # Add subtitles
            output_with_subs = os.path.join(TEMP_DIR, f"{uuid4()}_subtitled.mp4")
            temp_files.append(output_with_subs)
            
            result_file = add_subtitles(output_video, srt_file, output_with_subs)
            if result_file is None:
                raise HTTPException(status_code=500, detail="Failed to add subtitles")

        return FileResponse(result_file, media_type="video/mp4", filename="output.mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video creation error: {str(e)}")
    finally:
        # Clean up all temp files 
        for f in temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"Error deleting temporary file {f}: {e}")