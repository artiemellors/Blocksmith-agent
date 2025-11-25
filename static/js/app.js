// Blocksmith Web Interface - Client-side JavaScript

let currentSessionId = null;
let progressInterval = null;
let currentStatus = null; // Store the full status for access in download

// DOM Elements
const formContainer = document.getElementById('form-container');
const progressContainer = document.getElementById('progress-container');
const successContainer = document.getElementById('success-container');
const configForm = document.getElementById('config-form');
const generateBtn = document.getElementById('generate-btn');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const progressMessage = document.getElementById('progress-message');
const errorMessage = document.getElementById('error-message');
const downloadBtn = document.getElementById('download-btn');
const newBlockBtn = document.getElementById('new-block-btn');
const summaryContent = document.getElementById('summary-content');

// Form submission handler
configForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Disable submit button
    generateBtn.disabled = true;
    generateBtn.textContent = 'Starting...';

    try {
        // Collect form data
        const formData = new FormData(configForm);
        const data = Object.fromEntries(formData.entries());

        // Send generation request
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Generation failed');
        }

        // Store session ID
        currentSessionId = result.session_id;

        // Hide form, show progress
        formContainer.style.display = 'none';
        progressContainer.style.display = 'block';

        // Start polling for progress
        startProgressPolling();

    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Training Block';
    }
});

// Start polling for generation progress
function startProgressPolling() {
    if (progressInterval) {
        clearInterval(progressInterval);
    }

    progressInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status/${currentSessionId}`);
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to get status');
            }

            // Update progress bar
            updateProgress(result.progress, result.message);

            // Check if complete
            if (result.status === 'complete') {
                clearInterval(progressInterval);
                currentStatus = result; // Store the full status
                showSuccess(result);
            } else if (result.status === 'error') {
                clearInterval(progressInterval);
                showError(result.error || 'Generation failed');
            }

        } catch (error) {
            console.error('Error polling status:', error);
            clearInterval(progressInterval);
            showError(error.message);
        }
    }, 1000); // Poll every second
}

// Update progress bar
function updateProgress(percent, message) {
    progressBar.style.width = `${percent}%`;
    progressText.textContent = `${percent}%`;
    progressMessage.textContent = message || 'Processing...';
}

// Show success screen
function showSuccess(result) {
    progressContainer.style.display = 'none';
    successContainer.style.display = 'block';

    // Display the block summary if available
    if (result && result.summary_content) {
        // Convert markdown to HTML (simple version - just preserve formatting)
        const formattedContent = result.summary_content
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>');

        summaryContent.innerHTML = `<pre>${formattedContent}</pre>`;
    } else {
        summaryContent.innerHTML = '<p>Summary not available.</p>';
    }
}

// Show error message
function showError(message) {
    errorMessage.textContent = `Error: ${message}`;
    errorMessage.style.display = 'block';
    progressMessage.style.display = 'none';
}

// Download button handler
downloadBtn.addEventListener('click', async () => {
    try {
        downloadBtn.disabled = true;
        downloadBtn.textContent = '📦 Downloading...';

        // Download the file
        const response = await fetch(`/api/download/${currentSessionId}`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Download failed');
        }

        // Create blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `training_block_${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        downloadBtn.disabled = false;
        downloadBtn.textContent = '📦 Download Training Block (ZIP)';

    } catch (error) {
        console.error('Download error:', error);
        alert(`Download failed: ${error.message}`);
        downloadBtn.disabled = false;
        downloadBtn.textContent = '📦 Download Training Block (ZIP)';
    }
});

// New block button handler
newBlockBtn.addEventListener('click', () => {
    // Reset everything
    currentSessionId = null;
    currentStatus = null;
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }

    // Reset UI
    successContainer.style.display = 'none';
    progressContainer.style.display = 'none';
    formContainer.style.display = 'block';

    // Reset progress
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    progressMessage.textContent = 'Initializing...';
    errorMessage.style.display = 'none';

    // Clear summary
    summaryContent.innerHTML = '';

    // Re-enable button
    generateBtn.disabled = false;
    generateBtn.textContent = 'Generate Training Block';

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Form validation helpers
document.getElementById('threshold_t1_pace').addEventListener('input', (e) => {
    validatePaceFormat(e.target);
});

document.getElementById('threshold_t2_pace').addEventListener('input', (e) => {
    validatePaceFormat(e.target);
});

function validatePaceFormat(input) {
    const value = input.value;
    const pattern = /^\d{1,2}:\d{2}$/;

    if (value && !pattern.test(value)) {
        input.setCustomValidity('Please use mm:ss format (e.g., 4:37)');
    } else {
        input.setCustomValidity('');
    }
}

// Training week structure validation
const restDaysInput = document.getElementById('rest_days');
const totalSessionsInput = document.getElementById('total_sessions_per_week');
const doubleDaysInput = document.getElementById('double_days');
const runsPerWeekInput = document.getElementById('runs_per_week');

function validateWeekStructure() {
    const restDays = restDaysInput.value.split(',').filter(d => d.trim()).length || 1;
    const trainingDays = 7 - restDays;
    const totalSessions = parseInt(totalSessionsInput.value) || 0;
    const runsPerWeek = parseInt(runsPerWeekInput.value) || 0;

    // Check if runs exceed total sessions
    if (runsPerWeek > totalSessions) {
        runsPerWeekInput.setCustomValidity(`Runs per week (${runsPerWeek}) cannot exceed total sessions (${totalSessions})`);
        return false;
    } else {
        runsPerWeekInput.setCustomValidity('');
    }

    // Check if sessions fit in training days
    const maxSessions = trainingDays * 2;
    if (totalSessions > maxSessions) {
        totalSessionsInput.setCustomValidity(`Cannot fit ${totalSessions} sessions in ${trainingDays} training days (max: ${maxSessions})`);
        return false;
    } else {
        totalSessionsInput.setCustomValidity('');
    }

    // Calculate required double days
    const requiredDoubleDays = totalSessions - trainingDays;
    if (requiredDoubleDays > 0) {
        const doubleDays = doubleDaysInput.value.split(',').filter(d => d.trim()).length;
        if (doubleDays !== requiredDoubleDays) {
            doubleDaysInput.setCustomValidity(`You need ${requiredDoubleDays} double day(s) to fit ${totalSessions} sessions in ${trainingDays} training days`);
            return false;
        } else {
            doubleDaysInput.setCustomValidity('');
        }
    } else {
        doubleDaysInput.setCustomValidity('');
    }

    return true;
}

// Add validation listeners
[restDaysInput, totalSessionsInput, doubleDaysInput, runsPerWeekInput].forEach(input => {
    input.addEventListener('input', validateWeekStructure);
    input.addEventListener('blur', validateWeekStructure);
});

// Initial validation
validateWeekStructure();

// Auto-calculate double days (helper feature)
totalSessionsInput.addEventListener('change', () => {
    const restDays = restDaysInput.value.split(',').filter(d => d.trim()).length || 1;
    const trainingDays = 7 - restDays;
    const totalSessions = parseInt(totalSessionsInput.value) || 0;
    const requiredDoubleDays = totalSessions - trainingDays;

    if (requiredDoubleDays > 0 && !doubleDaysInput.value.trim()) {
        // Suggest double days
        const suggestions = ['Wednesday', 'Saturday', 'Tuesday', 'Thursday', 'Friday'];
        const suggested = suggestions.slice(0, requiredDoubleDays).join(', ');
        doubleDaysInput.placeholder = `Suggestion: ${suggested}`;
    }
});

console.log('Blocksmith web interface loaded');
