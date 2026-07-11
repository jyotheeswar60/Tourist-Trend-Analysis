/**
 * kpi_counter.js — KPI animated counter utility
 *
 * Dash automatically serves all files in assets/ to the browser.
 * This file defines window.animateKPI() which is called from
 * clientside_callbacks in each page that displays KPI cards.
 *
 * Usage (from a Dash clientside_callback):
 *   window.animateKPI('element-id', 1234567, '$', '', 0)
 *   window.animateKPI('element-id', 87.4, '', '%', 1)
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
 * @param {Array} configs - [{id, value, prefix, suffix, decimals}]
 */
window.animateAllKPIs = function(configs) {
    if (!configs || !Array.isArray(configs)) return;
    configs.forEach(function(cfg) {
        window.animateKPI(cfg.id, cfg.value, cfg.prefix || '', cfg.suffix || '', cfg.decimals || 0);
    });
};
