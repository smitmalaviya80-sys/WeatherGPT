from fastapi import FastAPI
import requests
from weather import getWeather, getLocation

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "WeatherGPT API is running"
    }


@app.get("/ask")
def ask(question: str):

    url = "http://localhost:11434/api/generate"

    data = {
        "model": "llama3.2:3b",
        "prompt": question,
        "stream": False
    }

    response = requests.post(url, json=data)

    result = response.json()

    return {
        "question": question,
        "answer": result["response"]
    }


@app.get("/chat")
def chat(question: str, latitude: float, longitude: float):

    weatherData = getWeather(latitude, longitude)

    prompt = f"""
You are WeatherGPT.

Answer the user's weather question using ONLY the weather data provided below.

Weather data:
{weatherData}

User question:
{question}

Do not invent weather information.
Give a simple and clear answer.
"""

    url = "http://localhost:11434/api/generate"

    data = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data)

    result = response.json()

    return {
        "question": question,
        "answer": result["response"]
    }
@app.get("/weatherChat")
def weatherChat(question: str, city: str):

    location = getLocation(city)

    if location is None:
        return {
            "error": "City not found"
        }

    weatherData = getWeather(
        location["latitude"],
        location["longitude"]
    )

    prompt = f"""
You are WeatherGPT.

The user asked:
{question}

Location:
{location["name"]}

Real weather data:
{weatherData}

Answer the user's question using ONLY the weather data provided.

Do not invent weather information.
Keep the answer simple and useful.
"""

    url = "http://localhost:11434/api/generate"

    data = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data)

    result = response.json()

    return {
        "location": location["name"],
        "question": question,
        "answer": result["response"]
    }