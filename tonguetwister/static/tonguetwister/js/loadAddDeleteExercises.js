document.addEventListener('DOMContentLoaded', function() {
    // Get the CSRF token required for making POST requests
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Handles the click event for toggling the exercise button
    function handleToggleButtonClick(event) {
        const button = event.target.closest('.toggle-exercise-btn'); // Find the clicked button
        if (!button || button.disabled) return; // Exit if button is not found or disabled

        const exerciseId = button.dataset.id; // Get the ID of the exercise
        const action = button.textContent.trim(); // Get the current button action (add or already added)
        button.disabled = true; // Disable the button to prevent multiple clicks

        if (action === 'Dodaj do powtórek') {
            // Send a POST request to add the exercise to repetitions
            fetch(`/tonguetwister/add-exercise/${exerciseId}/`, {
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
                if (data.status === 'Exercise added') {
                    // Update button state to show the exercise has been added to repetitions
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

    // Adds a new exercise to the DOM and handles the display for authenticated users
    function addExerciseToDOM(exercise, isAuthenticated) {
        if (document.getElementById(`exercise-${exercise.id}`)) {
            return; // Prevent adding duplicates
        }

        // Create a container for the exercise
        const exerciseContainer = document.createElement('div');
        exerciseContainer.id = `exercises-container-${exercise.id}`;

        // Create the exercise element and set its content
        const exerciseDiv = document.createElement('div');
        exerciseDiv.classList.add('exercise', 'col-md-16', 'fs-4', 'bg-light', 'bg-gradient', 'bg-gradient', 'text-center', 'shadow-sm', 'p-3', 'my-3', 'rounded','border');
        exerciseDiv.textContent = exercise.text;
        exerciseDiv.id = `exercise-${exercise.id}`;

        exerciseContainer.appendChild(exerciseDiv); // Append exercise to the container

        // If the user is authenticated, add the toggle button
        if (isAuthenticated) {
            const button = document.createElement('button'); // Create toggle button for authenticated users
            button.classList.add('btn', 'toggle-exercise-btn');
            button.dataset.id = exercise.id; // Assign exercise ID to the button
            button.textContent = exercise.is_added ? 'W powtórkach 😄' : 'Dodaj do powtórek'; // Set initial button text
            button.classList.add(exercise.is_added ? 'btn-secondary' : 'btn-success'); // Set initial button style
            button.disabled = exercise.is_added; // Disable button if exercise is already added

            button.addEventListener('click', handleToggleButtonClick); // Attach the click handler

            exerciseContainer.appendChild(button); // Append button to the container
        }

        // Append the entire container to the exercises section
        document.getElementById('exercises-container').appendChild(exerciseContainer);
    }

    // Event listener to delegate toggle button clicks within the exercises container
    const exercisesContainer = document.getElementById('exercises-container');
    if (exercisesContainer) {
        exercisesContainer.addEventListener('click', function(event) {
            if (event.target.matches('.toggle-exercise-btn')) {
                handleToggleButtonClick(event); // Handle button click if it matches the class
            }
        });
    }

    const loadMoreBtn = document.getElementById('load-more-exercises-btn'); // Load more button to fetch additional exercises
    let offset, url;
    if (loadMoreBtn) {
        offset = parseInt(loadMoreBtn.getAttribute('data-offset')); // Get initial offset
        url = loadMoreBtn.getAttribute('data-url'); // Get the URL for fetching more exercises
        const isAuthenticated = loadMoreBtn.getAttribute('data-authenticated') === 'true'; // Check if the user is authenticated

        loadMoreBtn.addEventListener('click', function() {
            fetch(`${url}?offset=${offset}`) // Fetch more exercises using the offset
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`); // Handle errors
                }
                return response.json(); // Parse the response
            })
            .then(data => {
                document.getElementById('exercises-container').innerHTML = ''; // Clear the container

                if (data.length > 0) {
                    data.forEach(exercise => addExerciseToDOM(exercise, isAuthenticated)); // Add exercises to DOM
                    offset += data.length; // Update the offset
                    loadMoreBtn.setAttribute('data-offset', offset.toString()); // Set new offset
                } else {
                    document.getElementById('card-exercises').style.display = 'block'; // Show success card when no more exercises
                    loadMoreBtn.style.display = 'none';

                    const successSound = document.getElementById('success-sound-exercises');
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
        // Handling deletion of exercises if the "Load More" button is not present
        document.querySelectorAll('.delete-exercise-btn').forEach(function(button) {
            button.addEventListener('click', function() {
                const exerciseId = this.getAttribute('data-id'); // Get the ID of the exercise
                fetch(`/tonguetwister/delete-exercise/${exerciseId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken, // Include CSRF token for security
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => response.json()) // Parse the response as JSON
                .then(data => {
                    if (data.status === 'Exercise deleted') {
                        location.reload(); // Reload the page if exercise is successfully deleted
                    }
                })
                .catch(error => {
                    // Handle errors silently
                });
            });
        });
    }
});
