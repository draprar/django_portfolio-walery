document.addEventListener('DOMContentLoaded', function() {
    // Get the CSRF token required for making POST requests
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Handles the click event for toggling the exercise button
    function handleToggleButtonClick(event) {
        const button = event.target.closest('.toggle-articulator-btn');  // Find the clicked button
        if (!button || button.disabled) return; // Exit if button is not found or disabled

        const articulatorId = button.dataset.id;  // Get the ID of the articulator
        const action = button.textContent.trim();  // Get the current button action (add or already added)
        button.disabled = true;  // Disable the button to prevent multiple clicks

        if (action === 'Dodaj do powtórek') {
            // Send a POST request to add the articulator to repetitions
            fetch(`/tonguetwister/add-articulator/${articulatorId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,  // Include CSRF token for security
                    'Content-Type': 'application/json'
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);  // Handle errors
                }
                return response.json(); // Parse the response as JSON
            })
            .then(data => {
                button.disabled = false; // Re-enable the button after the request
                if (data.status === 'Articulator added') {
                    // Update button state to show the articulator has been added to repetitions
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

    // Adds a new articulator to the DOM and handles the display for authenticated users
    function addArticulatorToDOM(articulator, isAuthenticated) {
        if (document.getElementById(`articulator-${articulator.id}`)) {
            return; // Prevent adding duplicates
        }

        // Create a container for the articulator
        const articulatorContainer = document.createElement('div');
        articulatorContainer.id = `articulators-container-${articulator.id}`;

        // Create the articulator element and set its content
        const articulatorDiv = document.createElement('div');
        articulatorDiv.classList.add('articulator', 'col-md-16', 'fs-4', 'bg-light', 'bg-gradient', 'bg-gradient', 'text-center', 'shadow-sm', 'p-3', 'my-3', 'rounded','border');
        articulatorDiv.textContent = articulator.text;
        articulatorDiv.id = `articulator-${articulator.id}`;

        articulatorContainer.appendChild(articulatorDiv); // Append articulator to the container

        // If the user is authenticated, add the toggle button
        if (isAuthenticated) {
            const button = document.createElement('button'); // Create toggle button for authenticated users
            button.classList.add('btn', 'toggle-articulator-btn');
            button.dataset.id = articulator.id;  // Assign articulator ID to the button
            button.textContent = articulator.is_added ? 'W powtórkach 😄' : 'Dodaj do powtórek'; // Set initial button text
            button.classList.add(articulator.is_added ? 'btn-secondary' : 'btn-success'); // Set initial button style
            button.disabled = articulator.is_added; // Disable button if articulator is already added

            button.addEventListener('click', handleToggleButtonClick); // Attach the click handler

            articulatorContainer.appendChild(button); // Append button to the container
        }

        // Append the entire container to the articulators section
        document.getElementById('articulators-container').appendChild(articulatorContainer);  // Append container to main DOM
    }

    // Event listener to delegate toggle button clicks within the articulators container
    const articulatorsContainer = document.getElementById('articulators-container');
    if (articulatorsContainer) {
        articulatorsContainer.addEventListener('click', function(event) {
            if (event.target.matches('.toggle-articulator-btn')) {
                handleToggleButtonClick(event); // Handle button click if it matches the class
            }
        });
    }

    const loadMoreBtn = document.getElementById('load-more-btn'); // Load more button to fetch additional articulators
    let offset, url;
    if (loadMoreBtn) {
        offset = parseInt(loadMoreBtn.getAttribute('data-offset')); // Get initial offset
        url = loadMoreBtn.getAttribute('data-url'); // Get the URL for fetching more articulators
        const isAuthenticated = loadMoreBtn.getAttribute('data-authenticated') === 'true'; // Check if the user is authenticated

        loadMoreBtn.addEventListener('click', function() {
            fetch(`${url}?offset=${offset}`) // Fetch more articulators using the offset
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`); // Handle errors
                }
                return response.json(); // Parse the response
            })
            .then(data => {
                document.getElementById('articulators-container').innerHTML = ''; // Clear the container

                if (data.length > 0) {
                    data.forEach(articulator => addArticulatorToDOM(articulator, isAuthenticated)); // Add articulators to DOM
                    offset += data.length; // Update the offset
                    loadMoreBtn.setAttribute('data-offset', offset.toString()); // Set new offset
                } else {
                    document.getElementById('card-articulator').style.display = 'block'; // Show success card when no more articulators
                    loadMoreBtn.style.display = 'none';  // Hide the load more button

                    const successSound = document.getElementById('success-sound-articulators');
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
        // Handling deletion of articulators if the "Load More" button is not present
        document.querySelectorAll('.delete-articulator-btn').forEach(function(button) {
            button.addEventListener('click', function() {
                const articulatorId = this.getAttribute('data-id'); // Get the ID of the articulator
                fetch(`/tonguetwister/delete-articulator/${articulatorId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken, // Include CSRF token for security
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => response.json()) // Parse the response as JSON
                .then(data => {
                    if (data.status === 'Articulator deleted') {
                        location.reload(); // Reload the page if articulator is successfully deleted
                    }
                })
                .catch(error => {
                    // Handle errors silently
                });
            });
        });
    }
});
