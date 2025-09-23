document.addEventListener('DOMContentLoaded', function() {
    // Get the CSRF token required for making POST requests
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Handles the click event for toggling the exercise button
    function handleToggleButtonClick(event) {
        const button = event.target.closest('.toggle-twister-btn'); // Find the clicked button
        if (!button || button.disabled) return; // Exit if button is not found or disabled

        const twisterId = button.dataset.id; // Get the ID of the twister
        const action = button.textContent.trim(); // Get the current button action (add or already added)
        button.disabled = true; // Disable the button to prevent multiple clicks

        if (action === 'Dodaj do powtórek') {
            // Send a POST request to add the twister to repetitions
            fetch(`/tonguetwister/add-twister/${twisterId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken, // Include CSRF token for security
                    'Content-Type': 'application/json'
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`); // Handle errors
                }
                return response.json(); // Parse the response as JSON
            })
            .then(data => {
                button.disabled = false; // Re-enable the button after the request
                if (data.status === 'Twister added') {
                    // Update button state to show the twister has been added to repetitions
                    button.disabled = true;
                    button.textContent = 'W powtórkach 😄'; // Change button text
                    button.classList.replace('btn-success', 'btn-secondary'); // Change button style
                }
            })
            .catch(error => {
                button.disabled = false; // Re-enable the button in case of an error
            });
        } else if (action === 'W powtórkach 😄') {
            button.disabled = true; // If already added, keep the button disabled
        }
    }

    // Adds a new twister to the DOM and handles the display for authenticated users
    function addTwisterToDOM(twister, isAuthenticated) {
        if (document.getElementById(`twister-${twister.id}`)) {
            return; // Prevent adding duplicates
        }

        // Create a container for the twister
        const twisterContainer = document.createElement('div');
        twisterContainer.id = `twisters-container-${twister.id}`;

        // Create the twister element and set its content
        const twisterDiv = document.createElement('div');
        twisterDiv.classList.add('twister', 'col-md-16', 'fs-4', 'bg-light', 'bg-gradient', 'bg-gradient', 'text-center', 'shadow-sm', 'p-3', 'my-3', 'rounded','border');
        twisterDiv.textContent = twister.text;
        twisterDiv.id = `twister-${twister.id}`;

        twisterContainer.appendChild(twisterDiv); // Append twister to the container

        // If the user is authenticated, add the toggle button
        if (isAuthenticated) {
            const button = document.createElement('button'); // Create toggle button for authenticated users
            button.classList.add('btn', 'toggle-twister-btn');
            button.dataset.id = twister.id; // Assign twister ID to the button
            button.textContent = twister.is_added ? 'W powtórkach 😄' : 'Dodaj do powtórek'; // Set initial button text
            button.classList.add(twister.is_added ? 'btn-secondary' : 'btn-success'); // Set initial button style
            button.disabled = twister.is_added; // Disable button if twister is already added

            button.addEventListener('click', handleToggleButtonClick); // Attach the click handler

            twisterContainer.appendChild(button); // Append button to the container
        }

        // Append the entire container to the twisters section
        document.getElementById('twisters-container').appendChild(twisterContainer);
    }

    // Event listener to delegate toggle button clicks within the twisters container
    const twistersContainer = document.getElementById('twisters-container');
    if (twistersContainer) {
        twistersContainer.addEventListener('click', function(event) {
            if (event.target.matches('.toggle-twister-btn')) {
                handleToggleButtonClick(event); // Handle button click if it matches the class
            }
        });
    }

    const loadMoreBtn = document.getElementById('load-more-twisters-btn'); // Load more button to fetch additional twisters
    let offset, url;
    if (loadMoreBtn) {
        offset = parseInt(loadMoreBtn.getAttribute('data-offset')); // Get initial offset
        url = loadMoreBtn.getAttribute('data-url'); // Get the URL for fetching more twisters
        const isAuthenticated = loadMoreBtn.getAttribute('data-authenticated') === 'true'; // Check if the user is authenticated

        loadMoreBtn.addEventListener('click', function() {
            fetch(`${url}?offset=${offset}`) // Fetch more twisters using the offset
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`); // Handle errors
                }
                return response.json(); // Parse the response
            })
            .then(data => {
                document.getElementById('twisters-container').innerHTML = ''; // Clear the container

                if (data.length > 0) {
                    data.forEach(twister => addTwisterToDOM(twister, isAuthenticated)); // Add twisters to DOM
                    offset += data.length; // Update the offset
                    loadMoreBtn.setAttribute('data-offset', offset.toString()); // Set new offset
                } else {
                    document.getElementById('card-twister').style.display = 'block'; // Show success card when no more twisters
                    loadMoreBtn.style.display = 'none';

                    const successSound = document.getElementById('success-sound-twisters');
                    successSound.play(); // Play success sound

                    if (navigator.vibrate) {
                        navigator.vibrate(200); // Vibrate if the device supports vibration
                    }
                }
            })
            .catch(error => {
                // Handle errors silently
            });
        });
    } else {
        // Handling deletion of twisters if the "Load More" button is not present
        document.querySelectorAll('.delete-twister-btn').forEach(function(button) {
            button.addEventListener('click', function() {
                const twisterId = this.getAttribute('data-id'); // Get the ID of the twister
                fetch(`/tonguetwister/delete-twister/${twisterId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken, // Include CSRF token for security
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => response.json()) // Parse the response as JSON
                .then(data => {
                    if (data.status === 'Twister deleted') {
                        location.reload(); // Reload the page if twister is successfully deleted
                    }
                })
                .catch(error => {
                    // Handle errors silently
                });
            });
        });
    }
});
