import json  
import re

import google.generativeai as genai
from html_sanitizer import Sanitizer

from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
# :
text_model = genai.GenerativeModel('gemini-2.5-flash')

# WCAG 2.2 AA guidelines (simplified for example)
WCAG_GUIDELINES = {
    "readability": "Ensure text is readable and understandable (e.g., sufficient contrast, clear language).",
    "headings": "Use proper heading structure (H1, H2, etc.) for content organization.",
    "links": "Ensure link text is descriptive and not generic (e.g., 'Click here').",
    "contrast": "Text and background color contrast ratio should be at least 4.5:1 for normal text.",
    "language": "Specify the language of the page content.",
    "forms": "Form elements should have clear labels.",
    "pii": "Do not expose Personally Identifiable Information.",
}

def detect_pii(text: str) -> list:
    """Detects common PII patterns (emails, phone numbers, some national IDs, names)."""
    pii_found = []
    # Basic regex patterns for PII (needs to be more robust for production)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'

    if re.search(email_pattern, text):
        pii_found.append("Email Address")
    if re.search(phone_pattern, text):
        pii_found.append("Phone Number")

    return pii_found

def analyze_text_for_accessibility(text_content: str) -> dict:
    """
    Analyzes text content for WCAG 2.2 AA compliance, readability, and PII.
    """
    prompt = f"""
    Analyze the following text content for WCAG 2.2 AA accessibility compliance, readability, and potential PII.
    Focus on:
    1. Readability: Is the language clear, concise, and easy to understand for the target audience?
    2. Heading Structure: If applicable, suggest improvements for logical heading use.
    3. Link Text: Are links descriptive?
    4. Contrast (mention if this is a general concern, specific checks need UI context).
    5. PII: Identify any Personally Identifiable Information.

    Text Content:
    ---
    {text_content}
    ---

    Provide your findings in a structured, *natural language* format. Try to include phrases like "Readability Score: [Good/Fair/Poor]", "Readability Feedback:", "Heading Issues:", "Link Issues:", "PII Detected:", "Compliance Issues:", and "Explanation:" to help with parsing.
    """

    response = text_model.generate_content(prompt)
    # Changed strategy: Assume Gemini will return natural language, not strict JSON,
    # and directly go to our custom parser. If you later refine the prompt
    # to always output strict JSON, you can re-introduce the try/except for json.loads.
    return parse_gemini_text_response(response.text, text_content) # <--- ALWAYS USE FALLBACK FOR NOW

def parse_gemini_text_response(text: str, original_text_content: str) -> dict:
    # A placeholder for actual parsing logic.
    # You'd use regex or keyword spotting to extract information.
    # This is where the "explainable" part comes in – Gemini's natural language output.

    # Example of very basic keyword-based parsing from natural language
    readability_score = "Unknown"
    if "Readability Score: Good" in text:
        readability_score = "Good"
    elif "Readability Score: Fair" in text:
        readability_score = "Fair"
    elif "Readability Score: Poor" in text:
        readability_score = "Poor"

    readability_feedback_match = re.search(r"Readability Feedback:([\s\S]*?)(?:Heading Issues:|Link Issues:|PII Detected:|Compliance Issues:|Explanation:|$)", text)
    readability_feedback = readability_feedback_match.group(1).strip() if readability_feedback_match else ""

    heading_issues = []
    if "Heading Issues:" in text:
        heading_match = re.search(r"Heading Issues:([\s\S]*?)(?:Link Issues:|PII Detected:|Compliance Issues:|Explanation:|$)", text)
        if heading_match:
            issues = [item.strip() for item in heading_match.group(1).split('\n') if item.strip()]
            heading_issues = [issue for issue in issues if issue and not issue.startswith('Readability Feedback:') and not issue.startswith('PII Detected:')] # Filter out extraneous text

    link_issues = []
    if "Link Issues:" in text:
        link_match = re.search(r"Link Issues:([\s\S]*?)(?:PII Detected:|Compliance Issues:|Explanation:|$)", text)
        if link_match:
            issues = [item.strip() for item in link_match.group(1).split('\n') if item.strip()]
            link_issues = [issue for issue in issues if issue]

    compliance_issues = []
    if "Compliance Issues:" in text:
        compliance_match = re.search(r"Compliance Issues:([\s\S]*?)(?:Explanation:|$)", text)
        if compliance_match:
            issues = [item.strip() for item in compliance_match.group(1).split('\n') if item.strip()]
            compliance_issues = [issue for issue in issues if issue]

    explanation_match = re.search(r"Explanation:([\s\S]*)$", text)
    explanation = explanation_match.group(1).strip() if explanation_match else text

    return {
        "readability_score": readability_score,
        "readability_feedback": readability_feedback,
        "heading_issues": heading_issues,
        "link_issues": link_issues,
        "pii_detected": detect_pii(original_text_content), # Re-run PII detection for certainty
        "compliance_issues": compliance_issues,
        "explanation": explanation
    }


def sanitize_pii(text: str) -> str:
    # ... (existing sanitize_pii code) ...
    """Redacts PII from text."""
    sanitizer = Sanitizer({
        'tags': {'p', 'b', 'i', 'strong', 'em', 'a', 'br'},
        'attributes': {'a': ('href', 'title')},
        'empty': {'p', 'br'},
        'separate': {'a', 'p'},
        'keep_bad': False,
        'add_nofollow': False,
        'remove_css_properties': False,
        'allow_details': False
    })
    # Example:
    redacted_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
    redacted_text = re.sub(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE_REDACTED]', redacted_text)
    return redacted_text