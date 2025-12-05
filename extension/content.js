/**
 * Content Script for Shariah Compliance Checker
 * Detects stock tickers on hover and displays compliance widget
 */

// Common stock ticker pattern (1-5 uppercase letters)
const TICKER_PATTERN = /\b[A-Z]{1,5}\b/;

// Known tickers for validation (expandable list)
const COMMON_TICKERS = new Set([
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 'INTC',
    'NFLX', 'BABA', 'V', 'MA', 'JPM', 'BAC', 'WMT', 'DIS', 'PYPL', 'ADBE',
    'CRM', 'ORCL', 'CSCO', 'IBM', 'QCOM', 'TXN', 'AVGO', 'NOW', 'SQ', 'SHOP',
    'ZM', 'UBER', 'LYFT', 'SNAP', 'PINS', 'TWTR', 'SPOT', 'ROKU', 'COIN', 'HOOD',
    'NKE', 'SBUX', 'MCD', 'KO', 'PEP', 'PG', 'JNJ', 'UNH', 'HD', 'LOW',
    'BUD', 'LVS', 'MGM', 'WYNN', 'PM', 'MO', 'BTI'  // Include some non-compliant for testing
]);

// Exclusion list for common words that look like tickers
const EXCLUDED_WORDS = new Set([
    'A', 'I', 'AM', 'PM', 'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU',
    'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'HAD', 'HAS',
    'HIS', 'HOW', 'ITS', 'LET', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'WAY',
    'WHO', 'BOY', 'DID', 'GET', 'HIM', 'HOW', 'MAN', 'SAY', 'SHE', 'TOO',
    'USE', 'USD', 'USA', 'UK', 'EU', 'CEO', 'CFO', 'COO', 'CTO', 'VP',
    'HR', 'IT', 'AI', 'ML', 'API', 'URL', 'FAQ', 'IPO', 'ETF', 'PDF'
]);

let currentWidget = null;
let hoverTimeout = null;
let lastCheckedTicker = null;

/**
 * Check if a word is likely a stock ticker
 */
function isLikelyTicker(word) {
    if (!word || word.length < 1 || word.length > 5) return false;
    if (EXCLUDED_WORDS.has(word.toUpperCase())) return false;
    if (!TICKER_PATTERN.test(word)) return false;

    // Accept known tickers or potential new ones (3-4 letters more likely)
    if (COMMON_TICKERS.has(word.toUpperCase())) return true;

    // Heuristic: 3-4 letter words are more likely to be tickers
    return word.length >= 3 && word.length <= 4;
}

/**
 * Get the word under the cursor
 */
function getWordUnderCursor(event) {
    const range = document.caretRangeFromPoint(event.clientX, event.clientY);
    if (!range) return null;

    const textNode = range.startContainer;
    if (textNode.nodeType !== Node.TEXT_NODE) return null;

    const text = textNode.textContent;
    const offset = range.startOffset;

    // Find word boundaries
    let start = offset;
    let end = offset;

    while (start > 0 && /[A-Za-z]/.test(text[start - 1])) {
        start--;
    }
    while (end < text.length && /[A-Za-z]/.test(text[end])) {
        end++;
    }

    const word = text.slice(start, end).toUpperCase();
    return word;
}

/**
 * Handle mouse movement for ticker detection
 */
function handleMouseMove(event) {
    // Clear any pending hover timeout
    if (hoverTimeout) {
        clearTimeout(hoverTimeout);
    }

    // Set a short delay before checking (prevents excessive API calls)
    hoverTimeout = setTimeout(async () => {
        const word = getWordUnderCursor(event);

        if (word && isLikelyTicker(word) && word !== lastCheckedTicker) {
            lastCheckedTicker = word;

            // Show loading state
            showWidget(event.clientX, event.clientY, {
                ticker: word,
                status: 'loading',
                source: 'Checking...'
            });

            // Request compliance check from background script
            try {
                const response = await chrome.runtime.sendMessage({
                    action: 'checkTicker',
                    ticker: word
                });

                if (response.success) {
                    updateWidget(response.data);

                    // Store for popup access
                    chrome.runtime.sendMessage({
                        action: 'setLastTicker',
                        ticker: word
                    });
                } else {
                    updateWidget({
                        ticker: word,
                        status: 'error',
                        source: 'Error',
                        error: response.error
                    });
                }
            } catch (error) {
                console.error('[Shariah Checker] Error:', error);
                updateWidget({
                    ticker: word,
                    status: 'error',
                    source: 'Error',
                    error: 'Backend unavailable'
                });
            }
        }
    }, 300); // 300ms hover delay
}

/**
 * Show the floating widget near the cursor
 */
function showWidget(x, y, data) {
    // Use the global floating widget functions
    if (typeof window.showComplianceWidget === 'function') {
        window.showComplianceWidget(x, y, data);
    }
}

/**
 * Update the widget with new data
 */
function updateWidget(data) {
    if (typeof window.updateComplianceWidget === 'function') {
        window.updateComplianceWidget(data);
    }
}

/**
 * Hide the widget
 */
function hideWidget() {
    lastCheckedTicker = null;
    if (typeof window.hideComplianceWidget === 'function') {
        window.hideComplianceWidget();
    }
}

// Add event listeners
document.addEventListener('mousemove', handleMouseMove, { passive: true });

// Hide widget when clicking elsewhere or scrolling
document.addEventListener('click', (event) => {
    if (!event.target.closest('.shariah-compliance-widget')) {
        hideWidget();
    }
});

document.addEventListener('scroll', hideWidget, { passive: true });

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (hoverTimeout) {
        clearTimeout(hoverTimeout);
    }
});

console.log('[Shariah Checker] Content script loaded');
