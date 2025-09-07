document.getElementById('analysisForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const response = await fetch('/analyze', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    document.getElementById('textAnalysis').textContent = JSON.stringify(data.text_analysis, null, 2);
    document.getElementById('textFixes').textContent = JSON.stringify(data.text_fixes, null, 2);
    document.getElementById('imageAnalysis').textContent = JSON.stringify(data.image_analysis, null, 2);
    document.getElementById('imageFixes').textContent = JSON.stringify(data.image_fixes, null, 2);

    document.getElementById('results').style.display = 'block';

    // --- One-Click Apply Demonstration ---
    let originalContent = formData.get('content');
    let appliedText = originalContent;

    if (data.text_fixes && data.text_fixes.redact_pii_applied) {
        appliedText = data.text_fixes.redact_pii_applied;
    }
    // Add logic for applying other text fixes like readability rewrites here

    let appliedImageAlt = formData.get('existing_alt_text');
    if (data.image_fixes && data.image_fixes.suggested_alt_text !== undefined) {
        appliedImageAlt = data.image_fixes.suggested_alt_text;
    }

    // This is a simplified demonstration. Real "one-click" would involve
    // dynamically updating the content's HTML/Markdown based on fixes.
    document.getElementById('appliedContent').innerHTML = `
        <h4>Applied Text (PII Redacted Example):</h4>
        <p>${appliedText}</p>
        <h4>Applied Image Alt Text (Example):</h4>
        <p>New Alt Text: ${appliedImageAlt}</p>
        <p>Original Image: <img src="${URL.createObjectURL(formData.get('image'))}" alt="${appliedImageAlt}" width="200"></p>
    `;
});