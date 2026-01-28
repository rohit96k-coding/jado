const socket = io();

// UI Elements
const statusText = document.getElementById('listening-status');
const conversationLog = document.getElementById('conversation-log');
const aiCore = document.querySelector('.robot-container');
const micBtn = document.getElementById('mic-btn');

// Mode Switching Logic
const modeRobotBtn = document.getElementById('mode-robot');
const modeScreenBtn = document.getElementById('mode-screen');
const viewRobot = document.getElementById('view-robot');
const viewScreen = document.getElementById('view-screen');
const liveFeedImg = document.getElementById('live-feed');

function switchMode(mode) {
    if (mode === 'robot') {
        modeRobotBtn.classList.add('active');
        modeScreenBtn.classList.remove('active');
        viewRobot.style.display = 'flex';
        viewScreen.style.display = 'none';
        // Stop fetching video to save bandwidth
        liveFeedImg.src = '';
    } else {
        modeScreenBtn.classList.add('active');
        modeRobotBtn.classList.remove('active');
        viewScreen.style.display = 'flex';
        viewRobot.style.display = 'none';
        // Start fetching video
        liveFeedImg.src = '/video_feed';
    }
}

if (modeRobotBtn && modeScreenBtn) {
    modeRobotBtn.addEventListener('click', () => switchMode('robot'));
    modeScreenBtn.addEventListener('click', () => switchMode('screen'));
}

if (micBtn) {
    micBtn.addEventListener('click', () => {
        socket.emit('toggle_listening', { action: 'toggle' });
    });
}

// Text Input Logic
const userInput = document.getElementById('user-input');

const sendBtn = document.getElementById('send-btn');
const uploadBtn = document.getElementById('upload-btn');
const cameraBtn = document.getElementById('camera-btn');
const imageUploadInput = document.getElementById('image-upload');



function sendCommand() {
    const text = userInput.value.trim();
    if (text) {
        // Emit text command to server
        socket.emit('text_command', { text: text });
        userInput.value = ''; // Clear input
    }
}

if (sendBtn) {
    sendBtn.addEventListener('click', sendCommand);
}

if (userInput) {
    let commandHistory = [];
    let historyIndex = -1;

    // Listen for inputs to add to history when sent
    function addToHistory(cmd) {
        if (cmd && (commandHistory.length === 0 || commandHistory[commandHistory.length - 1] !== cmd)) {
            commandHistory.push(cmd);
        }
        historyIndex = commandHistory.length;
    }

    // Override sendCommand to use addToHistory is harder cause it's outside.
    // Let's modify the existing listeners or just wrap the logic.
    // Actually, let's just intercept the send logic in the listeners.

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const text = userInput.value.trim();
            if (text) {
                addToHistory(text);
                sendCommand(); // Send the command!
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (commandHistory.length > 0) {
                if (historyIndex > 0) {
                    historyIndex--;
                }
                userInput.value = commandHistory[historyIndex];
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (historyIndex < commandHistory.length - 1) {
                historyIndex++;
                userInput.value = commandHistory[historyIndex];
            } else {
                historyIndex = commandHistory.length;
                userInput.value = '';
            }
        }
    });

    // We also need to capture clicks on send button to add to history
    if (sendBtn) {
        sendBtn.addEventListener('click', () => {
            const text = userInput.value.trim();
            if (text) addToHistory(text);
        });
    }
}

/* -------------------------------------------------------------------------- */
/*                            IMAGE ANALYSIS LOGIC                            */
/* -------------------------------------------------------------------------- */

// Upload Button
if (uploadBtn && imageUploadInput) {
    uploadBtn.addEventListener('click', () => {
        imageUploadInput.click();
    });

    imageUploadInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (event) {
                const base64Image = event.target.result;
                sendImageForAnalysis(base64Image, "Analyze this uploaded image.");
            };
            reader.readAsDataURL(file);
        }
    });
}

// Camera Button
if (cameraBtn) {
    cameraBtn.addEventListener('click', async () => {
        try {
            addLog("System: Accessing Camera...", "system");
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });

            // Create a temporary video element to capture the frame
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();

            // Wait for it to play
            await new Promise(r => setTimeout(r, 500)); // Delay for auto-exposure

            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const base64Image = canvas.toDataURL('image/jpeg');

            // Stop stream
            stream.getTracks().forEach(track => track.stop());

            sendImageForAnalysis(base64Image, "What do use see in this camera view?");

        } catch (err) {
            addLog(`Camera Error: ${err.message}`, "system");
            alert("Camera access failed or denied.");
        }
    });
}

