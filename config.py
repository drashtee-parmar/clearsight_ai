# import os
# from dotenv import load_dotenv

# load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# FAL_KEY = os.getenv("FAL_KEY")
# config.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

genai.configure(api_key=API_KEY)

# Using gemini-pro-vision as the placeholder for the more powerful
# Gemini 2.5 Flash Image Preview (Nano Banana) model.
GEMINI_VISION_MODEL_NAME = 'gemini-2.5-flash'

def get_gemini_vision_model():
    """Returns the configured Gemini Vision model, ready for use."""
    return genai.GenerativeModel(GEMINI_VISION_MODEL_NAME)