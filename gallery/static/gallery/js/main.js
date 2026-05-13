document.addEventListener("DOMContentLoaded", () => {
    const fadeInElements = document.querySelectorAll(".fade-in");

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");

                // Jeśli to sekcja Instagrama, wymuś ponowne przeliczenie wysokości
                if (entry.target.classList.contains('instagram-section')) {
                    if (window.instgrm) {
                        window.instgrm.Embeds.process();
                    }
                }
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

    // Force Instagram embeds to load on mobile
    const loadInstagramEmbeds = () => {
        if (window.instgrm && window.instgrm.Embeds) {
            window.instgrm.Embeds.process();
        }
    };

    loadInstagramEmbeds();
    setTimeout(loadInstagramEmbeds, 1000);
    setTimeout(loadInstagramEmbeds, 3000);
    window.addEventListener('load', loadInstagramEmbeds);
});