function sendImageForAnalysis(imageBase64, message) {
    addLog("System: Sending Image to Neural Engine...", "system");

    // Show preview in log (optional)
    const preview = document.createElement('img');
    preview.src = imageBase64;
    preview.style.maxWidth = "200px";
    preview.style.borderRadius = "10px";
    preview.style.marginTop = "10px";
    const entry = document.createElement('div');
    entry.className = "log-entry user";
    entry.appendChild(preview);
    conversationLog.appendChild(entry);
    conversationLog.scrollTop = conversationLog.scrollHeight;

    // Send to Backend
    fetch('/analyze_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            image: imageBase64,
            message: message
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                addLog(`SAMi: ${data.response}`, "sami");
            } else if (data.error) {
                addLog(`Error: ${data.error}`, "system");
            }
        })
        .catch(error => {
            addLog(`Network Error: ${error}`, "system");
        });
}

/* -------------------------------------------------------------------------- */
/*                               MATRIX RAIN EFFECT                           */
/* -------------------------------------------------------------------------- */
const canvas = document.getElementById('matrix-bg');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const matrixChars = "01";
const fontSize = 16;
const columns = canvas.width / fontSize;

// Array for drops - one per column
const drops = [];
for (let x = 0; x < columns; x++) {
    drops[x] = 1;
}


function drawMatrix() {
    // Black BG for the trail effect
    ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // VIBRANT NEON PALETTE for Matrix Rain
    const colors = ["#ff00ff", "#00ffff", "#bc13fe", "#0aff0a", "#ffffff"];
    ctx.font = fontSize + "px monospace";

    for (let i = 0; i < drops.length; i++) {
        // Random character
        const text = matrixChars.charAt(Math.floor(Math.random() * matrixChars.length));

        // Random color for each character to make it sparkling
        ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);

        // Reset drop to top randomly after it's fallen
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }

        drops[i]++;
    }
}

// Run Matrix animation
setInterval(drawMatrix, 33);

// Handle window resize
window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});


/* -------------------------------------------------------------------------- */
/*                                SOCKET LOGIC                                */
/* -------------------------------------------------------------------------- */

// Helper to add log
function addLog(text, type, imageUrl = null) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = text;

    if (imageUrl) {
        const img = document.createElement('img');
        img.src = imageUrl;
        img.style.maxWidth = "100%";
        img.style.borderRadius = "10px";
        img.style.marginTop = "10px";
        img.style.display = "block";
        img.alt = "Generated Image";

        // Error Handler
        img.onerror = function () {
            // Check if already retried to prevent infinite loop
            if (this.dataset.retry === "true") {
                this.style.display = 'none';
                const err = document.createElement('div');
                err.style.color = 'red';
                err.style.fontSize = '12px';
                err.textContent = "[Image Failed to Load]";
                entry.appendChild(err);
                return;
            }

            // Mark as retried
            this.dataset.retry = "true";
            console.log("Image load failed. Retrying via Proxy...");

            // Try Proxy
            this.src = '/proxy_image?url=' + encodeURIComponent(imageUrl);
        };

        entry.appendChild(img);
    }

    conversationLog.appendChild(entry);
    conversationLog.scrollTop = conversationLog.scrollHeight;
}

// Socket Events
socket.on('connect', () => {
    addLog('Interface connected to Mainframe.', 'system');
});

socket.on('status_update', (data) => {
    statusText.textContent = data.status.toUpperCase();

    // Speaking Animation for Core
    if (data.status.includes("Speaking")) {
        if (aiCore) aiCore.classList.add('speaking');
    } else {
        if (aiCore) aiCore.classList.remove('speaking');
    }
});

socket.on('mic_state', (data) => {
    if (data.active) {
        if (micBtn) micBtn.classList.add('active');
    } else {
        if (micBtn) micBtn.classList.remove('active');
    }
});

