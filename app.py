from flask import Flask, render_template, request, jsonify
from models.image_analysis import analyze_image_for_accessibility
from models.text_analysis import analyze_text_for_accessibility, sanitize_pii
from models.fix_suggestions import suggest_text_fixes, suggest_image_fixes
import base64
import json
from bs4 import BeautifulSoup
import os # For environment variables
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import fal_client # Add this import

app = Flask(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
FAL_KEY = os.environ.get("FAL_KEY")
FAL_KEY_ID = os.environ.get("FAL_KEY_ID")
FAL_KEY_SECRET = os.environ.get("FAL_KEY_SECRET")

# Adjust these based on the actual models you are using for image and text analysis
image_model = genai.GenerativeModel('gemini-pro-vision') # Or your specific image analysis model
text_model = genai.GenerativeModel('gemini-pro') # Or your specific text analysis model


@app.route('/')
def index():
    return render_template('index.html')

# --- Image Generation Route ---
@app.route('/generate_image_from_alt_text', methods=['POST'])
def generate_image_from_alt_text():
    data = request.get_json()
    alt_text_prompt = data.get('alt_text', '')

    if not alt_text_prompt:
        return jsonify({"error": "No alt text prompt provided for image generation"}), 400

    if not FAL_KEY or not FAL_KEY:
        return jsonify({"error": "Fal.ai API keys not configured on server"}), 500

    try:
        # Use fal_client to call an image generation model
        # You'll need to choose a specific model available on fal.ai
        # Example using "fast-sdxl":
        response = fal_client.submit_job(
            "fal-ai/fast-sdxl", # Or "fal-ai/stable-diffusion-xl" for higher quality
            arguments={
                "prompt": alt_text_prompt,
                "num_inference_steps": 20, # Adjust for quality/speed
                "width": 768,
                "height": 768
            },
            key_id=FAL_KEY,
            key_secret=FAL_KEY
        )

        # Get the result (this might take a few seconds, so you might need to poll for status)
        # For simplicity, we'll wait for it here. In a production app, use webhooks or client-side polling.
        result = fal_client.wait_for_job(response)
        
        # fal.ai typically returns a list of images
        if result and 'images' in result and len(result['images']) > 0:
            image_url = result['images'][0]['url']
            return jsonify({"image_url": image_url})
        else:
            return jsonify({"error": "Fal.ai did not return an image."}), 500

    except Exception as e:
        print(f"Error generating image with Fal.ai: {e}")
        return jsonify({"error": str(e)}), 500
    
    
# --- Image Analysis Route ---
@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image_data = image_file.read()

    # Create a part for the image
    image_part = {
        'mime_type': image_file.content_type,
        'data': image_data
    }

    # You'll need to define your image analysis prompt here
    # This prompt should guide Gemini to output structured JSON for easier parsing
    prompt = """
    Analyze the provided image for accessibility compliance, specifically regarding alt text.
    Return a JSON object with the following structure:
    {
      "current_alt_text_sufficiency": "Good" | "Needs Improvement" | "Critical Failure",
      "explanation": "Detailed explanation of alt text issues.",
      "suggested_alt_text": "A comprehensive and descriptive alt text.",
      "compliance_issues": [
        {"issue_type": "WCAG 2.2 AA 1.1.1 Non-text Content", "description": "Specific issue details"},
        {"issue_type": "WCAG 2.2 AA 1.4.3 Contrast", "description": "Specific contrast issue details if applicable"}
      ],
      "is_decorative": true | false,
      "pii_risk": true | false
    }
    """

    try:
        response = image_model.generate_content([prompt, image_part])
        # Assuming Gemini's response is a JSON string
        image_analysis_raw = json.loads(response.text)

        # --- Refactor Output for Professionalism ---
        formatted_output = {
            "alt_text_sufficiency": image_analysis_raw.get("current_alt_text_sufficiency", "N/A"),
            "reasoning": image_analysis_raw.get("explanation", "No specific explanation provided."),
            "suggested_alt_text": image_analysis_raw.get("suggested_alt_text", "No specific alt text suggested."),
            "issues": []
        }

        for issue in image_analysis_raw.get("compliance_issues", []):
            formatted_output["issues"].append({
                "type": issue.get("issue_type", "Unknown Issue"),
                "description": issue.get("description", "No description.")
            })

        if image_analysis_raw.get("is_decorative"):
            formatted_output["issues"].append({
                "type": "Decorative Image",
                "description": "The image is decorative and could potentially have an empty alt attribute, though a descriptive one is usually better for context."
            })
        if image_analysis_raw.get("pii_risk"):
            formatted_output["issues"].append({
                "type": "PII Risk Detected",
                "description": "The image may contain personally identifiable information (PII)."
            })

        return jsonify(formatted_output)

    except Exception as e:
        print(f"Error during image analysis: {e}")
        return jsonify({"error": str(e)}), 500

# --- Text Analysis Route ---
@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    data = request.get_json()
    html_content = data.get('html_content', '')

    if not html_content:
        return jsonify({"error": "No HTML content provided"}), 400

    prompt = f"""
    Analyze the following HTML content for accessibility and compliance issues (WCAG 2.2 AA).
    Focus on heading structure, link text, contrast, and PII.
    Return a JSON object with the following structure:
    {{
      "compliance_issues": [
        {{
          "issue_type": "Missing Heading Structure (WCAG 2.2 AA 2.4.6)",
          "explanation": "Detailed explanation.",
          "suggestion": "Actionable suggestion."
        }},
        {{
          "issue_type": "Insufficient Contrast (WCAG 2.2 AA 1.4.3)",
          "explanation": "Detailed explanation.",
          "suggestion": "Actionable suggestion."
        }},
        {{
          "issue_type": "Non-descriptive Link Text (WCAG 2.2 AA 2.4.4)",
          "explanation": "Detailed explanation.",
          "suggestion": "Actionable suggestion."
        }},
        {{
          "issue_type": "PII Risk (WCAG 2.2 AA 2.4.4, etc.)",
          "explanation": "Detailed explanation.",
          "suggestion": "Actionable suggestion."
        }}
      ]
    }}
    HTML Content:
    {html_content}
    """

    try:
        response = text_model.generate_content(prompt)
        text_analysis_raw = json.loads(response.text)

        # --- Refactor Output for Professionalism ---
        formatted_output = {
            "overall_summary": "Analysis complete. Review the issues below for recommendations.", # You might ask Gemini to generate this too
            "issues": []
        }

        for issue in text_analysis_raw.get("compliance_issues", []):
            formatted_output["issues"].append({
                "type": issue.get("issue_type", "Unknown Text Issue"),
                "explanation": issue.get("explanation", "No explanation."),
                "suggestion": issue.get("suggestion", "No suggestion.")
            })

        return jsonify(formatted_output)

    except Exception as e:
        print(f"Error during text analysis: {e}")
        return jsonify({"error": str(e)}), 500




@app.route('/analyze', methods=['POST'])
def analyze_content():
    content = request.form.get('content')
    image_file = request.files.get('image')

    results = {
        "text_analysis": None,
        "image_analysis": None,
        "text_fixes": None,
        "image_fixes": None
    }

    if content:
        # Basic parsing to extract text and image references (for real content, this is more complex)
        soup = BeautifulSoup(content, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)

        text_analysis = analyze_text_for_accessibility(text_content)
        results["text_analysis"] = text_analysis
        results["text_fixes"] = suggest_text_fixes(text_content, text_analysis)

        # Handle PII redaction as a one-click fix
        if "redact_pii" in results["text_fixes"]:
            results["text_fixes"]["redact_pii_applied"] = sanitize_pii(text_content)


    if image_file:
        image_bytes = image_file.read()
        # In a real scenario, you'd extract alt text associated with this image from 'content'
        # For MVP, let's assume no existing alt text or pass a placeholder
        existing_alt_text = request.form.get('existing_alt_text', '') # User can input this for testing

        image_analysis = analyze_image_for_accessibility(image_bytes, existing_alt_text)
        results["image_analysis"] = image_analysis
        results["image_fixes"] = suggest_image_fixes(image_bytes, existing_alt_text, image_analysis)

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)