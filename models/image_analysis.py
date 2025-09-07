import json
from PIL import Image
from config import get_gemini_vision_model

def analyze_image_for_compliance(image: Image.Image) -> list:
    """
    Analyzes an image using the Gemini Vision model for WCAG 2.2 AA and PII issues.
    
    Args:
        image: A PIL Image object.
        
    Returns:
        A list of dictionaries representing compliance issues.
    """
    model = get_gemini_vision_model()

    prompt = """
    You are an expert in web accessibility (WCAG 2.2 AA) and privacy (PII).
    Analyze the following image for any and all compliance and accessibility issues.
    Pay close attention to text legibility (contrast), PII (faces, names, addresses), and overall content accessibility.
    
    Provide your analysis as a JSON array of objects. Each object must have the following keys:
    - "type": "accessibility" or "pii"
    - "description": A clear, concise explanation of the problem.
    - "fix_prompt": A natural language prompt for an AI to fix the issue.

    If no issues are found, return an empty JSON array [].
    """
    try:
        response = model.generate_content([prompt, image])
        json_string = response.text.strip().replace('```json', '').replace('```', '')
        report = json.loads(json_string)
        return report
    except Exception as e:
        print(f"Error analyzing image with Gemini: {e}")
        return [{"type": "error", "description": f"Failed to analyze image: {str(e)}", "fix_prompt": ""}]