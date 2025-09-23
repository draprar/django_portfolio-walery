document.addEventListener('DOMContentLoaded', function() {
    // Initialize button and offset variables
    const triviaBtn = document.getElementById('load-more-trivia-btn');
    let triviaOffset = parseInt(triviaBtn.getAttribute('data-offset'));
    const triviaUrl = triviaBtn.getAttribute('data-url');

    const factsBtn = document.getElementById('load-more-facts-btn');
    let factsOffset = parseInt(factsBtn.getAttribute('data-offset'));
    const factsUrl = factsBtn.getAttribute('data-url');

    // Completion flags to track if all trivia/facts have been loaded
    let triviaComplete = false;
    let factsComplete = false;

    // Trivia button click handler
    triviaBtn.addEventListener('click', function() {
        $.ajax({
            url: triviaUrl,
            data: { 'offset': triviaOffset },
            dataType: 'json',
            success: function(data) {
                if (data.length > 0) {
                    $('#trivia-container').empty();
                    $('#facts-container').empty();
                    for (let i = 0; i < data.length; i++) {
                        $('#trivia-container').append('<div class="trivia col-md-16 fs-4 bg-light bg-gradient text-center shadow-sm p-3 my-3 rounded border">' + data[i].text + '</div>');
                    }
                    triviaOffset += data.length;

                } else {
                    triviaComplete = true;
                    $('#load-more-trivia-btn').hide();
                    $('#trivia-container .trivia').hide();
                    checkCompletionTrivia();
                }
            }
        });
    });

    // Facts button click handler
    factsBtn.addEventListener('click', function() {
        $.ajax({
            url: factsUrl,
            data: { 'offset': factsOffset },
            dataType: 'json',
            success: function(data) {
                if (data.length > 0) {
                    $('#facts-container').empty();
                    $('#trivia-container').empty();
                    for (let i = 0; i < data.length; i++) {
                        $('#facts-container').append('<br><div class="fact col-md-16 fs-4 bg-light bg-gradient text-center shadow-sm p-3 my-3 rounded border">' + data[i].text + '</div>');
                    }
                    factsOffset += data.length;

                } else {
                    factsComplete = true;
                    $('#load-more-facts-btn').hide();
                    $('#facts-container .fact').hide();
                    checkCompletionFacts();
                }
            }
        });
    });

    // Trivia completion check
    function checkCompletionTrivia() {
        if (triviaComplete) {
            showCongratulationsModalTrivia();
        }
    }

    // Trivia modal
    function showCongratulationsModalTrivia() {
        document.getElementById('congratulations-modal-trivia').style.display = 'block';
        loadMoreBtn.style.display = 'none';

        const successSound = document.getElementById('success-sound-trivia');
        successSound.play();

        if (navigator.vibrate) {
            navigator.vibrate(200);
        }
    }

    // Facts completion check
    function checkCompletionFacts() {
        if (factsComplete) {
            showCongratulationsModal();
        }
    }

    // Facts modal
    function showCongratulationsModal() {
        let modal = document.getElementById('congratulations-modal');
        let span = modal.getElementsByClassName('close')[0];

        modal.style.display = 'block';

        span.onclick = function() {
            modal.style.display = 'none';
        }

        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }

        const successSound = document.getElementById('success-sound-end');
        successSound.play();

        if (navigator.vibrate) {
            navigator.vibrate(200);
        }
    }

    // Change button text for trivia
    function changeTriviaButtonText() {
        var button = document.getElementById("load-more-trivia-btn");
        button.textContent = "Więcej porad";
    }
    document.getElementById("load-more-trivia-btn").onclick = changeTriviaButtonText;

    // Change button text for facts
    function changeFactsButtonText() {
        var button = document.getElementById("load-more-facts-btn");
        button.textContent = "Więcej ciekawostek";
    }
    document.getElementById("load-more-facts-btn").onclick = changeFactsButtonText;

});
