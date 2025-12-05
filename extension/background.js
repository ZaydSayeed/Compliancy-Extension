/**
 * Background Service Worker for Shariah Compliance Checker
 * Handles API requests to the backend server
 */

const API_BASE_URL = 'http://localhost:8000';

// Cache for compliance results to reduce API calls
const complianceCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

/**
 * Check compliance status for a ticker
 * @param {string} ticker - Stock ticker symbol
 * @returns {Promise<Object>} Compliance data
 */
async function checkCompliance(ticker) {
    // Check cache first
    const cached = complianceCache.get(ticker);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        return cached.data;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/check?ticker=${encodeURIComponent(ticker)}`);

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        // Cache the result
        complianceCache.set(ticker, {
            data: data,
            timestamp: Date.now()
        });

        return data;
    } catch (error) {
        console.error('[Shariah Checker] API error:', error);
        throw error;
    }
}

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'checkTicker') {
        checkCompliance(request.ticker)
            .then(data => {
                sendResponse({ success: true, data: data });
            })
            .catch(error => {
                sendResponse({
                    success: false,
                    error: error.message || 'Failed to check compliance'
                });
            });

        // Return true to indicate async response
        return true;
    }

    if (request.action === 'getLastResult') {
        // Return the last cached result for the popup
        const ticker = request.ticker;
        const cached = complianceCache.get(ticker);
        if (cached) {
            sendResponse({ success: true, data: cached.data });
        } else {
            sendResponse({ success: false, error: 'No cached result' });
        }
        return true;
    }

    if (request.action === 'clearCache') {
        complianceCache.clear();
        sendResponse({ success: true });
        return true;
    }
});

// Store the last checked ticker for popup access
let lastCheckedTicker = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'setLastTicker') {
        lastCheckedTicker = request.ticker;
    }

    if (request.action === 'getLastTicker') {
        sendResponse({ ticker: lastCheckedTicker });
        return true;
    }
});

console.log('[Shariah Checker] Background service worker started');
