// Blocksmith Web Interface - Client-side JavaScript

let currentSessionId = null;
let progressInterval = null;
let currentStatus = null; // Store the full status for access in download
let humorInterval = null;
let currentHumorIndex = 0;

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
const humorMessage = document.getElementById('humor-message');

// HYROX-themed humorous messages
const humorMessages = [
    "🏃 Calculating how much you'll hate the burpee broad jumps...",
    "💪 Programming the perfect amount of suffering...",
    "🛷 Teaching the sled to respect you (it won't)...",
    "📊 Calculating roxzone shame levels...",
    "⏱️ Adding just enough running to question your life choices...",
    "💯 Programming the deload week you'll definitely skip...",
    "🎭 Choreographing your roxzone theatre performance...",
    "🏆 Preparing you for farmers carry humility...",
    "🔥 Optimizing your love-hate relationship with wall balls...",
    "⚡ Ensuring the sled push breaks your spirit (but not your legs)...",
    "🎯 Calibrating burpee misery to acceptable levels...",
    "🌟 Adding more running because you clearly haven't suffered enough...",
    "💀 Programming SkiErg sessions that'll haunt your dreams...",
    "🎪 Planning your roxzone walk of shame timing...",
    "🏋️ Calculating exactly when you'll regret this training block...",
    "⚠️ Warning: May cause spontaneous hatred of burpees...",
    "🚀 Launching your fitness to places you didn't ask to go...",
    "😅 Adding transitions so smooth you'll actually miss them (you won't)...",
    "🎨 Painting a masterpiece of metabolic distress...",
    "🏃‍♀️ Strategically placing running to maximize existential dread...",
    "💪 Ensuring lunges are just the right amount of terrible...",
    "🎲 Rolling the dice on your recovery capacity...",
    "⏰ Timing wall balls to coincide with your will to live leaving...",
    "🔨 Hammering out a plan that'll hammer you...",
    "🎯 Targeting your weaknesses (spoiler: it's everything)...",
    "🌈 Finding the silver lining in the farmers carry (there isn't one)...",
    "📈 Graphing your suffering trajectory (it's exponential)...",
    "🏆 Preparing motivational content for when you're crying in the roxzone...",
    "⚡ Electrifying your training with just enough pain...",
    "🎪 Orchestrating the greatest show on earth: you vs. the sled...",
    "💥 Explosive power training (you'll feel the explosion tomorrow)...",
    "🌟 Manifesting PR energy (and by PR we mean 'personal regret')...",
    "🎭 Dramaturging your breakdown at station 5...",
    "🏃 Planning running intervals that make you reconsider your hobby...",
    "💪 Configuring wall ball hell in 5... 4... 3...",
    "🛷 Calculating optimal sled drag soul-crushing coefficient...",
    "⏱️ Synchronizing your watch with your impending doom...",
    "🔥 Forging a training plan in the fires of Mount Doom...",
    "📊 Generating enough volume to make CrossFitters jealous...",
    "🎯 Precision-engineering your suffering for maximum gains...",
];

// Rotate humor messages
function rotateHumorMessage() {
    if (!humorMessage) return;

    // Fade out
    humorMessage.style.opacity = '0';

    setTimeout(() => {
        // Change message
        currentHumorIndex = (currentHumorIndex + 1) % humorMessages.length;
        humorMessage.textContent = humorMessages[currentHumorIndex];

        // Fade in
        humorMessage.style.opacity = '1';
    }, 300); // Match CSS transition time
}

// Start humor rotation
function startHumorRotation() {
    // Show first message immediately
    currentHumorIndex = Math.floor(Math.random() * humorMessages.length);
    humorMessage.textContent = humorMessages[currentHumorIndex];
    humorMessage.style.display = 'block';
    humorMessage.style.opacity = '1';

    // Rotate every 3 seconds
    humorInterval = setInterval(rotateHumorMessage, 3000);
}

