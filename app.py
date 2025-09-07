import os
import io
import base64
import uuid
from flask import Flask, render_template, request, jsonify, session
from PIL import Image
from werkzeug.utils import secure_filename
from models.image_analysis import analyze_image_for_compliance
from models.fix_suggestions import apply_fix_with_gemini
from models.text_analysis import analyze_text_for_compliance

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = os.urandom(24)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze-content', methods=['POST'])
def analyze_content():
    """Handles both text and image analysis in a single request."""
    try:
        text_content = request.form.get('text_content', '')
        alt_text = request.form.get('alt_text', '')
        image_file = request.files.get('image')

        image_report = {}
        image_b64 = None

        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            image_file.save(file_path)

            session['original_image_filename'] = unique_filename
            
            img = Image.open(file_path)
            
            image_report = analyze_image_for_compliance(img)
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            image_b64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        
        # Analyze the text content
        text_report = analyze_text_for_compliance(text_content, alt_text)

        # Return all results in a single JSON response
        return jsonify({
            'text_report': text_report,
            'image_report': image_report,
            'original_image_data': image_b64
        })

    except Exception as e:
        print(f"Error during analysis: {e}")
        return jsonify({'error': 'An error occurred during analysis.'}), 500

@app.route('/apply-fix', methods=['POST'])
def apply_fix():
    """Apply a fix to the image using a Gemini prompt."""
    data = request.json
    fix_prompt = data.get('fix_prompt')
    
    if not fix_prompt:
        return jsonify({'error': 'Fix prompt is missing.'}), 400

    try:
        filename = session.get('original_image_filename')
        if not filename:
            return jsonify({'error': 'No image found in session.'}), 400
        
        original_img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        original_img = Image.open(original_img_path)

        fixed_img_b64 = apply_fix_with_gemini(original_img, fix_prompt)
        
        return jsonify({'fixed_image_data': fixed_img_b64}), 200

    except Exception as e:
        print(f"Error applying fix: {e}")
        return jsonify({'error': f'An error occurred while applying the fix: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)