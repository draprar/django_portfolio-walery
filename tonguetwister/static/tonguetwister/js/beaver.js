document.addEventListener('DOMContentLoaded', () => {
    const userAuthenticated = document.body.getAttribute('data-user-authenticated') === 'true';

    if (!userAuthenticated) {
        // Get elements for beaver tutorial
        const beaverImg = document.getElementById('beaver-img');
        const speechBubble = document.getElementById('beaver-speech-bubble');
        const closeBubble = document.getElementById('close-speech-bubble');
        const beaverText = document.getElementById('beaver-text');
        const screenDim = document.getElementById('screen-dim');
        const beaverOptions = document.createElement('div'); // Create options div for buttons
        let currentStep = 0; // Track current tutorial step

        beaverImg.onload = () => {
            speechBubble.style.display = 'block'; // Show speech bubble after image loads
        };

        // Resize beaver image
        beaverImg.style.width = `${beaverImg.offsetWidth * 1.2}px`;
        beaverImg.style.height = `${beaverImg.offsetHeight * 1.2}px`;

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
            const beaverRect = beaverImg.getBoundingClientRect();
            speechBubble.style.left = `${beaverRect.right + 20}px`;
            speechBubble.style.top = `${beaverRect.top - speechBubble.offsetHeight - 20}px`;
        };

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
                beaverImg.style.left = `${x}px`; // Update image X position
                beaverImg.style.top = `${y}px`; // Update image Y position
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

        // Initial positioning
        const viewportWidth = window.innerWidth;
        beaverImg.style.left = `${viewportWidth / 4 - beaverImg.offsetWidth / 2}px`;
        beaverImg.style.top = `${window.innerHeight / 1.5 - beaverImg.offsetHeight / 2}px`;

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
            polishBeaverImg.style.width = (polishBeaverImg.offsetWidth * 1.2) + 'px';
            polishBeaverImg.style.height = (polishBeaverImg.offsetHeight * 1.2) + 'px';
            randomizePosition();
            showPolishBeaver.initialized = true;
        }

        // Function to randomize position of the Polish Beaver
        function randomizePosition() {
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            const imgWidth = polishBeaverImg.offsetWidth;
            const imgHeight = polishBeaverImg.offsetHeight;

            const marginWidth = 0.1 * viewportWidth;
            const marginHeight = 0.1 * viewportHeight;

            // Randomly position the image within margins
            const randomLeft = marginWidth + Math.random() * (viewportWidth - imgWidth - 2 * marginWidth);
            const randomTop = marginHeight + Math.random() * (viewportHeight - imgHeight - 2 * marginHeight);

            polishBeaverImg.style.left = randomLeft + 'px';
            polishBeaverImg.style.top = randomTop + 'px';

            updatePolishSpeechBubblePosition(); // Adjust speech bubble position
        }

        // Update speech bubble position relative to the beaver
        function updatePolishSpeechBubblePosition() {
            var polishBeaverRect = polishBeaverImg.getBoundingClientRect();
            polishSpeechBubble.style.left = polishBeaverRect.right + 'px';
            polishSpeechBubble.style.top = (polishBeaverRect.top - polishSpeechBubble.offsetHeight - 20) + 'px';
        }

        // Fetch new Old Polish record and display it in the speech bubble
        function fetchNewRecord() {
            fetch(`/load-more-old-polish/`)
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
                polishBeaverImg.style.left = x + 'px';
                polishBeaverImg.style.top = y + 'px';
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
    }
});
