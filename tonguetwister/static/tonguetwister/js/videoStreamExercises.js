document.addEventListener('DOMContentLoaded', () => {
    const mirrorBtn = document.getElementById('mirror-btn-exercises');
    const videoContainer = document.getElementById('video-container-exercises');
    const videoPreview = document.getElementById('video-preview-exercises');

    let stream = null;

    // Toggle video stream when mirror button is clicked
    mirrorBtn.addEventListener('click', () => {
        videoContainer.style.display === 'none' || !videoContainer.style.display
            ? startVideoStream()
            : stopVideoStream();
    });

    // Start video stream using the user's webcam
    function startVideoStream() {
        navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false })
            .then(mediaStream => {
                stream = mediaStream;
                videoPreview.srcObject = stream;
                videoContainer.style.display = 'block';
                mirrorBtn.textContent = '🛑 Zatrzymaj lusterko';
            })
            .catch(error => {
                console.error('Error accessing media devices:', error);
            });
    }

    // Stop the video stream and reset the interface
    function stopVideoStream() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
            videoPreview.srcObject = null;
            videoContainer.style.display = 'none';
            mirrorBtn.textContent = '📷 Otwórz lusterko';
        }
    }
});