// Stop humor rotation
function stopHumorRotation() {
    if (humorInterval) {
        clearInterval(humorInterval);
        humorInterval = null;
    }
    if (humorMessage) {
        humorMessage.style.opacity = '0';
        setTimeout(() => {
            humorMessage.style.display = 'none';
        }, 300); // Wait for fade out
    }
}

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

        // Start humor rotation
        startHumorRotation();

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

            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Server returned an error. Check the console for details.');
            }

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to get status');
            }

            // Update progress bar
            updateProgress(result.progress, result.message);

            // Check if complete
            if (result.status === 'complete') {
                clearInterval(progressInterval);
                stopHumorRotation();
                currentStatus = result; // Store the full status
                showSuccess(result);
            } else if (result.status === 'error') {
                clearInterval(progressInterval);
                stopHumorRotation();
                showError(result.error || 'Generation failed');
            }

        } catch (error) {
            console.error('Error polling status:', error);
            clearInterval(progressInterval);
            stopHumorRotation();
            showError(error.message);
        }
    }, 1000); // Poll every second
}

// Map technical layer names to user-friendly messages
function getUserFriendlyMessage(layerName) {
    const messageMap = {
        'Layer 0': '📋 Setting up your training framework...',
        'Layer 1': '🏗️ Building Week 1 structure...',
        'Layer 2': '🏃 Designing your running sessions...',
        'Layer 3': '💪 Programming max strength work...',
        'Layer 4': '🔥 Crafting strength endurance sessions...',
        'Layer 5': '⚡ Creating HYROX combo workouts...',
        'Layer 6': '🌊 Planning recovery and aerobic work...',
        'Layer 7': '✨ Completing Week 1: Building your base...',
        'Layer 8': '📈 Building Week 2: Adding volume...',
        'Layer 9': '🎯 Building Week 3: Increasing intensity...',
        'Layer 10': '🚀 Building Week 4: Peak volume...',
        'Layer 11': '😌 Planning your deload week...',
        'Layer 12': '🏆 Finalizing your training block...',
    };

    // Check for exact match first
    if (messageMap[layerName]) {
        return messageMap[layerName];
    }

    // Handle week-specific layers (e.g., "Layer 8 - Week 2")
    const weekMatch = layerName.match(/Layer (\d+)/);
    if (weekMatch) {
        const layerNum = parseInt(weekMatch[1]);
        if (layerNum >= 7 && layerNum <= 10) {
            const weekNum = layerNum - 6;
            const weekMessages = {
                1: '✨ Completing Week 1: Building your base...',
                2: '📈 Building Week 2: Adding volume...',
                3: '🎯 Building Week 3: Increasing intensity...',
                4: '🚀 Building Week 4: Peak volume...'
            };
            return weekMessages[weekNum] || `Building Week ${weekNum}...`;
        } else if (layerNum === 11) {
            return '😌 Planning your deload week...';
        }
    }

    // Check if it contains "deload" (case insensitive)
    if (layerName.toLowerCase().includes('deload')) {
        return '😌 Planning your deload week...';
    }

    // Default fallback
    return layerName;
}

// Update progress bar
function updateProgress(percent, message) {
    progressBar.style.width = `${percent}%`;
    progressText.textContent = `${percent}%`;

    // Convert technical message to user-friendly
    const friendlyMessage = getUserFriendlyMessage(message || 'Processing...');
    progressMessage.textContent = friendlyMessage;
}

