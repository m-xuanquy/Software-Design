from together import Together
import base64
from PIL import Image
from io import BytesIO
import os
from config import TOGETHER_KEY

def generate_image(prompt, output_file="image.png", width=1024, height=768):
    """Generate image from text prompt using Together AI"""
    client = Together(api_key=TOGETHER_KEY)
    
    response = client.images.generate(
        prompt=prompt,
        model="black-forest-labs/FLUX.1-schnell-Free",
        width=width,
        height=height,
        steps=4,
        n=1,
        response_format="b64_json",
    )
    
    # Decode and save image
    image_data = base64.b64decode(response.data[0].b64_json)
    image = Image.open(BytesIO(image_data))
    image.save(output_file)
    
    return output_file