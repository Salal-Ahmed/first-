const themeToggle = document.getElementById('theme-toggle');
const root = document.documentElement;
const chatInput = document.getElementById('chat-input');
const chatMain = document.getElementById('chat-main');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');
const fileInput = document.getElementById('file-input');
const attachmentBtn = document.getElementById('attachment-btn');
const assistantBtn = document.getElementById('assistant');


assistantBtn.addEventListener('click', () => {
    processVoice();  // Call the function that invokes the API
});

async function processVoice() {
    try {
        const response = await fetch('http://127.0.0.1:5000/process_voice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: 'Voice message or some data' }),  // Send appropriate data if needed
        });

        if (response.ok) {
            const data = await response.json();
            // Handle the response, for example, display the bot's response
            displayMessage(data.command, 'user-message')
            displayMessage(data.response, 'bot-message');
        } else {
            const errorData = await response.json();
            console.error('Error:', errorData);
            displayMessage('Error: Could not process voice.', 'bot-message');
        }
    } catch (error) {
        console.error('Error communicating with backend:', error);
        displayMessage('Error: Unable to connect to the server.', 'bot-message');
    }
}


// Toggle between light and dark themes
themeToggle.addEventListener('click', toggleTheme);

function toggleTheme() {
    const currentTheme = root.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    root.setAttribute('data-theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = theme === 'light' ? 'night-mode.png' : 'day-mode.png';
    themeToggle.innerHTML = `<img src="${icon}" width="25px" height="25px" />`;
}

// Handle input and Enter key
chatInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') processMessage();
});

// Handle Send button
sendBtn.addEventListener('click', processMessage);

// Microphone button functionality using Web Speech API
micBtn.addEventListener('click', () => {
    startSpeechRecognition();
});

function startSpeechRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.onstart = () => micBtn.title = 'Listening...';
    recognition.onresult = handleSpeechResult;
    recognition.onerror = () => {
        alert('Error capturing voice. Please try again.');
        micBtn.title = 'Speak';
    };
    recognition.start();
}

function handleSpeechResult(event) {
    const voiceInput = event.results[0][0].transcript;
    displayMessage(voiceInput, 'user-message');
    sendMessageToBackend(voiceInput);
    micBtn.title = 'Speak';
}

// Handle attachment functionality
attachmentBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
        displayMessage(`File attached: ${file.name}`, 'user-message');
    }
});

// Process text input from chat
function processMessage() {
    const message = chatInput.value.trim();
    if (message) {
        displayMessage(message, 'user-message');
        sendMessageToBackend(message);
        chatInput.value = ''; // Clear input
    }
}

function displayMessage(message, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.textContent = message;
    chatMain.appendChild(messageDiv);
    chatMain.scrollTop = chatMain.scrollHeight; // Scroll to the latest message
}

// Send message to backend and handle response
async function sendMessageToBackend(message) {
    try {
        const response = await fetch('http://127.0.0.1:5000/manual_input', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: message }),
        });

        if (response.ok) {
            const data = await response.json();
            displayMessage(data.response, 'bot-message');
        } else {
            displayMessage('Error: Could not get a response from the server.', 'bot-message');
        }
    } catch (error) {
        console.error('Error communicating with backend:', error);
        displayMessage('Error: Unable to connect to the server.', 'bot-message');
    }
}


// async function invokeVoiceAssistant(message) {
//     try {
//         const response = await fetch('http://127.0.0.1:5000/process-voice', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: "invoke",
//         });

//         if (response.ok) {
//             const data = await response.json();
//             displayMessage(data.response, 'bot-message');
//         } else {
//             displayMessage('Error: Could not get a response from the server.', 'bot-message');
//         }
//     } catch (error) {
//         console.error('Error communicating with backend:', error);
//         displayMessage('Error: Unable to connect to the server.', 'bot-message');
//     }
// }