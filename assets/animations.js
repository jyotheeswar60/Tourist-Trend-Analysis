document.addEventListener('DOMContentLoaded', () => {
    // 1. INTERSECTION OBSERVER FOR SCROLL ANIMATIONS
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const scrollObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target); // Animate only once
            }
        });
    }, observerOptions);

    // Observe function that can be called periodically or after React renders
    window.observeElements = () => {
        const elements = document.querySelectorAll('.animate-on-scroll:not(.is-visible)');
        elements.forEach(el => scrollObserver.observe(el));
    };

    // Run initially and set a small interval to catch elements rendered by Dash
    window.observeElements();
    setInterval(window.observeElements, 500);

    // 2. PAGE TRANSITIONS
    // Dash renders pages inside #page-content. We can watch for mutations.
    const pageContent = document.getElementById('page-content');
    if (pageContent) {
        const mutationObserver = new MutationObserver(() => {
            pageContent.classList.remove('page-enter-active');
            void pageContent.offsetWidth; // trigger reflow
            pageContent.classList.add('page-enter-active');
            window.observeElements();
        });
        mutationObserver.observe(pageContent, { childList: true, subtree: false });
    }

    // 3. KPI COUNTER ANIMATION (Generic MutationObserver)
    const kpiObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    // Check if node is a text node inside a kpi-card-value
                    let el = node.nodeType === 3 ? node.parentElement : node;
                    if (el && el.classList && el.classList.contains('kpi-card-value') && !el.dataset.animating) {
                        const text = el.innerText.trim();
                        if (text === "—" || text === "") return;
                        
                        el.dataset.animating = "true";
                        const numMatch = text.match(/[\d,.]+/);
                        if (!numMatch) { el.dataset.animating = ""; return; }
                        
                        const numStr = numMatch[0];
                        const prefix = text.split(numStr)[0];
                        const suffix = text.split(numStr)[1];
                        const targetValue = parseFloat(numStr.replace(/,/g, ''));
                        
                        let startVal = 0;
                        let duration = 1200;
                        let startTimestamp = null;
                        
                        const step = (timestamp) => {
                            if (!startTimestamp) startTimestamp = timestamp;
                            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                            const easeProgress = 1 - Math.pow(1 - progress, 4); // easeOutQuart
                            const current = (easeProgress * (targetValue - startVal) + startVal);
                            
                            let displayVal;
                            if (numStr.includes(".")) {
                                const decs = numStr.split(".")[1].length;
                                displayVal = current.toFixed(decs);
                            } else {
                                displayVal = Math.round(current).toLocaleString();
                            }
                            
                            el.innerText = `${prefix}${displayVal}${suffix}`;
                            
                            if (progress < 1) {
                                window.requestAnimationFrame(step);
                            } else {
                                el.innerText = text;
                                setTimeout(() => { el.dataset.animating = ""; }, 50);
                            }
                        };
                        window.requestAnimationFrame(step);
                    }
                });
            }
        });
    });
    kpiObserver.observe(document.body, { childList: true, subtree: true });

    // 4. MOUSE PARALLAX EFFECT
    document.addEventListener('mousemove', (e) => {
        const bg = document.querySelector('.bg-image');
        if (!bg) return;
        const xOffset = (e.clientX / window.innerWidth - 0.5) * -30;
        const yOffset = (e.clientY / window.innerHeight - 0.5) * -30;
        bg.style.transform = `translateZ(-100px) scale(1.1) translate(${xOffset}px, ${yOffset}px)`;
    });

    // 5. CURSOR-REACTIVE LIGHTING
    const cursorGlow = document.createElement('div');
    cursorGlow.id = 'cursor-glow';
    document.body.appendChild(cursorGlow);

    document.addEventListener('mousemove', (e) => {
        cursorGlow.style.opacity = 1;
        cursorGlow.style.left = e.clientX + 'px';
        cursorGlow.style.top = e.clientY + 'px';
    });
    
    document.addEventListener('mouseleave', () => {
        cursorGlow.style.opacity = 0;
    });
});
