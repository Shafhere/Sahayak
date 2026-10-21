"""OCR using Groq Llama 3.2 Vision."""
import os
import base64
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_image(image_bytes: bytes) -> str:
    """Use Groq Vision to read an image and extract text."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY not found."
        
    client = Groq(api_key=api_key)
    
    # Convert image to base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    try:
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all text from this document. If it is an income certificate, find the name and annual income. If it is an ID, find the name and age. Return plain text."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OCR Error: {e}"

if __name__ == "__main__":
    print("OCR tool ready.")