document.addEventListener('DOMContentLoaded', () => {
    const beaverImg = document.getElementById('chat-beaver-img');
    const speechBubble = document.getElementById('chat-speech-bubble');
    const beaverContainer = document.getElementById('chat-beaver-container');
    const chatSendButton = document.getElementById('chat-send-button');
    const chatUserInput = document.getElementById('chat-user-input');
    const chatText = document.getElementById('chat-text');

    let isDragging = false;
    let offsetX = 0, offsetY = 0;

    // Start dragging the beaver container
    const startDrag = (e) => {
        isDragging = true;
        const rect = beaverContainer.getBoundingClientRect();
        offsetX = (e.clientX || e.touches[0].clientX) - rect.left;
        offsetY = (e.clientY || e.touches[0].clientY) - rect.top;
        e.preventDefault();
    };

    // Handle the dragging movement
    const doDrag = (e) => {
        if (isDragging) {
            const x = (e.clientX || e.touches[0].clientX) - offsetX;
            const y = (e.clientY || e.touches[0].clientY) - offsetY;
            beaverContainer.style.left = `${x}px`;
            beaverContainer.style.top = `${y}px`;
        }
    };

    // Stop dragging
    const stopDrag = () => {
        isDragging = false;
    };

    // Sending message through the chat
    const sendMessage = () => {
        const userMessage = chatUserInput.value.trim();
        if (userMessage) {
            fetch(`/tonguetwister/chatbot/?message=${encodeURIComponent(userMessage)}`)
                .then(response => response.json())
                .then(data => {
                    chatText.innerText = data.response;
                    chatUserInput.value = '';
                })
                .catch(error => console.error('Error fetching chatbot response:', error));
        }
    };

    // Handle input submission via 'Enter' key
    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            chatSendButton.click();
        }
    };

    // Prevent propagation of mousedown and touchstart events for input and button elements
    const stopPropagation = (e) => e.stopPropagation();

    // Dragging event listeners for desktop and mobile
    beaverContainer.addEventListener('mousedown', startDrag);
    document.addEventListener('mousemove', doDrag);
    document.addEventListener('mouseup', stopDrag);

    beaverContainer.addEventListener('touchstart', startDrag);
    document.addEventListener('touchmove', doDrag);
    document.addEventListener('touchend', stopDrag);

    // Chat-related event listeners
    chatSendButton.addEventListener('click', sendMessage);
    chatUserInput.addEventListener('keypress', handleKeyPress);
    chatUserInput.addEventListener('mousedown', stopPropagation);
    chatSendButton.addEventListener('mousedown', stopPropagation);
    chatUserInput.addEventListener('focus', stopPropagation);
    chatSendButton.addEventListener('touchstart', stopPropagation);
    chatSendButton.addEventListener('touchstart', () => chatSendButton.click());
    chatUserInput.addEventListener('touchstart', stopPropagation);
});
