from groq import Groq
import os
from config import GROQ_KEY

def transcribe_audio(audio_file, output_srt=None, language="en"):
    """Transcribe audio to text using Groq API and optionally create SRT file"""
    client = Groq(api_key=GROQ_KEY)
    
    with open(audio_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="distil-whisper-large-v3-en",
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
            language=language,
            temperature=0.0
        )
    
    # If output_srt is provided, create SRT file
    if output_srt and transcription.words:
        convert_to_srt(transcription.words, output_srt)
        
    return transcription

def convert_to_srt(words, output_file):
    """Convert word-level transcription data to SRT format"""
    if not words:
        print("No words data provided")
        return
        
    # Group words into subtitle segments
    segments = []
    current_segment = []
    word_count = 0
    
    for word_data in words:
        current_segment.append(word_data)
        word_count += 1
        
        if word_count == 5:  # Group by 5 words per segment
            segments.append(current_segment)
            current_segment = []
            word_count = 0
            
    # Add any remaining words
    if current_segment:
        segments.append(current_segment)
    
    # Format time as HH:MM:SS,mmm
    def format_time(seconds):
        ms = int((seconds % 1) * 1000)
        s = int(seconds) % 60
        m = int(seconds / 60) % 60
        h = int(seconds / 3600)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    # Generate SRT content
    srt_content = ""
    for i, segment in enumerate(segments, 1):
        if not segment:
            continue
            
        start_time = segment[0]['start']
        end_time = segment[-1]['end']
        text = " ".join(item['word'] for item in segment)
        
        srt_entry = f"{i}\n{format_time(start_time)} --> {format_time(end_time)}\n{text}\n\n"
        srt_content += srt_entry
    
    # Write to file
    with open(output_file, "w") as f:
        f.write(srt_content)
    
    return output_file