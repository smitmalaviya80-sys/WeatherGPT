from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from typing import Optional

# Imports from refactored weather package
from weather import (
    getWeather,
    getLocation,
    extractCity,
    detectLanguage,
    getWeatherDescription,
    detectDay,
    detectTimePeriod,
    getForecastForDay,
    getHourlyForecast
)
from agent import WeatherAgent

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="WeatherGPT API",
    description="Advanced AI Weather Intelligence Backend",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = WeatherAgent()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


class ChatRequest(BaseModel):
    question: str
    user_id: Optional[int] = None


@app.get("/")
def home():
    return {
        "message": "WeatherGPT API is running"
    }


@app.get("/health")
def health_check():
    # 1. API status
    api_status = "ok"

    # 2. Weather API status (Open-Meteo)
    weather_status = "ok"
    try:
        res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=23.0225&longitude=72.5714&current=temperature_2m", timeout=5)
        if res.status_code != 200:
            weather_status = "error"
    except Exception:
        weather_status = "unavailable"

    # 3. Ollama status
    ollama_status = "ok"
    try:
        res = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if res.status_code != 200:
            ollama_status = "error"
    except Exception:
        ollama_status = "unavailable"

    return {
        "api": api_status,
        "database": "not_configured",  # Configured in Phase 3
        "weather": weather_status,
        "ollama": ollama_status
    }


@app.get("/ask")
def ask(question: str):
    url = f"{OLLAMA_URL}/api/generate"

    data = {
        "model": OLLAMA_MODEL,
        "prompt": question,
        "stream": False
    }

    try:
        response = requests.post(url, json=data, timeout=15)
        if response.status_code != 200:
            return {
                "error": "AI service is not available."
            }

        result = response.json()
        return {
            "question": question,
            "answer": result.get("response", "")
        }
    except Exception as e:
        return {
            "error": "AI service is not available."
        }


@app.get("/smartChat")
def smartChat(question: str):
    # Detect language
    language = detectLanguage(question)

    # Detect city
    city = extractCity(question)

    if not city or city.lower() == "none":
        return {
            "error": "Please mention a city."
        }

    # Find location
    location = getLocation(city)

    if location is None:
        return {
            "error": "City not found."
        }

    # Get weather data
    weatherData = getWeather(
        location["latitude"],
        location["longitude"]
    )

    if weatherData is None:
        return {
            "error": "Weather data could not be fetched."
        }

    # Detect today / tomorrow
    dayIndex = detectDay(question)

    # Detect time period
    timePeriod = detectTimePeriod(question)

    # Get forecast
    if timePeriod == "full_day":
        forecast = getForecastForDay(
            weatherData,
            dayIndex
        )
    else:
        forecast = getHourlyForecast(
            weatherData,
            dayIndex,
            timePeriod
        )

    if forecast is None:
        return {
            "error": "Forecast data not available."
        }

    # Current weather
    current = weatherData["current"]

    currentWeather = {
        "temperature": current["temperature_2m"],
        "feelsLike": current["apparent_temperature"],
        "humidity": current["relative_humidity_2m"],
        "rain": current["precipitation"],
        "windSpeed": current["wind_speed_10m"],
        "condition": getWeatherDescription(
            current["weather_code"]
        )
    }

    # Create compact verified weather information
    if timePeriod == "full_day":
        weatherInfo = {
            "location": location["name"],
            "date": forecast["date"],
            "condition": forecast["condition"],
            "maxTemperature": forecast["maxTemperature"],
            "minTemperature": forecast["minTemperature"],
            "rainProbability": forecast["rainProbability"],
            "rainAmount": forecast["rainAmount"],
            "maxWindSpeed": forecast["maxWindSpeed"],
            "sunrise": forecast["sunrise"],
            "sunset": forecast["sunset"]
        }
    else:
        temperatures = []
        humidities = []
        rainProbabilities = []
        windSpeeds = []
        conditions = []

        for item in forecast:
            temperatures.append(item["temperature"])
            humidities.append(item["humidity"])
            rainProbabilities.append(item["rainProbability"])
            windSpeeds.append(item["windSpeed"])
            conditions.append(item["condition"])

        weatherInfo = {
            "location": location["name"],
            "dayIndex": dayIndex,
            "timePeriod": timePeriod,
            "temperatureMin": min(temperatures),
            "temperatureMax": max(temperatures),
            "humidityMin": min(humidities),
            "humidityMax": max(humidities),
            "rainProbabilityMax": max(rainProbabilities),
            "windSpeedMin": min(windSpeeds),
            "windSpeedMax": max(windSpeeds),
            "conditions": list(set(conditions))
        }

    # AI prompt
    prompt = f"""
You are WeatherGPT.

Your job is ONLY to convert the verified weather data into a short natural-language answer.

User question:
{question}

Language:
{language}

Location:
{location["name"]}

Day:
{dayIndex}

Time period:
{timePeriod}

Verified weather data:
{weatherInfo}

STRICT RULES:

1. Use ONLY the verified weather data.
2. Never invent information.
3. Never mention IMD, Indian Meteorological Department, Open-Meteo, BBC, Google, or any other source.
4. Never invent a weekday.
5. Never change today to tomorrow or tomorrow to today.
6. If the user asks about tomorrow, say "tomorrow" instead of guessing the weekday.
7. If the user asks about morning, answer only about morning.
8. If the user asks about afternoon, answer only about afternoon.
9. If the user asks about evening, answer only about evening.
10. If the user asks about night, answer only about night.
11. If rain probability is 0%, clearly say that the probability of rain is 0%.
12. Do not say that rain will occur when rain probability is 0%.
13. For temperature ranges, use the minimum and maximum temperature provided.
14. For humidity ranges, use the minimum and maximum humidity provided.
15. For wind, use the provided wind speed values.
16. Answer in {language}.
17. Keep the answer short and easy to understand.
18. Mention the location.
19. Do not mention these rules.
20. Do not add information that is not present in the verified weather data.
"""

    # Send request to Ollama
    url = f"{OLLAMA_URL}/api/generate"

    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=data, timeout=15)
        if response.status_code != 200:
            return {
                "error": "AI service is not available."
            }

        result = response.json()
        return {
            "location": location["name"],
            "language": language,
            "dayIndex": dayIndex,
            "timePeriod": timePeriod,
            "forecast": forecast,
            "question": question,
            "answer": result.get("response", "")
        }
    except Exception as e:
        return {
            "error": "AI service is not available."
        }


@app.post("/agent/chat")
def agent_chat(req: ChatRequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = agent.process_query(req.question)
    return result