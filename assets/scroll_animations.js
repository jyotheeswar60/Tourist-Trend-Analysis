/**
 * scroll_animations.js — Dynamic scroll-triggered animations (Intersection Observer)
 *
 * This script runs in the browser, watching for elements as they enter the viewport
 * and triggering fade, scale, and slide transitions once. Staggered delays are
 * applied to grid elements to create a premium flow.
 */

(function() {
    function setupScrollAnimations() {
        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -30px 0px', // slight offset trigger for viewport entrance
            threshold: 0.02
        };

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    obs.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // 1. KPI Cards (staggered fade-up)
        document.querySelectorAll('.kpi-grid').forEach(grid => {
            const cards = grid.querySelectorAll('.kpi-card');
            cards.forEach((card, idx) => {
                if (!card.classList.contains('reveal-on-scroll')) {
                    card.classList.add('reveal-on-scroll', 'reveal-fade-up');
                    if (idx > 0 && idx < 8) {
                        card.classList.add(`reveal-delay-${idx}`);
                    }
                    observer.observe(card);
                }
            });
        });

        // 2. Chart Cards (staggered scale-in or fade-up)
        document.querySelectorAll('.chart-card').forEach(card => {
            if (!card.classList.contains('reveal-on-scroll')) {
                const parent = card.parentElement;
                card.classList.add('reveal-on-scroll', 'reveal-scale-in');
                if (parent && parent.classList.contains('chart-grid')) {
                    const siblings = Array.from(parent.children).filter(c => c.classList.contains('chart-card'));
                    const siblingIdx = siblings.indexOf(card);
                    if (siblingIdx > 0 && siblingIdx < 8) {
                        card.classList.add(`reveal-delay-${siblingIdx}`);
                    }
                }
                observer.observe(card);
            }
        });

        // 3. Tables & Containers (fade-up)
        document.querySelectorAll('.table-container, .data-table, .dash-table-container').forEach(el => {
            if (!el.classList.contains('reveal-on-scroll')) {
                el.classList.add('reveal-on-scroll', 'reveal-fade-up');
                observer.observe(el);
            }
        });

        // 4. Insight Items (staggered slide from left)
        document.querySelectorAll('#overview-insights, #adv-insights, #fc-insights, #hotel-insights').forEach(container => {
            const items = container.querySelectorAll('.insight-item');
            items.forEach((item, idx) => {
                if (!item.classList.contains('reveal-on-scroll')) {
                    item.classList.add('reveal-on-scroll', 'reveal-fade-left');
                    if (idx > 0 && idx < 8) {
                        item.classList.add(`reveal-delay-${idx}`);
                    }
                    observer.observe(item);
                }
            });
        });

        // 5. Filter Panels (fade-in)
        document.querySelectorAll('.filter-panel').forEach(panel => {
            if (!panel.classList.contains('reveal-on-scroll')) {
                panel.classList.add('reveal-on-scroll', 'reveal-fade-in');
                observer.observe(panel);
            }
        });

        // 6. Section & Page Titles (fade-right)
        document.querySelectorAll('.page-title, .page-subtitle, .chart-card-title').forEach(title => {
            if (!title.classList.contains('reveal-on-scroll')) {
                title.classList.add('reveal-on-scroll', 'reveal-fade-right');
                observer.observe(title);
            }
        });
    }

    // Initialize Intersection Observer with DOM change tracking (supports Dash SPA single-page routing)
    const domObserver = new MutationObserver(() => {
        setupScrollAnimations();
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setupScrollAnimations();
            domObserver.observe(document.body, { childList: true, subtree: true });
        });
    } else {
        setupScrollAnimations();
        domObserver.observe(document.body, { childList: true, subtree: true });
    }
})();
