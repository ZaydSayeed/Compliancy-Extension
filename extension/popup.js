/**
 * Popup Script for Shariah Compliance Checker
 * Handles user input and displays detailed compliance breakdown
 */

const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const tickerInput = document.getElementById('tickerInput');
const checkBtn = document.getElementById('checkBtn');
const loadingSection = document.getElementById('loadingSection');
const resultSection = document.getElementById('resultSection');
const errorMessage = document.getElementById('errorMessage');
const tickerSymbol = document.getElementById('tickerSymbol');
const statusBadge = document.getElementById('statusBadge');
const sourceInfo = document.getElementById('sourceInfo');
const breakdownList = document.getElementById('breakdownList');
const breakdownSection = document.getElementById('breakdownSection');

/**
 * Check compliance for a ticker
 */
async function checkCompliance(ticker) {
    try {
        // Show loading, hide results/error
        loadingSection.style.display = 'flex';
        resultSection.classList.remove('visible');
        errorMessage.classList.remove('visible');
        checkBtn.disabled = true;

        const response = await fetch(`${API_BASE_URL}/check?ticker=${encodeURIComponent(ticker)}`);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        const data = await response.json();
        displayResult(data);

    } catch (error) {
        console.error('[Popup] Error:', error);
        showError(error.message || 'Failed to check compliance. Is the backend running?');
    } finally {
        loadingSection.style.display = 'none';
        checkBtn.disabled = false;
    }
}

/**
 * Display compliance result
 */
function displayResult(data) {
    // Set ticker
    tickerSymbol.textContent = data.ticker;

    // Set status badge
    statusBadge.className = 'status-badge';
    if (data.status === 'compliant') {
        statusBadge.textContent = '✅ Halal';
        statusBadge.classList.add('compliant');
    } else if (data.status === 'not_compliant') {
        statusBadge.textContent = '❌ Not Halal';
        statusBadge.classList.add('not-compliant');
    } else if (data.status === 'doubtful') {
        statusBadge.textContent = '⚠️ Doubtful';
        statusBadge.classList.add('doubtful');
    }

    // Set source
    sourceInfo.textContent = `Source: ${data.source}`;

    // Render breakdown
    if (data.breakdown && data.breakdown.length > 0) {
        breakdownSection.style.display = 'block';
        renderBreakdown(data.breakdown);
    } else {
        breakdownSection.style.display = 'none';
    }

    resultSection.classList.add('visible');
}

/**
 * Render compliance breakdown items
 */
function renderBreakdown(breakdown) {
    breakdownList.innerHTML = '';

    breakdown.forEach(item => {
        const div = document.createElement('div');
        div.className = `breakdown-item ${item.passed ? 'passed' : 'failed'}`;

        div.innerHTML = `
            <div class="breakdown-left">
                <span class="breakdown-rule">${item.rule}</span>
                <span class="breakdown-values">${item.value} (Limit: ${item.limit})</span>
            </div>
            <div class="breakdown-right">
                <span class="breakdown-status">${item.passed ? '✔ PASS' : '❌ FAIL'}</span>
                ${item.reason ? `<span class="breakdown-reason">${item.reason}</span>` : ''}
            </div>
        `;

        breakdownList.appendChild(div);
    });
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('visible');
    resultSection.classList.remove('visible');
}

/**
 * Handle check button click
 */
function handleCheck() {
    const ticker = tickerInput.value.trim().toUpperCase();

    if (!ticker) {
        showError('Please enter a ticker symbol');
        return;
    }

    if (!/^[A-Z]{1,5}$/.test(ticker)) {
        showError('Invalid ticker format. Use 1-5 letters.');
        return;
    }

    checkCompliance(ticker);
}

// Event listeners
checkBtn.addEventListener('click', handleCheck);

tickerInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleCheck();
    }
});

// Auto-uppercase input
tickerInput.addEventListener('input', () => {
    tickerInput.value = tickerInput.value.toUpperCase();
});

// Check if there's a last checked ticker from content script
chrome.runtime.sendMessage({ action: 'getLastTicker' }, (response) => {
    if (response && response.ticker) {
        tickerInput.value = response.ticker;
        checkCompliance(response.ticker);
    }
});

// Focus input on open
tickerInput.focus();
