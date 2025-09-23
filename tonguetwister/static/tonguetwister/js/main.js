document.addEventListener('DOMContentLoaded', function() {
    // Initialize Swiper with navigation, pagination, and touch support.
    var mainSwiper = new Swiper(".mySwiper", {
        on: {
            init: function () {
                //calculateSlideHeights();
            },
            slideChange: function () {
                //calculateSlideHeights();
            }
        },
        pagination: {
            el: ".swiper-pagination",
            type: "progressbar",
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev'
        },
        simulateTouch: true,
        allowTouchMove: true,
    });

    /**
     * Calculate and set heights for each slide dynamically.
     * Adjusts the swiper container height based on the current active slide.
     */
    function calculateSlideHeights() {
        const slides = document.querySelectorAll('.swiper-slide');
        slides.forEach((slide) => {
            slide.style.height = 'auto'; // Reset slide height
            const slideHeight = slide.scrollHeight; // Get natural height
            slide.style.height = slideHeight + 'px'; // Set calculated height
        });

        // Adjust the container height to match the active slide
        const activeSlide = document.querySelector('.mySwiper .swiper-slide-active');
        if (activeSlide) {
            document.querySelector('.mySwiper').style.height = activeSlide.scrollHeight + 'px';
        }
    }

    /**
     * List of button selectors that trigger dynamic content loading or changes.
     * Once clicked, the slide heights will be recalculated.
     */
    const dynamicContentTriggers = [
        '.toggle-articulator-btn',
        '#load-more-btn',
        '#mirror-btn',
        '#mirror-btn-articulators',
        '#mirror-btn-exercises',
        '#mirror-btn-twisters',
        '#mirror-btn-bonuses',
        '.toggle-exercise-btn',
        '#load-more-exercises-btn',
        '.toggle-twister-btn',
        '#load-more-twisters-btn',
        '#load-more-trivia-btn',
        '#load-more-facts-btn'
    ];

    // Attach click event listeners to each dynamic content trigger
    dynamicContentTriggers.forEach(function(selector) {
        document.querySelectorAll(selector).forEach(function(button) {
            button.addEventListener('click', function() {
                setTimeout(calculateSlideHeights, 100);
            });
        });
    });

    /**
     * List of elements to observe for style changes.
     * The MutationObserver will monitor changes in the 'style' attribute.
     * When elements become visible, it triggers recalculating slide heights.
     */
    const elementsToObserve = [
        '#video-container-articulators',
        '#video-container-twisters',
        '#video-container-exercises',
        '#video-container-bonuses',
        '#video-container',
        '#card-articulator',
        '#card-exercises',
        '#card-twister',
        '#trivia-container',
        '#facts-container',
        '#congratulations-modal'
    ];

    /**
     * Observe style changes to trigger recalculating heights.
     * This uses a MutationObserver to detect attribute changes on selected elements.
     */
    elementsToObserve.forEach(function(selector) {
        const element = document.querySelector(selector);
        if (element) {
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.attributeName === 'style' && element.style.display !== 'none') {
                        setTimeout(calculateSlideHeights, 100);
                    }
                });
            });
            observer.observe(element, { attributes: true });
        }
    });

    // Recalculate slide heights after any custom 'ajaxContentLoaded' event.
    document.addEventListener('ajaxContentLoaded', function() {
        setTimeout(calculateSlideHeights, 100);
    });

    // Attach click event listeners to all buttons to recalculate slide heights after interaction.
    document.querySelectorAll('button').forEach(function(button) {
        button.addEventListener('click', function() {
            setTimeout(calculateSlideHeights, 100);
        });
    });

    // Initial calculation of slide heights when the page loads.
    calculateSlideHeights();
});