socket.on('system_stats', (data) => {
    // Update Bars
    const cpuBar = document.getElementById('cpu-bar');
    const ramBar = document.getElementById('ram-bar');
    const diskBar = document.getElementById('disk-bar');

    if (cpuBar) cpuBar.style.width = data.cpu + '%';
    if (document.getElementById('cpu-text')) document.getElementById('cpu-text').textContent = data.cpu + '%';

    if (ramBar) ramBar.style.width = data.ram + '%';
    if (document.getElementById('ram-text')) document.getElementById('ram-text').textContent = data.ram + '%';

    if (diskBar) diskBar.style.width = data.disk + '%';
    if (document.getElementById('disk-text')) document.getElementById('disk-text').textContent = data.disk + '%';

    // Update Info
    if (document.getElementById('clock')) document.getElementById('clock').textContent = data.time;
    if (document.getElementById('date')) document.getElementById('date').textContent = data.date;
    if (document.getElementById('weather')) document.getElementById('weather').textContent = data.weather;
});

socket.on('conversation_update', (data) => {
    if (data.role === 'user') {
        addLog(`USER: ${data.text}`, 'user');
    } else {
        // Check for image
        if (data.image) {
            addLog(`SAMi: ${data.text}`, 'sami', data.image);
        } else {
            addLog(`SAMi: ${data.text}`, 'sami');
        }
    }
});

/* -------------------------------------------------------------------------- */
/*                            WEB SPEECH API (MOBILE MIC)                     */
/* -------------------------------------------------------------------------- */
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
let isMobileListening = false;
const mobileMicBtn = document.getElementById('mobile-mic-btn');

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = true; // Enabled for Hands-Free
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = function () {
        isMobileListening = true;
        if (mobileMicBtn) mobileMicBtn.classList.add('pulse-active');
        addLog("Mobile Mic: Listening (Hands-Free)...", "system");
    };

    recognition.onend = function () {
        // Auto-restart if we want persistent hands-free
        if (isMobileListening) {
            recognition.start(); // Restart instantly
        } else {
            if (mobileMicBtn) mobileMicBtn.classList.remove('pulse-active');
        }
    };

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        addLog(`Mobile Voice: "${transcript}"`, "user");
        socket.emit('text_command', { text: transcript });
    };

    recognition.onerror = function (event) {
        console.error("Speech Error:", event.error);
        addLog(`Mobile Mic Error: ${event.error}`, "system");
        if (event.error === 'not-allowed') {
            alert("Microphone access blocked. Please allow mic permissions in your browser settings. If on HTTP, some mobile browsers block this.");
        } else if (event.error === 'network') {
            alert("Network error. Please check your connection.");
        }
        if (mobileMicBtn) mobileMicBtn.classList.remove('pulse-active');
    };
} else {
    console.log("Web Speech API not supported in this browser.");
}

// Toggle Mobile Mic
if (mobileMicBtn) {
    mobileMicBtn.addEventListener('click', () => {
        if (!recognition) {
            alert("Voice input not supported in this browser. Try Chrome.");
            return;
        }
        if (isMobileListening) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });
}

/* -------------------------------------------------------------------------- */
/*                            PWA INSTALL LOGIC                               */
/* -------------------------------------------------------------------------- */
let deferredPrompt;
const installBtn = document.getElementById('install-btn');

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later.
    deferredPrompt = e;
    // Update UI to notify the user they can add to home screen
    if (installBtn) installBtn.style.display = 'flex';

    addLog("System: App Installation Ready.", "system");
});

if (installBtn) {
    installBtn.addEventListener('click', (e) => {
        // Hide our user interface that shows our A2HS button
        installBtn.style.display = 'none';
        // Show the prompt
        if (deferredPrompt) {
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    addLog('User accepted the A2HS prompt', 'system');
                } else {
                    addLog('User dismissed the A2HS prompt', 'system');
                }
                deferredPrompt = null;
            });
        }
    });
}

/* -------------------------------------------------------------------------- */
/*                            PARALLAX EFFECT (Optimized)                     */
/* -------------------------------------------------------------------------- */
let isParallaxRunning = false;
document.addEventListener('mousemove', (e) => {
    if (isParallaxRunning) return;

    isParallaxRunning = true;
    requestAnimationFrame(() => {
        const panels = document.querySelectorAll('.panel');
        // Reduce intensity for smoother feel
        const x = (window.innerWidth - e.pageX * 2) / 200;
        const y = (window.innerHeight - e.pageY * 2) / 200;

        panels.forEach(panel => {
            // simplified transform
            panel.style.transform = `perspective(1000px) rotateY(${x}deg) rotateX(${y}deg)`;
        });

        const robot = document.querySelector('.robot-container');
        if (robot) {
            robot.style.transform = `perspective(1000px) rotateY(${x * 2}deg) rotateX(${y * 2}deg)`;
        }

        isParallaxRunning = false;
    });
});
