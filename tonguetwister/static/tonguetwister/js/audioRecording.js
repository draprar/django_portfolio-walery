// Wait until the DOM is fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {

    // Cache DOM elements for reuse
    const micBtn = document.getElementById('mic-btn');
    const micBtnMobile = document.getElementById('mic-btn-mobile');
    const micImg = document.getElementById('mic-img');

    // Destructure mic configuration from global window object
    const { micOnSrc, micOffSrc } = window.micConfig;

    // Declare variables for audio recording
    let audioContext = null; // Holds the AudioContext instance
    let audioChunks = []; // Array to store recorded audio chunks
    let currentStream = null; // Store the current media stream
    let recordingAudio = false; // Boolean flag for recording state

    /**
     * Start recording audio
     * Uses the MediaDevices API to capture the user's microphone input
     */
    async function startAudioRecording() {
        try {
            // Request permission and access to the microphone
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            recordingAudio = true;
            currentStream = stream;

            // Create a new AudioContext for managing audio
            audioContext = new (window.AudioContext || window.webkitAudioContext)();

            // Create a MediaStreamAudioSourceNode from the audio stream
            const source = audioContext.createMediaStreamSource(stream);

            // Create a ScriptProcessorNode to process the audio stream
            const processor = audioContext.createScriptProcessor(4096, 1, 1);

            // Define how to handle audio processing
            processor.onaudioprocess = (e) => {
                // Extract audio data from the input buffer
                const inputData = e.inputBuffer.getChannelData(0);

                // Convert the audio data to a 16-bit signed integer array
                const buffer = inputData.map(sample => Math.max(-1, Math.min(1, sample)) * 0x7FFF);

                // Add the processed audio chunk to the array
                audioChunks.push(new Int16Array(buffer));
            };

            // Connect the source to the processor and the processor to the destination
            source.connect(processor);
            processor.connect(audioContext.destination);

            // Update UI to reflect that recording has started
            updateUIForRecording(true);
        } catch (err) {
            // Handle any errors related to accessing the microphone
            console.error('Error accessing audio stream:', err);
            alert('Błąd przy próbie dostępu do mikrofonu. Proszę sprawdzić uprawnienia.');
        }
    }

    /**
     * Stop recording audio
     * Encodes the recorded audio into an MP3 file
     */
    function stopAudioRecording() {
        if (recordingAudio) {
            // Close the AudioContext to free up system resources
            audioContext.close();

            // Export the recorded audio chunks as an MP3 file
            const mp3Blob = exportMP3(audioChunks);

            // Prompt the user to save the file
            confirmSave(mp3Blob, 'audio.mp3');

            // Reset the recording state
            resetRecordingState();
        }
    }

    /**
     * Export recorded audio chunks to an MP3 format
     * @param {Array} chunks - The array of audio chunks to encode
     * @returns {Blob} - The MP3 file as a blob
     */
    function exportMP3(chunks) {
        const mp3Encoder = new lamejs.Mp3Encoder(1, 44100, 128);
        const mp3Data = [];

        // Process each audio chunk and encode it as MP3
        chunks.forEach(chunk => {
            const mp3buf = mp3Encoder.encodeBuffer(chunk);
            if (mp3buf.length) mp3Data.push(new Int8Array(mp3buf));
        });

        // Finalize the encoding and push the remaining buffer
        const mp3buf = mp3Encoder.flush();
        if (mp3buf.length) mp3Data.push(new Int8Array(mp3buf));

        return new Blob(mp3Data, { type: 'audio/mp3' });
    }

    /**
     * Stop the media stream by stopping all tracks
     */
    function stopMediaStream() {
        currentStream?.getTracks().forEach(track => track.stop());
        currentStream = null;
    }

    /**
     * Confirm with the user if they want to save the recorded file
     * @param {Blob} blob - The audio file blob
     * @param {string} filename - The filename to save as
     */
    function confirmSave(blob, filename) {
        if (confirm("Czy chcesz zapisać nagranie?")) {
            downloadBlob(blob, filename);
        }
    }

    /**
     * Trigger download of a blob object as a file
     * @param {Blob} blob - The blob to download
     * @param {string} filename - The file name
     */
    function downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob); // Create a URL for the blob
        const a = document.createElement('a'); // Create an anchor element
        a.href = url;
        a.download = filename;
        document.body.appendChild(a); // Add anchor to DOM
        a.click(); // Programmatically click the anchor to trigger download

        // Cleanup by removing the anchor and revoking the URL
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    }

    /**
     * Update the UI based on whether recording is active
     * @param {boolean} isRecording - Flag to indicate recording state
     */
    function updateUIForRecording(isRecording) {
        micBtn.textContent = isRecording ? '🛑 Zatrzymaj nagranie' : '🎙️ Nagraj swój głos';
        micImg.src = isRecording ? micOffSrc : micOnSrc;
        micImg.alt = isRecording ? 'mic-off' : 'mic-on';
    }

    /**
     * Reset the recording state and UI
     */
    function resetRecordingState() {
        recordingAudio = false;
        audioChunks = []; // Clear the audio chunks
        stopMediaStream(); // Stop the media stream
        updateUIForRecording(false); // Update the UI
    }

    /**
     * Toggle between starting and stopping the recording
     */
    function toggleRecording() {
        recordingAudio ? stopAudioRecording() : startAudioRecording();
    }

    // Attach event listeners for both desktop and mobile microphone buttons
    micBtn.addEventListener('click', toggleRecording);
    micBtnMobile.addEventListener('click', toggleRecording);

    // Clean up event listeners and stop the media stream before the user leaves the page
    window.addEventListener('beforeunload', () => {
        stopMediaStream();
        micBtn.removeEventListener('click', toggleRecording);
        micBtnMobile.removeEventListener('click', toggleRecording);
    })
});
