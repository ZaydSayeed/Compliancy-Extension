/**
 * Floating Widget for Shariah Compliance Checker
 * Displays compliance status badge next to hovered tickers
 */

(function () {
    let widget = null;
    let hideTimeout = null;

    /**
     * Create the floating widget element
     */
    function createWidget() {
        if (widget) return widget;

        widget = document.createElement('div');
        widget.className = 'shariah-compliance-widget';
        widget.innerHTML = `
            <div class="scw-header">
                <span class="scw-ticker"></span>
                <span class="scw-status-badge"></span>
            </div>
            <div class="scw-source"></div>
            <div class="scw-hint">Click for details</div>
        `;

        document.body.appendChild(widget);

        // Add click handler to open popup
        widget.addEventListener('click', () => {
            // Trigger extension popup or show details
            chrome.runtime.sendMessage({ action: 'openPopup' });
        });

        // Prevent hiding when hovering over widget
        widget.addEventListener('mouseenter', () => {
            if (hideTimeout) {
                clearTimeout(hideTimeout);
                hideTimeout = null;
            }
        });

        widget.addEventListener('mouseleave', () => {
            hideTimeout = setTimeout(() => {
                hideWidget();
            }, 500);
        });

        return widget;
    }

    /**
     * Show the compliance widget at specified position
     */
    function showComplianceWidget(x, y, data) {
        const w = createWidget();

        // Clear any pending hide
        if (hideTimeout) {
            clearTimeout(hideTimeout);
            hideTimeout = null;
        }

        // Update content
        updateWidgetContent(w, data);

        // Position the widget
        w.style.display = 'block';

        // Calculate position (avoid going off-screen)
        const rect = w.getBoundingClientRect();
        const padding = 10;

        let left = x + padding;
        let top = y + padding;

        // Adjust if going off right edge
        if (left + 220 > window.innerWidth) {
            left = x - 220 - padding;
        }

        // Adjust if going off bottom edge
        if (top + 100 > window.innerHeight) {
            top = y - 100 - padding;
        }

        w.style.left = `${left}px`;
        w.style.top = `${top}px`;
    }

    /**
     * Update widget content with compliance data
     */
    function updateWidgetContent(w, data) {
        const tickerEl = w.querySelector('.scw-ticker');
        const badgeEl = w.querySelector('.scw-status-badge');
        const sourceEl = w.querySelector('.scw-source');

        tickerEl.textContent = data.ticker;

        // Set status badge
        if (data.status === 'loading') {
            badgeEl.textContent = '⏳ Checking...';
            badgeEl.className = 'scw-status-badge scw-loading';
            sourceEl.textContent = '';
        } else if (data.status === 'compliant') {
            badgeEl.textContent = '✅ Halal';
            badgeEl.className = 'scw-status-badge scw-compliant';
            sourceEl.textContent = `Source: ${data.source}`;
        } else if (data.status === 'not_compliant') {
            badgeEl.textContent = '❌ Not Halal';
            badgeEl.className = 'scw-status-badge scw-not-compliant';
            sourceEl.textContent = `Source: ${data.source}`;
        } else if (data.status === 'doubtful') {
            badgeEl.textContent = '⚠️ Doubtful';
            badgeEl.className = 'scw-status-badge scw-doubtful';
            sourceEl.textContent = `Source: ${data.source}`;
        } else if (data.status === 'error') {
            badgeEl.textContent = '⚠️ Error';
            badgeEl.className = 'scw-status-badge scw-error';
            sourceEl.textContent = data.error || 'Check failed';
        }
    }

    /**
     * Update an existing widget
     */
    function updateComplianceWidget(data) {
        if (widget) {
            updateWidgetContent(widget, data);
        }
    }

    /**
     * Hide the widget
     */
    function hideComplianceWidget() {
        if (widget) {
            widget.style.display = 'none';
        }
    }

    // Expose functions globally for content.js
    window.showComplianceWidget = showComplianceWidget;
    window.updateComplianceWidget = updateComplianceWidget;
    window.hideComplianceWidget = hideComplianceWidget;
})();
