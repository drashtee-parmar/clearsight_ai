import io
from PIL import Image
import google.generativeai as genai
from config import GEMINI_API_KEY
import json # Make sure json is imported if you're using it for parsing

genai.configure(api_key=GEMINI_API_KEY)
# 
model = genai.GenerativeModel('gemini-2.5-flash') # Use gemini-2.5-flash for multimodal capabilities

def analyze_image_for_accessibility(image_bytes: bytes, existing_alt_text: str = "") -> dict:
    """
    Analyzes an image and its existing alt text for accessibility issues.
    Suggests new alt text if needed and identifies compliance gaps.
    """
    img = Image.open(io.BytesIO(image_bytes))

    prompt = f"""
    Analyze the provided image for accessibility.
    Consider the following:
    1. Does the image convey important information that needs to be described?
    2. Is the existing alt text sufficient, descriptive, and concise?
    3. Are there any potential compliance issues (e.g., text in image that isn't replicated, complex charts needing detailed descriptions)?
    4. Is the image purely decorative? If so, suggest an empty alt text or indicate it's decorative.
    5. Check for any PII or sensitive information visible in the image.

    Existing Alt Text: "{existing_alt_text}"

    Based on your analysis, provide:
    - `is_decorative` (boolean): True if purely decorative, False otherwise.
    - `current_alt_text_sufficiency` (string): "Good", "Needs Improvement", "Missing".
    - `suggested_alt_text` (string): A concise and descriptive alt text. If decorative, suggest "".
    - `compliance_issues` (list of strings): List of identified WCAG 2.2 AA issues related to the image.
    - `pii_risk` (boolean): True if potential PII is detected, False otherwise.
    - `explanation` (string): A brief explanation of the findings.
    """

    response = model.generate_content([prompt, img])
    # The response from Gemini will be free-form text.
    # You'll need to parse this text into a structured dictionary.
    # For MVP, a simple string output might suffice, or use regex/JSON parsing if Gemini can be prompted to output JSON.

    # Example of parsing (simplified, actual parsing would be more robust)
    try:
        # Assuming Gemini can be prompted to output JSON directly
        result = json.loads(response.text.strip())
        return result
    except json.JSONDecodeError:
        # Fallback if not JSON, parse as best as possible
        return parse_gemini_image_response(response.text)

def parse_gemini_image_response(text: str) -> dict:
    # A placeholder for actual parsing logic.
    # You'd use regex or keyword spotting to extract information.
    # This is where the "explainable" part comes in – Gemini's natural language output.
    return {
        "is_decorative": "True" in text and "decorative" in text,
        "current_alt_text_sufficiency": "Good" if "sufficient" in text or "good" in text else ("Missing" if "missing" in text else "Needs Improvement"),
        "suggested_alt_text": "A descriptive image of..." if "suggested alt text" in text else "",
        "compliance_issues": ["Missing alt text"] if "missing alt text" in text else [],
        "pii_risk": "PII detected" in text or "sensitive information" in text,
        "explanation": text
    }