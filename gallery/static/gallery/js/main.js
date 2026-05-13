"use strict";

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

    // Force Instagram embeds to load on mobile
    const loadInstagramEmbeds = () => {
        if (window.instgrm && window.instgrm.Embeds) {
            window.instgrm.Embeds.process();
        }
    };

    // Try immediately
    loadInstagramEmbeds();

    // Retry after a short delay in case script hasn't loaded yet
    setTimeout(loadInstagramEmbeds, 1000);

    // Retry after 3 seconds
    setTimeout(loadInstagramEmbeds, 3000);

    // Retry after page load
    window.addEventListener('load', loadInstagramEmbeds);
});