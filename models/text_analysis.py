import json
import google.generativeai as genai
from config import get_gemini_vision_model

def analyze_text_for_compliance(text_content: str, alt_text: str) -> dict:
    """
    Analyzes text and alt text for compliance and accessibility issues.
    
    Args:
        text_content: The main text/HTML content to analyze.
        alt_text: The existing alt text for an image.
        
    Returns:
        A dictionary report of compliance issues and fixes.
    """
    model = get_gemini_vision_model()
    
    prompt = f"""
    You are an expert in web content accessibility and SEO.
    Analyze the following content for compliance issues (WCAG 2.2 AA).
    
    Content to analyze:
    ---
    Text: {text_content}
    Alt Text: {alt_text}
    ---
    
    Provide your analysis as a JSON object with the following structure:
    - "text_issues": An array of objects for text-based issues (e.g., readability, missing headings).
    - "alt_text_analysis": An object analyzing the sufficiency of the provided alt text.
    - "suggested_fixes": An array of natural language prompts to fix the issues.
    
    If no issues are found, return an empty object for each key.
    """
    
    try:
        response = model.generate_content(prompt)
        json_string = response.text.strip().replace('```json', '').replace('```', '')
        report = json.loads(json_string)
        return report
    except Exception as e:
        print(f"Error analyzing text with Gemini: {e}")
        return {"error": f"Failed to analyze text: {str(e)}"}