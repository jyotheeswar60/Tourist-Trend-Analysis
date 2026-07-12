/**
 * kpi_counter.js — KPI animated counter utility
 *
 * Dash automatically serves all files in assets/ to the browser.
 * This file defines window.animateKPI() and hooks a MutationObserver
 * to automatically trigger count-up animations for any .kpi-card-value
 * elements when they load or change.
 */

window.animateKPI = function(elementId, target, prefix, suffix, decimals) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const duration = 1400;  // ms — feels snappy but not rushed
    const easeOut  = (t) => 1 - Math.pow(1 - t, 3);  // cubic ease-out

    let startTime = null;

    function step(timestamp) {
        if (!startTime) startTime = timestamp;
        const elapsed  = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased    = easeOut(progress);
        const current  = eased * target;

        let formatted;
        if (decimals > 0) {
            formatted = (prefix || '') + current.toFixed(decimals) + (suffix || '');
        } else {
            // Add thousands separators
            formatted = (prefix || '') + Math.floor(current).toLocaleString('en-US') + (suffix || '');
        }

        el.textContent = formatted;

        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            // Final precise value
            const final = decimals > 0
                ? (prefix || '') + target.toFixed(decimals) + (suffix || '')
                : (prefix || '') + target.toLocaleString('en-US') + (suffix || '');
            el.textContent = final;
        }
    }

    requestAnimationFrame(step);
};

/**
 * Animate multiple KPIs at once.
 */
window.animateAllKPIs = function(configs) {
    if (!configs || !Array.isArray(configs)) return;
    configs.forEach(function(cfg) {
        window.animateKPI(cfg.id, cfg.value, cfg.prefix || '', cfg.suffix || '', cfg.decimals || 0);
    });
};

// ── Automatic MutationObserver for KPI Animation ─────────────────────────────
(function() {
    function parseKPIValue(text) {
        text = text.trim();
        if (text === "" || text === "—") return null;

        // Match numbers like: $12.3M, 45.2%, 123,456, 4.82 / 5.0, 4.8 days
        const match = text.match(/^([^0-9\-\+]*)([\d,\.\+]+)(.*)$/);
        if (!match) return null;

        const prefix = match[1];
        const numStr = match[2].replace(/,/g, '');
        const suffix = match[3];

        const value = parseFloat(numStr);
        if (isNaN(value)) return null;

        const dotIdx = numStr.indexOf('.');
        const decimals = dotIdx >= 0 ? (numStr.length - dotIdx - 1) : 0;

        return { value, prefix, suffix, decimals };
    }

    function triggerAnimation(el) {
        if (el.getAttribute('data-animating') === 'true') return;

        const originalText = el.textContent.trim();
        if (originalText === "" || originalText === "—") return;

        const parsed = parseKPIValue(originalText);
        if (!parsed) return;

        el.setAttribute('data-animating', 'true');

        const duration = 1400; // ms
        const easeOut = (t) => 1 - Math.pow(1 - t, 3);
        const startTime = performance.now();

        function step(timestamp) {
            const elapsed = timestamp - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = easeOut(progress);
            const current = eased * parsed.value;

            let formatted;
            if (parsed.decimals > 0) {
                formatted = (parsed.prefix || '') + current.toFixed(parsed.decimals) + (parsed.suffix || '');
            } else {
                formatted = (parsed.prefix || '') + Math.floor(current).toLocaleString('en-US') + (parsed.suffix || '');
            }

            el.textContent = formatted;

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                el.textContent = originalText;
                el.removeAttribute('data-animating');
            }
        }

        requestAnimationFrame(step);
    }

    // Monitor DOM for new KPI values or changes
    const kpiObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.classList.contains('kpi-card-value')) {
                            triggerAnimation(node);
                        }
                        node.querySelectorAll('.kpi-card-value').forEach(triggerAnimation);
                    }
                });
            }

            let targetEl = null;
            if (mutation.type === 'characterData') {
                targetEl = mutation.target.parentElement;
            }
            if (targetEl && targetEl.classList && targetEl.classList.contains('kpi-card-value')) {
                triggerAnimation(targetEl);
            }
        });
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelectorAll('.kpi-card-value').forEach(triggerAnimation);
            kpiObserver.observe(document.body, { childList: true, subtree: true, characterData: true });
        });
    } else {
        document.querySelectorAll('.kpi-card-value').forEach(triggerAnimation);
        kpiObserver.observe(document.body, { childList: true, subtree: true, characterData: true });
    }
})();
