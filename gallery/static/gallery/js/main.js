document.addEventListener("DOMContentLoaded", () => {
    const fadeInElements = document.querySelectorAll(".fade-in");

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
            }
        });
    }, { threshold: 0.1, rootMargin: "0px 0px -30px 0px" });

    fadeInElements.forEach(element => observer.observe(element));

    // Smooth scrolling for navbar links
    const navbarLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navbarLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });

    // Blur-up effect for gallery images
    document.querySelectorAll('.gallery-item img').forEach(img => {
        if (img.complete) {
            img.classList.add('loaded');
        } else {
            img.addEventListener('load', () => img.classList.add('loaded'));
        }
    });

    // ── Instagram: lazy load + fix width/height issues ──────────────────────
    setupInstagramEmbeds();
});

function setupInstagramEmbeds() {
    const section = document.querySelector('.instagram-section');
    if (!section) return;

    const items = document.querySelectorAll('.instagram-item');
    if (!items.length) return;

    // 1. Inject placeholders and hide blockquotes until we're ready
    items.forEach(item => {
        const bq = item.querySelector('blockquote');
        if (!bq) return;
        bq.style.display = 'none';

        const placeholder = document.createElement('div');
        placeholder.className = 'ig-placeholder';
        placeholder.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
                <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
                <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
            </svg>
            <span>Ładowanie posta&hellip;</span>
        `;
        item.appendChild(placeholder);
    });

    let embedsLoaded = false;

    const loadEmbeds = () => {
        if (embedsLoaded) return;
        embedsLoaded = true;

        items.forEach(item => {
            const bq = item.querySelector('blockquote');
            if (bq) bq.style.display = '';
        });

        const script = document.createElement('script');
        script.src = 'https://www.instagram.com/embed.js';
        script.async = true;
        script.onload = () => {
            if (window.instgrm) {
                window.instgrm.Embeds.process();
            }
            // Wywołujemy fixy kilkukrotnie, bo IG renderuje się "na raty"
            scheduleWidthFixes();
        };
        // Obsługa błędu ładowania skryptu (np. brak połączenia)
        script.onerror = () => {
            console.error("Nie udało się załadować skryptu Instagrama.");
            schedulePlaceholderCleanup();
        };
        document.body.appendChild(script);

        // Agresywny MutationObserver
        const mo = new MutationObserver(() => {
            section.querySelectorAll('iframe, .instagram-media').forEach(el => {
                el.style.setProperty('min-width', 'unset', 'important');
                el.style.setProperty('width', '100%', 'important');
                el.style.setProperty('max-width', '100%', 'important');
            });
        });
        mo.observe(section, { subtree: true, attributes: true, attributeFilter: ['style'] });
    };

    // 4. Trigger load only when the section approaches the viewport
    const sectionObserver = new IntersectionObserver(([entry]) => {
        if (entry.isIntersecting) {
            loadEmbeds();
            sectionObserver.disconnect();
        }
    }, { rootMargin: '500px' });

    sectionObserver.observe(section);

    function scheduleWidthFixes() {
        const fix = () => {
            const frames = document.querySelectorAll('.instagram-item iframe');
            frames.forEach(frame => {
                // Instagram często dodaje min-width: 326px co rozpycha telefon
                frame.style.setProperty('min-width', 'unset', 'important');
                frame.style.setProperty('width', '100%', 'important');
                frame.style.setProperty('max-width', '100%', 'important');

                // Jeśli post jest pusty (błąd połączenia), ustawiamy mu wysokość
                if (frame.offsetHeight < 100) {
                    frame.style.setProperty('height', '500px', 'important');
                }
            });
        };

        // Wykonaj fixy w kilku interwałach, bo IG renderuje się powoli
        [500, 1500, 3000, 6000].forEach(delay => setTimeout(fix, delay));
    }

    // Skróć czas wyświetlania "Ładowanie posta", żeby nie wisiało w nieskończoność
    function schedulePlaceholderCleanup() {
        setTimeout(() => {
            document.querySelectorAll('.ig-placeholder').forEach(p => {
                p.style.opacity = '0';
                setTimeout(() => p.remove(), 400);
            });
        }, 2000); // 2 sekundy to max, potem usuwamy niezależnie od stanu
    }
}