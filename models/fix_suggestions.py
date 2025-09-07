import google.generativeai as genai
from config import GEMINI_API_KEY
from models.image_analysis import analyze_image_for_accessibility
from models.text_analysis import analyze_text_for_accessibility, sanitize_pii
import json 
import io # Needed for Image.open(io.BytesIO...) in suggest_image_fixes
from PIL import Image # Needed for Image.open(io.BytesIO...) in suggest_image_fixes
import re # Needed for parse_gemini_fix_response

genai.configure(api_key=GEMINI_API_KEY)
# CHANGE THIS LINE:
fix_model = genai.GenerativeModel('gemini-2.5-flash') # For generating text fixes

def suggest_text_fixes(original_text: str, analysis_results: dict) -> dict:
    """
    Generates one-click fix suggestions for text content based on analysis.
    """
    prompt = f"""
    Given the following original text and its accessibility analysis, provide concise, one-click fix suggestions.
    Focus on:
    - Rewriting sentences for better readability.
    - Correcting heading structure (if applicable, provide revised HTML snippets).
    - Making link text more descriptive.
    - Redacting PII.

    Original Text:
    ---
    {original_text}
    ---

    Analysis Results:
    ---
    {json.dumps(analysis_results, indent=2)}
    ---

    Provide a dictionary where keys are the type of fix (e.g., "rewrite_readability", "fix_headings", "fix_links", "redact_pii")
    and values are the suggested new text or HTML snippet. For PII, provide the redacted version.
    If no fix is needed for a category, omit it or provide an empty string.
    """
    response = fix_model.generate_content(prompt)
    try:
        return json.loads(response.text.strip())
    except json.JSONDecodeError:
        # Fallback parsing if Gemini doesn't always output perfect JSON
        return parse_gemini_fix_response(response.text)

def parse_gemini_fix_response(text: str) -> dict:
    # This is crucial for "one-click fixes". Gemini needs to provide a clear, actionable output.
    # You might need to refine the prompt to ensure it consistently outputs a parseable structure.
    fixes = {}
    if "suggested_alt_text" in text:
        # Example for alt text, you'd apply similar logic for other fixes
        match = re.search(r"Suggested Alt Text:\s*\"([^\"]*)\"", text)
        if match:
            fixes["suggested_alt_text"] = match.group(1)
    if "redacted_content" in text:
        match = re.search(r"Redacted Content:\s*\"([^\"]*)\"", text)
        if match:
            fixes["redact_pii"] = match.group(1)
    # ... more parsing logic
    return fixes

def suggest_image_fixes(image_bytes: bytes, existing_alt_text: str, analysis_results: dict) -> dict:
    """
    Generates one-click fix suggestions for images based on analysis.
    Primarily suggests new alt text.
    """
    prompt = f"""
    Given the following image and its accessibility analysis, provide a concise, one-click fix suggestion for the alt text.

    Existing Alt Text: "{existing_alt_text}"

    Analysis Results:
    ---
    {json.dumps(analysis_results, indent=2)}
    ---

    Provide a dictionary with a single key "suggested_alt_text" and its value being the new, improved alt text.
    If the image is decorative, the suggested alt text should be an empty string.
    """
    img = Image.open(io.BytesIO(image_bytes))
    response = fix_model.generate_content([prompt, img]) # Use multimodal for image context
    try:
        return json.loads(response.text.strip())
    except json.JSONDecodeError:
        return parse_gemini_fix_response(response.text)