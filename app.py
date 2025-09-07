from flask import Flask, render_template, request, jsonify
from models.image_analysis import analyze_image_for_accessibility
from models.text_analysis import analyze_text_for_accessibility, sanitize_pii
from models.fix_suggestions import suggest_text_fixes, suggest_image_fixes
import base64
import json
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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