/*
 * Blocksmith - Client-Side JavaScript
 * Handles form submission, progress tracking, and results display
 */

// Global state
let currentSessionId = null;
let progressInterval = null;

// Stage progression mapping
const STAGES = [
    { id: 'planning', name: 'Planning Agent', duration: 2 },
    { id: 'running', name: 'Running Coach', duration: 3 },
    { id: 'strength', name: 'Strength Coach', duration: 3 },
    { id: 'hyrox', name: 'HYROX Specialist', duration: 3 },
    { id: 'recovery', name: 'Recovery Coach', duration: 2 },
    { id: 'coordinator', name: 'Programming Coordinator', duration: 4 },
    { id: 'qa', name: 'Quality Assurance', duration: 3 }
];

const TOTAL_DURATION_MS = 18 * 60 * 1000; // 18 minutes in milliseconds
let generationStartTime = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('trainingForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

/**
 * Toggle collapsible sections
 */
function toggleSection(headerElement) {
    const section = headerElement.closest('.form-section');
    const content = section.querySelector('.section-content');
    const header = section.querySelector('.section-header');

    if (content.classList.contains('collapsed')) {
        content.classList.remove('collapsed');
        header.classList.add('active');
    } else {
        content.classList.add('collapsed');
        header.classList.remove('active');
    }
}

/**
 * Parse comma-separated text areas into arrays
 */
function parseCommaSeparated(value) {
    if (!value || value.trim() === '') return [];
    return value.split(',').map(item => item.trim()).filter(item => item.length > 0);
}

/**
 * Collect form data
 */
function collectFormData() {
    const formData = {};

    // Get all form inputs
    const inputs = document.querySelectorAll('#trainingForm input, #trainingForm select, #trainingForm textarea');

    inputs.forEach(input => {
        const name = input.name || input.id;
        let value = input.value;

        // Skip empty optional fields
        if (!value && !input.required) {
            return;
        }

        // Handle comma-separated fields
        if (input.id === 'specific_focus_areas' ||
            input.id === 'current_injuries' ||
            input.id === 'injury_history' ||
            input.id === 'movement_restrictions') {
            formData[name] = parseCommaSeparated(value);
        } else {
            formData[name] = value;
        }
    });

    return formData;
}

/**
 * Validate form data
 */
function validateForm(data) {
    const errors = [];

    // Required fields
    if (!data.name || data.name.trim() === '') {
        errors.push('Athlete name is required');
    }

    if (!data.age || parseInt(data.age) < 15 || parseInt(data.age) > 80) {
        errors.push('Age must be between 15 and 80');
    }

    if (!data.rest_day) {
        errors.push('Rest day is required');
    }

    if (!data.long_run_day) {
        errors.push('Long run day is required');
    }

    if (!data.primary_goal) {
        errors.push('Training phase is required');
    }

    if (!data.running_mileage_week1 || parseFloat(data.running_mileage_week1) < 15) {
        errors.push('Week 1 mileage must be at least 15km');
    }

    if (!data.block_duration_weeks || parseInt(data.block_duration_weeks) < 2 || parseInt(data.block_duration_weeks) > 8) {
        errors.push('Block duration must be between 2 and 8 weeks');
    }

    return errors;
}

/**
 * Poll status endpoint
 */
async function pollStatus(sessionId) {
    try {
        const response = await fetch(`/status/${sessionId}`);
        const result = await response.json();

        if (result.status === 'completed') {
            stopProgressSimulation();
            currentSessionId = sessionId;
            showResults(result.summary);
            return true; // Stop polling
        } else if (result.status === 'failed') {
            stopProgressSimulation();
            alert('Generation failed: ' + result.error);
            resetForm();
            return true; // Stop polling
        }

        return false; // Keep polling
    } catch (error) {
        console.error('Error polling status:', error);
        return false; // Keep polling
    }
}

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();

    // Collect and validate form data
    const formData = collectFormData();
    const errors = validateForm(formData);

    if (errors.length > 0) {
        alert('Please fix the following errors:\n\n' + errors.join('\n'));
        return;
    }

    // Hide form, show progress
    document.getElementById('formContainer').style.display = 'none';
    document.getElementById('progressContainer').style.display = 'block';

    // Start generation timer
    generationStartTime = Date.now();

    // Start progress simulation
    startProgressSimulation();

    try {
        // Submit to backend (starts background task)
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success && result.session_id) {
            // Start polling for status every 3 seconds
            const pollInterval = setInterval(async () => {
                const done = await pollStatus(result.session_id);
                if (done) {
                    clearInterval(pollInterval);
                }
            }, 3000);
        } else {
            throw new Error(result.error || 'Failed to start generation');
        }

    } catch (error) {
        stopProgressSimulation();
        alert('Error generating training block: ' + error.message);
        resetForm();
    }
}

/**
 * Start progress bar simulation
 */