// Show success screen
function showSuccess(result) {
    // Redirect to the beautiful success page instead of showing inline
    window.location.href = `/success/${currentSessionId}`;
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
    stopHumorRotation();

    // Reset UI
    successContainer.style.display = 'none';
    progressContainer.style.display = 'none';
    formContainer.style.display = 'block';

    // Reset progress
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    progressMessage.textContent = 'Initializing...';
    errorMessage.style.display = 'none';

    // Clear summary and humor
    summaryContent.innerHTML = '';
    humorMessage.textContent = '';

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

// Toggle collapsible sections
function toggleSection(contentId, iconId) {
    const content = document.getElementById(contentId);
    const icon = document.getElementById(iconId);

    if (content.style.display === 'none') {
        // Expand
        content.style.display = 'block';
        icon.textContent = '▼';
        icon.classList.add('rotated');
    } else {
        // Collapse
        content.style.display = 'none';
        icon.textContent = '▶';
        icon.classList.remove('rotated');
    }
}

// Auto-check equipment based on gym setup selection
const gymSetupDropdown = document.getElementById('gym_setup');
if (gymSetupDropdown) {
    gymSetupDropdown.addEventListener('change', function() {
        const selectedSetup = this.value;
        const allCheckboxes = document.querySelectorAll('input[name="equipment"]');

        // Define equipment sets for each gym type
        const fullHyroxGym = [
            'Sled', 'SkiErg', 'Wall Balls', 'Sandbag', 'Farmers Carry handles', 'Sled Track',
            'Rowing Machine', 'Echo Bike', 'Exercise Bike', 'Treadmill',
            'Full barbell setup', 'Dumbbells', 'Kettlebells', 'Pull-up Bar'
        ];

        const standardGym = [
            'Rowing Machine', 'Exercise Bike', 'Treadmill',
            'Full barbell setup', 'Dumbbells', 'Kettlebells', 'Pull-up Bar'
        ];

        allCheckboxes.forEach(checkbox => {
            if (selectedSetup === 'Full HYROX Gym') {
                checkbox.checked = fullHyroxGym.includes(checkbox.value);
            } else if (selectedSetup === 'Standard Gym') {
                checkbox.checked = standardGym.includes(checkbox.value);
            } else if (selectedSetup === 'Limited Equipment') {
                checkbox.checked = false;
            }
        });
    });
}

// Toggle collapsible sections
function toggleSection(contentId, iconId) {
    const content = document.getElementById(contentId);
    const icon = document.getElementById(iconId);

    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.textContent = '▼';
    } else {
        content.style.display = 'none';
        icon.textContent = '▶';
    }
}

// Model options for each provider
const modelOptions = {
    anthropic: [
        { value: "claude-sonnet-4-5-20250929", name: "Claude Sonnet 4.5", info: "200K context, balanced performance (recommended)" },
        { value: "claude-3-5-sonnet-20241022", name: "Claude 3.5 Sonnet", info: "200K context, very capable" },
        { value: "claude-opus-4-20250514", name: "Claude Opus 4", info: "200K context, most capable" }
    ],
    openai: [
        { value: "gpt-4o", name: "GPT-4o", info: "128K context, fast and capable (recommended)" },
        { value: "gpt-4-turbo", name: "GPT-4 Turbo", info: "128K context, strong reasoning" },
        { value: "o1-preview", name: "o1-preview (Reasoning)", info: "128K context, slower but thoughtful" }
    ],
    gemini: [
        { value: "gemini-3-pro-preview", name: "Gemini 3 Pro (Preview)", info: "Latest Gemini 3 model, preview release (recommended)" },
        { value: "gemini-1.5-pro", name: "Gemini 1.5 Pro", info: "2M context, excellent for long prompts" },
        { value: "gemini-2.0-flash-exp", name: "Gemini 2.0 Flash (Experimental)", info: "1M context, very fast" },
        { value: "gemini-1.5-flash", name: "Gemini 1.5 Flash", info: "1M context, budget-friendly" }
    ]
};

// Update model dropdown based on selected provider
function updateModelOptions() {
    const provider = document.getElementById('ai_provider').value;
    const modelSelect = document.getElementById('model_name');
    const modelInfo = document.getElementById('model_info');

    // Clear existing options
    modelSelect.innerHTML = '';

    // Add new options
    modelOptions[provider].forEach(model => {
        const option = document.createElement('option');
        option.value = model.value;
        option.textContent = model.name;
        option.dataset.info = model.info;
        modelSelect.appendChild(option);
    });

    // Update info text
    modelInfo.textContent = modelSelect.options[modelSelect.selectedIndex].dataset.info;
}

// Initialize model options on page load
document.addEventListener('DOMContentLoaded', function() {
    updateModelOptions();

    // Update info when model changes
    const modelSelect = document.getElementById('model_name');
    if (modelSelect) {
        modelSelect.addEventListener('change', function() {
            const modelInfo = document.getElementById('model_info');
            modelInfo.textContent = this.options[this.selectedIndex].dataset.info;
        });
    }
});

console.log('Blocksmith web interface loaded');
