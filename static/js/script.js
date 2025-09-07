// Function to display image analysis results
function displayImageAnalysis(data) {
    const resultsDiv = document.getElementById('imageAnalysisResults');
    resultsDiv.style.display = 'block';

    document.getElementById('imageAltTextSufficiency').innerHTML = `<strong>Alt Text Sufficiency:</strong> ${data.alt_text_sufficiency}`;
    document.getElementById('imageReasoning').innerHTML = `<strong>Reasoning:</strong> ${data.reasoning}`;
    document.getElementById('suggestedAltTextDisplay').innerText = data.suggested_alt_text;

    const issuesList = document.getElementById('imageIssuesList');
    issuesList.innerHTML = ''; // Clear previous issues
    if (data.issues && data.issues.length > 0) {
        data.issues.forEach(issue => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${issue.type}:</strong> ${issue.description}`;
            issuesList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.innerText = "No specific compliance issues detected beyond alt text sufficiency.";
        issuesList.appendChild(li);
    }

    // Show the "Generate Image" button if alt text was suggested
    if (data.suggested_alt_text && data.suggested_alt_text !== "No specific alt text suggested.") {
        document.getElementById('generateImageFromAltTextBtn').style.display = 'inline-block';
    } else {
        document.getElementById('generateImageFromAltTextBtn').style.display = 'none';
    }
    // Clear previously generated image
    document.getElementById('generatedImageContainer').style.display = 'none';
    document.getElementById('generatedImage').src = '';
}

// Function to display text analysis results
function displayTextAnalysis(data) {
    const resultsDiv = document.getElementById('textAnalysisResults');
    resultsDiv.style.display = 'block';

    document.getElementById('textOverallSummary').innerText = data.overall_summary;

    const issuesContainer = document.getElementById('textIssuesContainer');
    issuesContainer.innerHTML = ''; // Clear previous issues

    if (data.issues && data.issues.length > 0) {
        data.issues.forEach(issue => {
            const issueDiv = document.createElement('div');
            issueDiv.classList.add('text-issue-card'); // Add a class for styling
            issueDiv.innerHTML = `
                <h4>${issue.type}</h4>
                <p><strong>Explanation:</strong> ${issue.explanation}</p>
                <p><strong>Suggestion:</strong> ${issue.suggestion}</p>
                <button class="fix-it-btn" data-suggestion="${encodeURIComponent(issue.suggestion)}">Fix It</button>
            `;
            issuesContainer.appendChild(issueDiv);
        });
    } else {
        issuesContainer.innerHTML = '<p>No specific text compliance issues detected.</p>';
    }
}

// --- Example of how your form submission might call these functions ---
// (This is a placeholder, adapt to your actual form handling)
document.getElementById('analyzeImageForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    // ... code to get image file ...
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await fetch('/analyze_image', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    if (response.ok) {
        displayImageAnalysis(result);
    } else {
        alert('Error analyzing image: ' + result.error);
    }
});

document.getElementById('generateImageFromAltTextBtn').addEventListener('click', async () => {
    const suggestedAltText = document.getElementById('suggestedAltTextDisplay').innerText;
    if (!suggestedAltText || suggestedAltText === "No specific alt text suggested.") {
        alert("No valid alt text to generate an image from.");
        return;
    }

    // Indicate loading
    document.getElementById('generateImageFromAltTextBtn').innerText = 'Generating...';
    document.getElementById('generateImageFromAltTextBtn').disabled = true;

    try {
        const response = await fetch('/generate_image_from_alt_text', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ alt_text: suggestedAltText })
        });
        const result = await response.json();

        if (response.ok && result.image_url) {
            const generatedImageContainer = document.getElementById('generatedImageContainer');
            const generatedImage = document.getElementById('generatedImage');
            generatedImage.src = result.image_url;
            generatedImageContainer.style.display = 'block';
        } else {
            alert('Error generating image: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Network or other error during image generation:', error);
        alert('Failed to connect to image generation service.');
    } finally {
        document.getElementById('generateImageFromAltTextBtn').innerText = 'Generate Image';
        document.getElementById('generateImageFromAltTextBtn').disabled = false;
    }
});
// JavaScript (continued)

// Event delegation for "Fix It" buttons
document.getElementById('textIssuesContainer').addEventListener('click', (event) => {
    if (event.target.classList.contains('fix-it-btn')) {
        const suggestion = decodeURIComponent(event.target.dataset.suggestion);
        const currentHtmlContentInput = document.getElementById('htmlContentInput'); // Assuming your HTML input field has this ID

        if (currentHtmlContentInput) {
            // For a simple input, you might just append the suggestion or replace text
            // In a real application, you'd parse the HTML and apply the fix programmatically.
            // This is a placeholder for actual intelligent HTML manipulation.
            const userConfirms = confirm(`Apply this suggestion?\n\n"${suggestion}"\n\n(This is a simple demo. Advanced fix requires HTML parsing.)`);
            if (userConfirms) {
                // This is a very basic example. A real "Fix It" would require
                // more sophisticated HTML parsing and manipulation based on the issue type.
                // For instance, if it's "Missing Heading Structure", you'd need to identify
                // the logical headings in the content and wrap them in <h1>, <h2>, etc.
                // For a hackathon, you might just show an alert or a simple text replacement.
                alert("Fix applied! (This is a conceptual demo. Actual HTML changes require more complex parsing.)");
                // Example: If a missing H1 was detected, and the suggestion was to add one,
                // you'd need to modify the 'htmlContentInput' value.
                // currentHtmlContentInput.value = `<h1>New Heading</h1>\n${currentHtmlContentInput.value}`;
            }
        } else {
            alert("Could not find the HTML content input field to apply the fix.");
        }
    }
});


document.getElementById('analyzeTextForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    // ... code to get HTML content ...
    const htmlContent = document.getElementById('htmlInput').value; // Assuming an input field
    const response = await fetch('/analyze_text', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ html_content: htmlContent })
    });
    const result = await response.json();
    if (response.ok) {
        displayTextAnalysis(result);
    } else {
        alert('Error analyzing text: ' + result.error);
    }
});

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