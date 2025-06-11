def generate_image(model, prompt, output_file="image.png", width=1024, height=768):
    if model == "flux":
        import base64
        from PIL import Image
        from io import BytesIO
        from together import Together
        from config import TOGETHER_KEY

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
    elif model == "gemini":
        """Generate image from text prompt using Google Gemini"""
        from PIL import Image
        from io import BytesIO
        from google import genai
        from google.genai import types
        from PIL import Image
        from io import BytesIO
        import base64
        from config import GEMINI_KEY

        client = genai.Client(api_key=GEMINI_KEY)

        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
            )
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image = Image.open(BytesIO((part.inline_data.data)))
                # Save the image to the current path with the name "image.png"
                image.save(output_file)
                
                return output_file