const API_BASE = "https://weathergpt-backend-t8x3.onrender.com";

// DOM Elements
const healthPill = document.getElementById('healthPill');
const healthText = document.getElementById('healthText');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const chatHistory = document.getElementById('chatHistory');
const micBtn = document.getElementById('micBtn');

// Weather Dashboard Elements
const locationName = document.getElementById('locationName');
const weatherDate = document.getElementById('weatherDate');
const tempValue = document.getElementById('tempValue');
const conditionText = document.getElementById('conditionText');
const feelsLikeValue = document.getElementById('feelsLikeValue');
const rainProb = document.getElementById('rainProb');
const humidityVal = document.getElementById('humidityVal');
const windSpeed = document.getElementById('windSpeed');
const sunTimes = document.getElementById('sunTimes');
const sourceName = document.getElementById('sourceName');
const confidenceScore = document.getElementById('confidenceScore');
const advisoryText = document.getElementById('advisoryText');
const weatherIcon = document.getElementById('weatherIcon');

// Check Backend Health
async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
            const data = await res.json();
            healthPill.classList.add('online');
            healthText.innerText = `API Live | Weather: ${data.weather} | AI: ${data.ollama}`;
        } else {
            healthText.innerText = "API Offline";
            healthPill.classList.remove('online');
        }
    } catch (err) {
        healthText.innerText = "API Offline (127.0.0.1:8000)";
        healthPill.classList.remove('online');
    }
}

// Initial health check and interval
checkHealth();
setInterval(checkHealth, 10000);

// Load initial weather for Ahmedabad on startup
fetchWeatherForCity("Ahmedabad");

async function fetchWeatherForCity(city) {
    try {
        const res = await fetch(`${API_BASE}/agent/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: `What is the weather in ${city}?` })
        });
        if (res.ok) {
            const data = await res.json();
            updateDashboard(data);
        }
    } catch (err) {
        console.warn("Could not fetch initial weather:", err);
    }
}

// Handle Form Submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = userInput.value.trim();
    if (!question) return;

    // 1. Add User Bubble
    addUserBubble(question);
    userInput.value = '';

    // 2. Add Loading Agent Bubble
    const loadingId = addLoadingBubble();

    try {
        const res = await fetch(`${API_BASE}/agent/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        removeBubble(loadingId);

        if (res.ok) {
            const data = await res.json();
            addAgentBubble(data);
            updateDashboard(data);
        } else {
            addAgentBubble({
                answer: "Sorry, I encountered an error processing your query. Please ensure the backend is running.",
                source: "System Error",
                confidence: "Low",
                intent: "ERROR"
            });
        }
    } catch (err) {
        removeBubble(loadingId);
        addAgentBubble({
            answer: `Could not connect to backend server at ${API_BASE}. Please ensure uvicorn is running.`,
            source: "Network Error",
            confidence: "Low",
            intent: "OFFLINE"
        });
    }
});

// Quick Prompt Clicks
document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
        const promptText = chip.getAttribute('data-prompt');
        userInput.value = promptText;
        chatForm.dispatchEvent(new Event('submit'));
    });
});