function startProgressSimulation() {
    let currentStageIndex = 0;
    let stageStartTime = Date.now();

    progressInterval = setInterval(() => {
        const elapsed = Date.now() - generationStartTime;
        const progress = Math.min((elapsed / TOTAL_DURATION_MS) * 100, 95); // Cap at 95% until complete

        // Update progress bar
        document.getElementById('progressBar').style.width = progress + '%';

        // Update progress text
        const minutesElapsed = Math.floor(elapsed / 60000);
        const secondsElapsed = Math.floor((elapsed % 60000) / 1000);
        document.getElementById('progressText').textContent =
            `${minutesElapsed}:${secondsElapsed.toString().padStart(2, '0')} elapsed - Estimated time remaining: ${Math.max(0, 18 - minutesElapsed)} minutes`;

        // Update stage indicators based on elapsed time
        const cumulativeDuration = STAGES.slice(0, currentStageIndex + 1)
            .reduce((sum, stage) => sum + stage.duration, 0);
        const expectedTime = (cumulativeDuration / 20) * TOTAL_DURATION_MS; // 20 is sum of all durations

        if (elapsed >= expectedTime && currentStageIndex < STAGES.length - 1) {
            // Mark current stage as complete
            const currentStageElement = document.getElementById(`stage-${STAGES[currentStageIndex].id}`);
            if (currentStageElement) {
                currentStageElement.classList.remove('active');
                currentStageElement.classList.add('complete');
                currentStageElement.querySelector('.stage-icon').textContent = '✓';
            }

            // Move to next stage
            currentStageIndex++;
            stageStartTime = Date.now();

            // Mark next stage as active
            const nextStageElement = document.getElementById(`stage-${STAGES[currentStageIndex].id}`);
            if (nextStageElement) {
                nextStageElement.classList.add('active');
                nextStageElement.querySelector('.stage-icon').textContent = '⏳';
            }
        }

    }, 500); // Update every 500ms
}

/**
 * Stop progress simulation
 */
function stopProgressSimulation() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }

    // Set progress to 100%
    document.getElementById('progressBar').style.width = '100%';

    // Mark all stages as complete
    STAGES.forEach(stage => {
        const stageElement = document.getElementById(`stage-${stage.id}`);
        if (stageElement) {
            stageElement.classList.remove('active');
            stageElement.classList.add('complete');
            stageElement.querySelector('.stage-icon').textContent = '✓';
        }
    });
}

/**
 * Show results
 */
function showResults(summary) {
    // Hide progress, show results
    document.getElementById('progressContainer').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'block';

    // Populate summary
    const summaryHTML = `
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-label">Athlete</div>
                <div class="summary-value">${summary.athlete}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Training Phase</div>
                <div class="summary-value">${summary.phase}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Block Duration</div>
                <div class="summary-value">${summary.weeks} weeks</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Starting Mileage</div>
                <div class="summary-value">${summary.starting_mileage}km</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Generation Time</div>
                <div class="summary-value">${summary.generation_time}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">AI Tokens Used</div>
                <div class="summary-value">${summary.total_tokens.toLocaleString()}</div>
            </div>
        </div>
    `;

    document.getElementById('resultsSummary').innerHTML = summaryHTML;

    // Load training block preview by default
    viewContent('training_block');
}

/**
 * Download file
 */
async function downloadFile(fileType) {
    if (!currentSessionId) {
        alert('No session available');
        return;
    }

    try {
        window.location.href = `/download/${currentSessionId}/${fileType}`;
    } catch (error) {
        alert('Error downloading file: ' + error.message);
    }
}

/**
 * View content
 */
async function viewContent(contentType) {
    if (!currentSessionId) {
        alert('No session available');
        return;
    }

    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${contentType}"]`)?.classList.add('active');

    // Show loading
    document.getElementById('previewContent').textContent = 'Loading...';

    try {
        const response = await fetch(`/view/${currentSessionId}/${contentType}`);
        const result = await response.json();

        if (result.success) {
            document.getElementById('previewContent').textContent = result.content;
        } else {
            throw new Error(result.error || 'Failed to load content');
        }
    } catch (error) {
        document.getElementById('previewContent').textContent =
            'Error loading content: ' + error.message;
    }
}

/**
 * Reset form and start over
 */
function resetForm() {
    // Clean up session if exists
    if (currentSessionId) {
        fetch(`/cleanup/${currentSessionId}`, { method: 'POST' })
            .catch(err => console.error('Cleanup error:', err));
        currentSessionId = null;
    }

    // Stop any running intervals
    stopProgressSimulation();

    // Reset progress indicators
    STAGES.forEach(stage => {
        const stageElement = document.getElementById(`stage-${stage.id}`);
        if (stageElement) {
            stageElement.classList.remove('active', 'complete');
            stageElement.querySelector('.stage-icon').textContent = '⏳';
        }
    });

    // Reset progress bar
    document.getElementById('progressBar').style.width = '0%';
    document.getElementById('progressText').textContent = 'Starting generation...';

    // Show form, hide others
    document.getElementById('formContainer').style.display = 'block';
    document.getElementById('progressContainer').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'none';

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
