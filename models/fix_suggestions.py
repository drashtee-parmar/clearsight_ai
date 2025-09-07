import io
import base64
from PIL import Image, ImageFilter
from config import get_gemini_vision_model

def apply_fix_with_gemini(image: Image.Image, fix_prompt: str) -> str:
    """
    Simulates using the Gemini model to apply a fix to an image.
    
    Args:
        image: The original PIL Image object.
        fix_prompt: The natural language instruction to fix the image.
        
    Returns:
        A base64-encoded string of the new, fixed image.
    """
    try:
        if "blur" in fix_prompt.lower() or "redact" in fix_prompt.lower():
            fixed_image = image.filter(ImageFilter.GaussianBlur(radius=50))
        elif "contrast" in fix_prompt.lower() or "color" in fix_prompt.lower():
            fixed_image = Image.eval(image, lambda x: 255 - x)
        else:
            fixed_image = image

        fixed_img_bytes = io.BytesIO()
        fixed_image.save(fixed_img_bytes, format='PNG')
        return base64.b64encode(fixed_img_bytes.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error applying fix: {e}")
        original_img_bytes = io.BytesIO()
        image.save(original_img_bytes, format='PNG')
        return base64.b64encode(original_img_bytes.getvalue()).decode('utf-8')