// Add User Bubble
function addUserBubble(text) {
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble user-bubble';
    bubble.innerHTML = `
        <div class="bubble-header">
            <span class="bubble-author">You</span>
            <span class="bubble-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
        </div>
        <div class="bubble-content">${escapeHTML(text)}</div>
    `;
    chatHistory.appendChild(bubble);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Add Loading Bubble
function addLoadingBubble() {
    const id = 'loading-' + Date.now();
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble agent-bubble';
    bubble.id = id;
    bubble.innerHTML = `
        <div class="bubble-header">
            <span class="bubble-avatar"><i class="fa-solid fa-spinner fa-spin"></i></span>
            <span class="bubble-author">WeatherGPT Thinking...</span>
        </div>
        <div class="bubble-content">Analyzing weather data & verifying facts...</div>
    `;
    chatHistory.appendChild(bubble);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return id;
}

function removeBubble(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Add Agent Response Bubble
function addAgentBubble(data) {
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble agent-bubble';
    
    const timeStr = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    const speakBtnId = 'speak-' + Date.now();

    bubble.innerHTML = `
        <div class="bubble-header">
            <span class="bubble-avatar"><i class="fa-solid fa-robot"></i></span>
            <span class="bubble-author">WeatherGPT Agent</span>
            <span class="bubble-time">${timeStr}</span>
            <button class="input-action-btn" id="${speakBtnId}" style="width:24px; height:24px; margin-left:8px;" title="Listen (TTS)">
                <i class="fa-solid fa-volume-high"></i>
            </button>
        </div>
        <div class="bubble-content">${escapeHTML(data.answer)}</div>
        <div class="bubble-meta">
            ${data.intent ? `<span class="meta-tag"><i class="fa-solid fa-bullseye"></i> ${data.intent}</span>` : ''}
            ${data.source ? `<span class="meta-tag"><i class="fa-solid fa-database"></i> ${data.source}</span>` : ''}
            ${data.confidence ? `<span class="meta-tag"><i class="fa-solid fa-shield-halved"></i> Confidence: ${data.confidence}</span>` : ''}
            ${data.language ? `<span class="meta-tag"><i class="fa-solid fa-language"></i> ${data.language}</span>` : ''}
        </div>
    `;
    
    chatHistory.appendChild(bubble);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // TTS Speak button event
    document.getElementById(speakBtnId).addEventListener('click', () => {
        speakText(data.answer);
    });
}

// Update Right Side Weather Dashboard
function updateDashboard(data) {
    if (!data || !data.verified_data) return;

    const v = data.verified_data;
    const curr = v.current || {};

    locationName.innerText = data.location || v.location || "Ahmedabad";
    weatherDate.innerText = v.date ? `Forecast Date: ${v.date}` : `Realtime ${new Date().toLocaleDateString()}`;

    // Temperature
    if (v.maxTemperature !== undefined && v.minTemperature !== undefined) {
        tempValue.innerText = `${v.maxTemperature}`;
        feelsLikeValue.innerText = `${v.minTemperature}`;
    } else if (curr.temperature !== undefined) {
        tempValue.innerText = `${curr.temperature}`;
        feelsLikeValue.innerText = `${curr.feelsLike || curr.temperature}`;
    }

    // Condition
    const cond = v.condition || curr.condition || "Clear";
    conditionText.innerText = cond;
    updateWeatherIcon(cond);

    // Metrics
    rainProb.innerText = `${v.rainProbability !== undefined ? v.rainProbability : (v.rainProbabilityMax || 0)}%`;
    humidityVal.innerText = `${curr.humidity !== undefined ? curr.humidity : (v.humidityMax || '--')}%`;
    windSpeed.innerText = `${v.maxWindSpeed || curr.windSpeed || '--'} km/h`;
    
    if (v.sunrise && v.sunset) {
        const sr = v.sunrise.split('T')[1] || v.sunrise;
        const ss = v.sunset.split('T')[1] || v.sunset;
        sunTimes.innerText = `${sr} / ${ss}`;
    } else {
        sunTimes.innerText = "06:30 / 18:30";
    }

    // Source & Confidence
    sourceName.innerText = data.source || "Open-Meteo API";
    confidenceScore.innerText = data.confidence ? data.confidence.toUpperCase() : "HIGH";

    // Sector Advisory Update
    if (data.intent === "AGRICULTURE") {
        advisoryText.innerHTML = `<strong>Farmer Advisory:</strong> ${data.answer}`;
    } else if (data.intent === "RAIN") {
        advisoryText.innerHTML = `<strong>Precipitation Warning:</strong> Max Rain Probability: ${v.rainProbabilityMax || v.rainProbability || 0}%. ${data.answer}`;
    } else {
        advisoryText.innerText = data.answer || "Weather metrics are verified against Open-Meteo API.";
    }
}

// Update Animated Weather Icon
function updateWeatherIcon(condition) {
    const c = condition.toLowerCase();
    let iconClass = "fa-cloud-sun";

    if (c.includes("rain") || c.includes("drizzle") || c.includes("shower")) {
        iconClass = "fa-cloud-showers-heavy";
    } else if (c.includes("clear") || c.includes("sunny")) {
        iconClass = "fa-sun";
    } else if (c.includes("overcast") || c.includes("cloud")) {
        iconClass = "fa-cloud";
    } else if (c.includes("thunderstorm")) {
        iconClass = "fa-cloud-bolt";
    } else if (c.includes("fog")) {
        iconClass = "fa-smog";
    }

    weatherIcon.innerHTML = `<i class="fa-solid ${iconClass}"></i>`;
}

// Web Speech STT (Speech to Text) & TTS Setup
const voiceLangSelect = document.getElementById('voiceLangSelect');
const micStatusPill = document.getElementById('micStatusPill');
const micStatusText = document.getElementById('micStatusText');

let recognition = null;
let isRecording = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    micBtn.addEventListener('click', () => {
        if (isRecording) {
            stopSpeechRecognition();
        } else {
            startSpeechRecognition();
        }
    });

    function startSpeechRecognition() {
        try {
            recognition.lang = voiceLangSelect.value || 'en-IN';
            recognition.start();
            isRecording = true;
            micBtn.classList.add('recording');
            micStatusPill.classList.remove('hidden');
            micStatusText.innerText = `Listening (${voiceLangSelect.value})... Speak now!`;
        } catch (err) {
            console.error("Speech recognition start error:", err);
            stopSpeechRecognition();
        }
    }

    function stopSpeechRecognition() {
        isRecording = false;
        micBtn.classList.remove('recording');
        micStatusPill.classList.add('hidden');
        try { recognition.stop(); } catch (e) {}
    }

    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interimTranscript += event.results[i][0].transcript;
            }
        }

        const recognizedText = finalTranscript || interimTranscript;
        if (recognizedText) {
            userInput.value = recognizedText;
        }

        if (finalTranscript) {
            stopSpeechRecognition();
            // Automatically submit after 800ms so user can see what was transcribed
            setTimeout(() => {
                if (userInput.value.trim() === finalTranscript.trim()) {
                    chatForm.dispatchEvent(new Event('submit'));
                }
            }, 800);
        }
    };

    recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        stopSpeechRecognition();
        if (event.error === 'not-allowed') {
            alert("Microphone access was denied. Please allow microphone permissions in your browser settings.");
        } else if (event.error === 'no-speech') {
            micStatusPill.classList.remove('hidden');
            micStatusText.innerText = "No speech heard. Click microphone to try again.";
            setTimeout(() => micStatusPill.classList.add('hidden'), 3000);
        }
    };

    recognition.onend = () => {
        stopSpeechRecognition();
    };
} else {
    micBtn.title = "Voice Input not supported on this browser (Use Chrome or Edge)";
}

// Speech Synthesis TTS
function speakText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        
        const lang = voiceLangSelect ? voiceLangSelect.value : 'en-IN';
        utterance.lang = lang;

        // Try selecting matching voice if available
        const voices = window.speechSynthesis.getVoices();
        const matchingVoice = voices.find(v => v.lang.toLowerCase().includes(lang.toLowerCase().split('-')[0]));
        if (matchingVoice) {
            utterance.voice = matchingVoice;
        }

        window.speechSynthesis.speak(utterance);
    }
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}
