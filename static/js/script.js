document.addEventListener('DOMContentLoaded', () => {
    const analyzeButton = document.getElementById('analyze-button');
    const textContent = document.getElementById('text-content');
    const imageUpload = document.getElementById('image-upload');
    const existingAltText = document.getElementById('existing-alt-text');
    const textAnalysisOutput = document.getElementById('text-analysis-output');
    const imageAnalysisOutput = document.getElementById('image-analysis-output');
    const originalImage = document.getElementById('original-image');
    const imageDisplay = document.getElementById('image-display');
    const fixedImage = document.getElementById('fixed-image');
    const imageFixesOutput = document.getElementById('image-fixes-output'); // Added this line

    analyzeButton.addEventListener('click', async () => {
        const formData = new FormData();
        formData.append('text_content', textContent.value);
        formData.append('alt_text', existingAltText.value);

        if (imageUpload.files.length > 0) {
            formData.append('image', imageUpload.files[0]);
        }

        analyzeButton.textContent = 'Analyzing...';
        analyzeButton.disabled = true;

        try {
            const response = await fetch('/analyze-content', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                // Display the analysis reports
                textAnalysisOutput.textContent = JSON.stringify(result.text_report, null, 2);
                imageAnalysisOutput.textContent = JSON.stringify(result.image_report, null, 2);

                if (result.original_image_data) {
                    originalImage.src = 'data:image/png;base64,' + result.original_image_data;
                    imageDisplay.style.display = 'flex';
                }

                // Dynamically create "Fix with AI" buttons based on the analysis
                imageFixesOutput.innerHTML = ''; // Clear previous buttons
                if (result.image_report && result.image_report.length > 0) {
                    result.image_report.forEach(issue => {
                        if (issue.fix_prompt) {
                            const button = document.createElement('button');
                            button.textContent = `Fix with AI`;
                            button.classList.add('fix-btn');
                            button.setAttribute('data-prompt', issue.fix_prompt);
                            imageFixesOutput.appendChild(button);
                        }
                    });
                } else {
                    imageFixesOutput.textContent = 'No image issues found.';
                }

                // Add event listeners for the new "Fix with AI" buttons
                const fixButtons = document.querySelectorAll('.fix-btn');
                fixButtons.forEach(button => {
                    button.addEventListener('click', async function() {
                        const fixPrompt = this.getAttribute('data-prompt');
                        this.textContent = 'Applying...';
                        this.disabled = true;

                        try {
                            const fixResponse = await fetch('/apply-fix', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ fix_prompt: fixPrompt })
                            });
                            
                            const fixData = await fixResponse.json();
                            if (fixResponse.ok) {
                                fixedImage.src = 'data:image/png;base64,' + fixData.fixed_image_data;
                                this.textContent = 'Fixed!';
                                this.disabled = true;
                            } else {
                                alert(fixData.error);
                                this.textContent = 'Failed';
                            }
                        } catch (error) {
                            console.error('Fetch error:', error);
                            alert('An error occurred. Please try again.');
                            this.textContent = 'Fix with AI';
                        }
                    });
                });
            } else {
                alert('Analysis failed: ' + result.error);
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('An error occurred. Please check the console.');
        } finally {
            analyzeButton.textContent = 'Analyze Content';
            analyzeButton.disabled = false;
        }
    });
});