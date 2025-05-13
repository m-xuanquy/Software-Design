from groq import Groq
from config import GROQ_KEY
import os

def generate_speech(text, output_file="speech.wav", voice="Fritz-PlayAI"):
    """Generate speech from text using Groq API"""
    client = Groq(api_key=GROQ_KEY)
    
    model = "playai-tts"
    response_format = "wav"
    
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        response_format=response_format
    )
    
    response.write_to_file(output_file)
    return output_file