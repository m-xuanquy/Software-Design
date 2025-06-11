

def generate_text(model, prompt, max_length=None):
    if (model=="deepseek"):
        from openai import OpenAI
        from config import OPENROUTER_KEY

        # Initialize the OpenAI client
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_KEY,
        )
        
        # Generate text using the OpenAI API
        completion = client.chat.completions.create(
            extra_body={},
            model="deepseek/deepseek-prover-v2:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ]    
                }
            ],
            max_tokens=max_length
        )
        return completion.choices[0].message.content
    
    elif (model=="gemini"):
        from google import genai
        from config import GEMINI_KEY
        from google.genai import types

        client = genai.Client(api_key=GEMINI_KEY)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                max_output_tokens=max_length
            )       
        )
        return response.text
