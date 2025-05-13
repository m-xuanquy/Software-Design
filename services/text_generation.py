from openai import OpenAI
from config import OPENROUTER_KEY

def generate_text(prompt, max_length=None):
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
