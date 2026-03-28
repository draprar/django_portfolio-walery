document.addEventListener('DOMContentLoaded', () => {
    const userAuthenticated = document.body.getAttribute('data-user-authenticated') === 'true';
    const BUBBLE_GAP = 20;
    const SAFE_MARGIN = 8;
    const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

    const fitBubbleToViewport = (bubbleElement) => {
        const maxBubbleWidth = Math.max(180, window.innerWidth - (SAFE_MARGIN * 2));
        bubbleElement.style.maxWidth = `${maxBubbleWidth}px`;
    };

    if (!userAuthenticated) {
        // Get elements for beaver tutorial
        const beaverImg = document.getElementById('beaver-img');
        const speechBubble = document.getElementById('beaver-speech-bubble');
        const closeBubble = document.getElementById('close-speech-bubble');
        const beaverText = document.getElementById('beaver-text');
        const screenDim = document.getElementById('screen-dim');
        const beaverOptions = document.createElement('div'); // Create options div for buttons
        let currentStep = 0; // Track current tutorial step

        let tutorialBeaverSized = false;

        const initializeTutorialBeaver = () => {
            // Handle cached image and avoid repeated 1.2x scaling.
            if (!tutorialBeaverSized) {
                beaverImg.style.width = `${beaverImg.offsetWidth * 1.2}px`;
                beaverImg.style.height = `${beaverImg.offsetHeight * 1.2}px`;
                tutorialBeaverSized = true;
            }

            const vw = window.innerWidth;
            beaverImg.style.left = `${vw / 4 - beaverImg.offsetWidth / 2}px`;
            beaverImg.style.top = `${window.innerHeight / 1.5 - beaverImg.offsetHeight / 2}px`;

            updateSpeechBubblePosition();
            speechBubble.style.display = 'block';
        };

        // Dim the screen for focus
        screenDim.style.display = 'block';

        // Define tutorial steps with selector and text
        const steps = [
            { selector: ['#login', '#login-mobile'], text: 'Tu możesz się zarejestrować, aby stworzyć swój profil i spersonalizować swoją naukę 😎' },
            { selector: ['#contact', '#contact-mobile'], text: 'Tu możesz się z nami skontaktować, a ja zamienię się w chatbota 🧐' },
            { selector: ['#mic-btn', '#mic-btn-mobile'], text: 'Jeżeli klikniesz tu - rozpoczniesz nagrywanie swojego głosu 🎤' },
            { selector: '#swiper-button-next', text: 'Aby przejść do następnego ćwiczenia, przesuń palcem lub przeciągnij myszką ➡️' },
            { selector: '#mirror-btn-exercises', text: 'Dzięki tej opcji, możesz odpalić lusterko (kamerę skierowaną na usta) 🎥' },
            { selector: '#load-more-exercises-btn', text: 'A tutaj wygenerujesz nowe ćwiczenie do praktyki 💡' },
            { selector: 'body', text: 'Zaczynamy? Zamknij tę chmurkę, aby przejść do rozgrzewki 🚀', final: true }
        ];

        // Get the target element based on step and screen size (mobile vs desktop)
        const getTargetElement = (step) => {
            return step <= 2 ? document.querySelector(window.innerWidth <= 991 ? steps[step].selector[1] : steps[step].selector[0]) : document.querySelector(steps[step].selector);
        };

        // Move to the next tutorial step
        function moveToStep(step) {
            if (step >= steps.length) return; // Exit if beyond last step

            const stepInfo = steps[step];
            const targetElement = getTargetElement(step); // Get the target element for the current step

            if (!targetElement) {
                console.error('Target element not found for step:', step); // Error if no target element found
                return;
            }

            // Position the beaver image based on viewport size
            const targetRect = targetElement.getBoundingClientRect();
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;

            beaverImg.style.left = `${viewportWidth / 4 - beaverImg.offsetWidth / 2}px`;
            beaverImg.style.top = `${viewportHeight / 1.5 - beaverImg.offsetHeight / 2}px`;

            updateSpeechBubblePosition(); // Update the speech bubble position
            beaverText.innerHTML = stepInfo.text; // Set tutorial text for the step

            beaverOptions.innerHTML = ''; // Clear previous buttons
            const nextButton = document.createElement('button'); // Create next button
            nextButton.className = 'btn btn-dark';

            // If it's the final step
            if (stepInfo.final) {
                nextButton.innerText = 'ZAMKNIJ'; // Change button text to 'CLOSE'
                nextButton.addEventListener('click', function () {
                    var swiperInstance = document.querySelector('.mySwiper').swiper;
                    if (swiperInstance) {
                        swiperInstance.slideTo(0, 500); // Slide to first swiper slide

                        swiperInstance.on('slideChangeTransitionEnd', function () {
                            closeTutorialAndShowPolishBeaver(); // Close tutorial after sliding
                        });
                    } else {
                        closeTutorialAndShowPolishBeaver(); // Close if no swiper found
                    }
                });
            } else {
                // For intermediate steps
                nextButton.innerText = 'DALEJ'; // Set button text to 'NEXT'
                nextButton.addEventListener('click', function () {
                    var slideArrowContainer = document.getElementById('slide-arrow-container');

                    // Handle step 2 - show arrow container
                    if (step === 2 && slideArrowContainer) {
                        if (window.innerWidth <= 992) {
                            slideArrowContainer.style.display = 'block';
                        }
                        moveToStep(step + 1); // Move to next step

                    // Handle step 3 - hide arrow container and move swiper
                    } else if (step === 3 && slideArrowContainer) {
                        slideArrowContainer.style.display = 'none';
                        var swiperInstance = document.querySelector('.mySwiper').swiper;
                        if (swiperInstance) {
                            swiperInstance.slideTo(2, 500); // Slide to swiper slide 2

                            swiperInstance.on('slideChangeTransitionEnd', function () {
                                moveToStep(step + 1); // Move to next step after swiper transition
                            });
                        } else {
                            moveToStep(step + 1); // Move to next step if no swiper
                        }
                    } else {
                        moveToStep(step + 1); // Default next step
                    }
                });
            }

            beaverOptions.appendChild(nextButton); // Add next button to beaver options
            speechBubble.appendChild(beaverOptions); // Show the next button in the speech bubble
            speechBubble.style.display = 'block'; // Display the speech bubble

            removePulseEffectFromAllSteps(); // Remove highlight effect from previous steps

            if (targetElement) {
                targetElement.classList.add('highlight'); // Highlight the current target element
            }
            updateSpeechBubblePosition(); // Update the speech bubble position
        }

        // Remove highlight effect from all steps
        const removePulseEffectFromAllSteps = () => {
            steps.forEach((step, index) => {
                const target = getTargetElement(index);
                target?.classList.remove('highlight'); // Remove highlight class from target
            });
        };

        // Close tutorial and show the Polish Beaver
        const closeTutorialAndShowPolishBeaver = () => {
            closeTutorial(); // Close the tutorial
            showPolishBeaver(); // Show the Polish Beaver after closing
        };

        // Close the tutorial
        const closeTutorial = () => {
            speechBubble.style.display = 'none'; // Hide the speech bubble
            screenDim.style.display = 'none'; // Remove screen dimming effect
            beaverImg.style.display = 'none'; // Hide the beaver image
            removePulseEffectFromAllSteps(); // Remove highlight effect
        };

        // Start the tutorial
        const startTutorial = () => {
            document.getElementById('beaver-yes').style.display = 'none'; // Hide 'yes' button
            document.getElementById('beaver-no').style.display = 'none'; // Hide 'no' button

            screenDim.style.display = 'block'; // Show screen dimming effect
            moveToStep(0); // Start at the first tutorial step
            updateSpeechBubblePosition(); // Update speech bubble position
        };

        // Update the speech bubble position relative to the beaver image
        const updateSpeechBubblePosition = () => {
            fitBubbleToViewport(speechBubble);

            const bubbleWidth = speechBubble.offsetWidth;
            const bubbleHeight = speechBubble.offsetHeight;
            const beaverHeight = beaverImg.offsetHeight;

            // Keep enough vertical room so bubble always stays above the beaver.
            const maxTop = Math.max(SAFE_MARGIN, window.innerHeight - beaverHeight - SAFE_MARGIN);
            const requiredTop = Math.min(bubbleHeight + BUBBLE_GAP + SAFE_MARGIN, maxTop);
            const currentTop = parseFloat(beaverImg.style.top) || beaverImg.getBoundingClientRect().top;
            if (currentTop < requiredTop) {
                beaverImg.style.top = `${requiredTop}px`;
            }

            const beaverRect = beaverImg.getBoundingClientRect();
            const desiredLeft = beaverRect.right + BUBBLE_GAP;
            const maxLeft = Math.max(SAFE_MARGIN, window.innerWidth - bubbleWidth - SAFE_MARGIN);

            speechBubble.style.left = `${clamp(desiredLeft, SAFE_MARGIN, maxLeft)}px`;
            speechBubble.style.top = `${beaverRect.top - bubbleHeight - BUBBLE_GAP}px`;
        };

        // Run image init only after helpers are initialized (avoid TDZ crash on cached images).
        if (beaverImg.complete) {
            initializeTutorialBeaver();
        } else {
            beaverImg.onload = initializeTutorialBeaver;
        }

        // Drag functionality for beaver image
        let isDragging = false, startX, startY, offsetX, offsetY;

        // Start dragging the beaver image
        const startDrag = (e) => {
            startX = e.clientX || e.touches[0].clientX;
            startY = e.clientY || e.touches[0].clientY;
            offsetX = startX - beaverImg.getBoundingClientRect().left;
            offsetY = startY - beaverImg.getBoundingClientRect().top;
            isDragging = true;
            e.preventDefault(); // Prevent default drag behavior
        };

        // Drag the beaver image
        const doDrag = (e) => {
            if (isDragging) {
                const x = (e.clientX || e.touches[0].clientX) - offsetX;
                const y = (e.clientY || e.touches[0].clientY) - offsetY;

                const minX = SAFE_MARGIN;
                const maxX = Math.max(minX, window.innerWidth - beaverImg.offsetWidth - SAFE_MARGIN);
                const desiredMinY = speechBubble.offsetHeight + BUBBLE_GAP + SAFE_MARGIN;
                const viewportMaxY = window.innerHeight - beaverImg.offsetHeight - SAFE_MARGIN;
                const maxY = Math.max(SAFE_MARGIN, viewportMaxY);
                const minY = Math.min(desiredMinY, maxY);

                beaverImg.style.left = `${clamp(x, minX, maxX)}px`; // Update image X position
                beaverImg.style.top = `${clamp(y, minY, maxY)}px`; // Keep room for bubble above
                updateSpeechBubblePosition(); // Update speech bubble position
            }
        };

        // Stop dragging the beaver image
        const stopDrag = () => isDragging = false;

        // Add event listeners for dragging the beaver image
        beaverImg.addEventListener('mousedown', startDrag);
        document.addEventListener('mousemove', doDrag);
        document.addEventListener('mouseup', stopDrag);
        beaverImg.addEventListener('touchstart', startDrag);
        document.addEventListener('touchmove', doDrag);
        document.addEventListener('touchend', stopDrag);

        // Start tutorial
        document.getElementById('beaver-yes').addEventListener('click', startTutorial);
        document.getElementById('beaver-no').addEventListener('click', closeTutorialAndShowPolishBeaver);
        closeBubble.addEventListener('click', closeTutorialAndShowPolishBeaver);

        window.addEventListener('resize', updateSpeechBubblePosition);
        window.addEventListener('orientationchange', updateSpeechBubblePosition);

        updateSpeechBubblePosition();
    } else {
        showPolishBeaver();
    }

    // --- POLISH BEAVER ---
    function showPolishBeaver() {
        // Select Tutorial Beaver elements
        const polishBeaverContainer = document.getElementById('polish-beaver-container');
        const speechBubble = document.getElementById('beaver-speech-bubble');
        const beaverImg = document.getElementById('beaver-img');
        const closeBubble = document.getElementById('close-speech-bubble');
        const beaverText = document.getElementById('beaver-text');

        // Hide original beaver elements
        polishBeaverContainer.style.display = 'block';
        speechBubble.style.display = 'none';
        beaverImg.style.display = 'none';
        closeBubble.style.display = 'none';
        beaverText.style.display = 'none';

        // Select Polish Beaver elements
        const polishBeaverImg = document.getElementById('polish-beaver-img');
        const polishSpeechBubble = document.getElementById('polish-beaver-speech-bubble');
        const polishCloseBubble = document.getElementById('polish-close-speech-bubble');
        const polishBeaverText = document.getElementById('polish-beaver-text');

        let offset = 0;  // Track database offset for fetching new records
        let isDragging = false, startX, startY, offsetX, offsetY;
        let moved = false;  // Track if beaver was moved
        let bubbleClosedManually = false;  // Track manual bubble close state

        // Initialize the beaver size and position once
        if (typeof showPolishBeaver.initialized === 'undefined') {
        showPolishBeaver.initialized = false;
        }

        // If not initialized, enlarge beaver image and randomize its position
        if (!showPolishBeaver.initialized) {
            if (polishBeaverImg.complete) {
                polishBeaverImg.style.width = (polishBeaverImg.offsetWidth * 1.2) + 'px';
                polishBeaverImg.style.height = (polishBeaverImg.offsetHeight * 1.2) + 'px';
                randomizePosition();
            } else {
                polishBeaverImg.onload = () => {
                    polishBeaverImg.style.width = (polishBeaverImg.offsetWidth * 1.2) + 'px';
                    polishBeaverImg.style.height = (polishBeaverImg.offsetHeight * 1.2) + 'px';
                    randomizePosition();
                };
            }
            showPolishBeaver.initialized = true;
        }

        // Function to randomize position of the Polish Beaver
        function randomizePosition() {
            fitBubbleToViewport(polishSpeechBubble);

            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            const imgWidth = polishBeaverImg.offsetWidth;
            const imgHeight = polishBeaverImg.offsetHeight;
            const bubbleHeight = polishSpeechBubble.offsetHeight;

            const marginWidth = 0.1 * viewportWidth;
            const marginHeight = 0.1 * viewportHeight;

            // Randomly position the image within margins
            const minLeft = marginWidth;
            const maxLeft = Math.max(minLeft, viewportWidth - imgWidth - marginWidth);
            const desiredMinTop = Math.max(marginHeight, bubbleHeight + BUBBLE_GAP + SAFE_MARGIN);
            const viewportMaxTop = viewportHeight - imgHeight - marginHeight;
            const maxTop = Math.max(SAFE_MARGIN, viewportMaxTop);
            const minTop = Math.min(desiredMinTop, maxTop);

            const randomLeft = minLeft + Math.random() * (maxLeft - minLeft);
            const randomTop = minTop + Math.random() * (maxTop - minTop);

            polishBeaverImg.style.left = randomLeft + 'px';
            polishBeaverImg.style.top = randomTop + 'px';

            updatePolishSpeechBubblePosition(); // Adjust speech bubble position
        }

        // Update speech bubble position relative to the beaver
        function updatePolishSpeechBubblePosition() {
            fitBubbleToViewport(polishSpeechBubble);

            var bubbleWidth = polishSpeechBubble.offsetWidth;
            var bubbleHeight = polishSpeechBubble.offsetHeight;
            var beaverHeight = polishBeaverImg.offsetHeight;

            // Keep enough vertical room so bubble always stays above the beaver.
            var maxTop = Math.max(SAFE_MARGIN, window.innerHeight - beaverHeight - SAFE_MARGIN);
            var requiredTop = Math.min(bubbleHeight + BUBBLE_GAP + SAFE_MARGIN, maxTop);
            var currentTop = parseFloat(polishBeaverImg.style.top) || polishBeaverImg.getBoundingClientRect().top;
            if (currentTop < requiredTop) {
                polishBeaverImg.style.top = requiredTop + 'px';
            }

            var polishBeaverRect = polishBeaverImg.getBoundingClientRect();
            var desiredLeft = polishBeaverRect.right + BUBBLE_GAP;
            var maxLeft = Math.max(SAFE_MARGIN, window.innerWidth - bubbleWidth - SAFE_MARGIN);

            polishSpeechBubble.style.left = clamp(desiredLeft, SAFE_MARGIN, maxLeft) + 'px';
            polishSpeechBubble.style.top = (polishBeaverRect.top - bubbleHeight - BUBBLE_GAP) + 'px';
        }

        // Fetch new Old Polish record and display it in the speech bubble
        function fetchNewRecord() {
            fetch(`/tonguetwister/load-more-old-polish/`)
                .then(response => response.json())
                .then(data => {
                    if (data.length > 0) {
                        var record = data[0];
                        polishBeaverText.innerHTML = `Czy wiesz, że staropolskie <strong>${record.old_text}</strong> to dziś <strong>${record.new_text}</strong>?`;
                    } else {
                        polishBeaverText.innerHTML = 'Brawo! Baza danych wyczyszczona 😲';
                    }
                    polishSpeechBubble.style.display = 'block';
                    updatePolishSpeechBubblePosition();
                })
                .catch(error => {
                    polishBeaverText.innerHTML = 'Error loading data.';
                    polishSpeechBubble.style.display = 'block';
                });
        }

        // Dragging start
        function startDrag(e) {
            startX = e.clientX || e.touches[0].clientX;
            startY = e.clientY || e.touches[0].clientY;
            offsetX = startX - polishBeaverImg.getBoundingClientRect().left;
            offsetY = startY - polishBeaverImg.getBoundingClientRect().top;
            isDragging = true;
            moved = false;
            e.preventDefault();
        }

        // Dragging
        function doDrag(e) {
            if (isDragging) {
                var x = (e.clientX || e.touches[0].clientX) - offsetX;
                var y = (e.clientY || e.touches[0].clientY) - offsetY;

                var minX = SAFE_MARGIN;
                var maxX = Math.max(minX, window.innerWidth - polishBeaverImg.offsetWidth - SAFE_MARGIN);
                var desiredMinY = polishSpeechBubble.offsetHeight + BUBBLE_GAP + SAFE_MARGIN;
                var viewportMaxY = window.innerHeight - polishBeaverImg.offsetHeight - SAFE_MARGIN;
                var maxY = Math.max(SAFE_MARGIN, viewportMaxY);
                var minY = Math.min(desiredMinY, maxY);

                polishBeaverImg.style.left = clamp(x, minX, maxX) + 'px';
                polishBeaverImg.style.top = clamp(y, minY, maxY) + 'px';
                moved = true; // Mark that the beaver was moved
                updatePolishSpeechBubblePosition(); // Adjust speech bubble position
            }
        }

        // Stop dragging
        function stopDrag() {
            if (isDragging) {
                if (!moved && !bubbleClosedManually) {
                    fetchNewRecord(); // Fetch new record if not moved
                }
                isDragging = false; // Disable dragging state
            }
        }

        // Dragging event listeners for Polish Beaver
        polishBeaverImg.addEventListener('mousedown', startDrag);  // Mouse drag start
        document.addEventListener('mousemove', doDrag);  // Mouse drag move
        document.addEventListener('mouseup', stopDrag);  // Mouse drag stop
        polishBeaverImg.addEventListener('touchstart', startDrag);  // Touch drag start
        document.addEventListener('touchmove', doDrag);  // Touch drag move
        document.addEventListener('touchend', stopDrag);  // Touch drag stop

        // Close the speech bubble and hide beaver image
        polishCloseBubble.addEventListener('click', function () {
            polishSpeechBubble.style.display = 'none';
            polishBeaverImg.style.display = 'none';
            bubbleClosedManually = true;  // Track manual close
        });

        // Re-fetch record if beaver clicked after manually closing bubble
        polishBeaverImg.addEventListener('click', function () {
            if (bubbleClosedManually && !moved) {
                fetchNewRecord();
                bubbleClosedManually = false;  // Reset manual close flag
            }
        });

        if (typeof showPolishBeaver.viewportHandler === 'function') {
            window.removeEventListener('resize', showPolishBeaver.viewportHandler);
            window.removeEventListener('orientationchange', showPolishBeaver.viewportHandler);
        }

        showPolishBeaver.viewportHandler = function () {
            updatePolishSpeechBubblePosition();
        };

        window.addEventListener('resize', showPolishBeaver.viewportHandler);
        window.addEventListener('orientationchange', showPolishBeaver.viewportHandler);
    }
});