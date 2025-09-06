from dotenv import load_dotenv
load_dotenv()

from google import genai
from PIL import Image
from io import BytesIO
import os

# Configure the client with API key

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """
Return ONLY JSON. No extra text.
{
  "status": "ok",
  "message": "Your Gemini setup is working!"
}
"""



# Call the API to generate content
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)
print(response.text)