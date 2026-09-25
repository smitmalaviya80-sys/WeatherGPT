# WeatherGPT ⛅🤖 - Autonomous AI Weather Intelligence System

WeatherGPT is an advanced AI weather intelligence platform combining **FastAPI**, **Open-Meteo API**, **Ollama Llama 3.2 3B**, and a **Glassmorphism UI Frontend**. It converts raw meteorology forecasts into grounded, context-aware natural language answers for general users, farmers, and disaster managers.

---

## 🌟 Key Features

### 1. Grounded LLM Weather Agent
- Autonomous **intent recognition** (`CURRENT_WEATHER`, `FORECAST`, `HOURLY_FORECAST`, `RAIN`, `TEMPERATURE`, `WIND`, `HUMIDITY`, `SUNRISE_SUNSET`, `AGRICULTURE`, `ALERT`).
- Tool-calling planner executing exact meteorology parameters.
- **Zero Hallucination Guarantee**: Strict rules ensure the AI never invents weather data, dates, or rainfall numbers.

### 2. Sector-Specific Advisories
- **Agricultural Intelligence**: Recommends pesticide spraying, irrigation, and crop protection window based on real-time wind speed, rain probability, and temperature.
- **Precipitation & Storm Warnings**: Instant alerts on rain probabilities and extreme weather windows.

### 3. Glassmorphism UI Frontend
- Frosted glass containers (`backdrop-filter: blur(16px)`), dynamic gradient background animations, and custom dark mode layout.
- Real-time **Speech-to-Text (STT)** microphone input and **Text-to-Speech (TTS)** voice output.
- Live system status pill polling backend health (`GET /health`).

### 4. Multi-Language Support
- Deterministic detection and synthesis for **English**, **Hindi (हिंदी)**, and **Gujarati (ગુજરાતી)**.

---

## 🏗️ Architecture & Project Structure

```
WeatherGPT/
├── backend/
│   ├── main.py                # FastAPI Application & Route Handlers
│   ├── weather.py             # Facade Module (Backward Compatibility)
│   ├── requirements.txt       # Python Package Dependencies
│   ├── .env.example           # Environment Variables Template
│   │
│   ├── weather/               # Weather Service Package
│   │   ├── __init__.py
│   │   ├── weather_service.py # Open-Meteo Forecast Fetcher & Caching
│   │   ├── geocoding.py       # City Geocoding API Search
│   │   ├── forecast.py        # Daily & Hourly Forecast Summarizers
│   │   └── parser.py          # City, Language, Date & Time Period Parser
│   │
│   ├── agent/                 # Autonomous Weather Agent Package
│   │   ├── __init__.py
│   │   ├── intent.py          # Intent Recognition Engine
│   │   ├── planner.py         # Tool Execution Planner
│   │   └── weather_agent.py   # Grounded LLM Response Synthesizer
│   │
│   └── utils/                 # Utilities Package
│       ├── __init__.py
│       ├── logging_config.py  # Structured Console Logging
│       └── cache.py           # In-Memory Cache with Configurable TTL
│
├── frontend/
│   ├── index.html             # Glassmorphism HTML5 Dashboard
│   ├── style.css              # Custom Glassmorphism CSS Styles System
│   └── app.js                 # Frontend Logic, STT/TTS & API Client
│
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+** installed
- **Ollama** installed locally (with `llama3.2:3b` model downloaded)

```bash
ollama run llama3.2:3b
```

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables template
cp .env.example .env

# Run FastAPI server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend will be live at `http://127.0.0.1:8000`.

---

### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Start a static HTTP server
python -m http.server 8080
```

Frontend will be live at `http://127.0.0.1:8080`.

---

## 📡 API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API status message |
| `GET` | `/health` | System health check (API, Weather API, Ollama status) |
| `GET` | `/smartChat?question=...` | Legacy chat endpoint |
| `POST` | `/agent/chat` | Main Weather Agent chat endpoint |

### Example `POST /agent/chat` Request

```json
{
  "question": "Should I spray pesticide tomorrow in Ahmedabad?"
}
```

### Example Response

```json
{
  "question": "Should I spray pesticide tomorrow in Ahmedabad?",
  "intent": "AGRICULTURE",
  "location": "Ahmedabad",
  "coordinates": { "latitude": 23.02579, "longitude": 72.58727 },
  "language": "English",
  "source": "Open-Meteo API",
  "confidence": "high",
  "data_time": "2026-09-25T21:30:00Z",
  "answer": "Based on weather data for Ahmedabad on 2026-09-26, wind speed is 15.2 km/h and rain probability is 0%. Conditions are favorable for agricultural spraying.",
  "verified_data": {
    "location": "Ahmedabad",
    "date": "2026-09-26",
    "condition": "Mainly clear",
    "maxTemperature": 34.5,
    "minTemperature": 24.6,
    "rainProbability": 0,
    "maxWindSpeed": 15.2
  }
}
```

---

## 🔮 Future Improvements Roadmap

- **PostgreSQL Database Integration**: Conversation history storage, user accounts, and location bookmarks.
- **RAG Architecture**: Integration with IMD bulletins and agricultural extension advisories.
- **SMS & WhatsApp Alerts**: Automated weather alerts for farmers via Twilio / SMS gateways.
- **Historical Climate Analysis**: Comparative rainfall & temperature trend analysis over past decades.

---

## 📜 License

MIT License. Built for hackathon innovation.
