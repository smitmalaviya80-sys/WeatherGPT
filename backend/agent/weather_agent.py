import requests
import os
from datetime import datetime
from weather.geocoding import getLocation
from weather.weather_service import getWeather
from weather.forecast import getForecastForDay, getHourlyForecast, getWeatherDescription
from .planner import build_plan
from utils.logging_config import logger

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

class WeatherAgent:
    def process_query(self, question: str) -> dict:
        logger.info(f"Processing query through WeatherAgent: '{question}'")
        plan = build_plan(question)

        city = plan["city"]
        language = plan["language"]
        day_index = plan["day_index"]
        time_period = plan["time_period"]
        intent = plan["intent"]

        if not city or city.lower() == "none":
            no_city_msg = {
                "English": "Please specify a city name (e.g. 'What is the weather in Ahmedabad?').",
                "Hindi": "कृपया किसी शहर का नाम बताएं (जैसे: 'अहमदाबाद में मौसम कैसा है?')।",
                "Gujarati": "મહેરબાની કરીને શહેરનું નામ લખો (જેમ કે: 'અમદાવાદમાં હવામાન કેવું છે?')."
            }
            return {
                "question": question,
                "city": None,
                "language": language,
                "intent": intent,
                "source": "WeatherGPT Agent",
                "confidence": "high",
                "answer": no_city_msg.get(language, no_city_msg["English"]),
                "error": "City not specified"
            }

        location = getLocation(city)
        if not location:
            not_found_msg = {
                "English": f"Sorry, could not find location information for '{city}'.",
                "Hindi": f"क्षमा करें, '{city}' के लिए स्थान की जानकारी नहीं मिल सकी।",
                "Gujarati": f"માફ કરશો, '{city}' માટે સ્થળની માહિતી મળી નથી."
            }
            return {
                "question": question,
                "city": city,
                "language": language,
                "intent": intent,
                "source": "Open-Meteo Geocoding",
                "confidence": "low",
                "answer": not_found_msg.get(language, not_found_msg["English"]),
                "error": "City not found"
            }

        weather_data = getWeather(location["latitude"], location["longitude"])
        if not weather_data:
            fetch_err_msg = {
                "English": f"Could not fetch weather data for {location['name']} at this time.",
                "Hindi": f"{location['name']} के लिए मौसम डेटा प्राप्त नहीं हो सका।",
                "Gujarati": f"{location['name']} માટે હવામાન ડેટા મેળવી શકાયો નથી."
            }
            return {
                "question": question,
                "city": location["name"],
                "language": language,
                "intent": intent,
                "source": "Open-Meteo API",
                "confidence": "low",
                "answer": fetch_err_msg.get(language, fetch_err_msg["English"]),
                "error": "Weather data unavailable"
            }

        current = weather_data.get("current", {})
        current_weather = {
            "temperature": current.get("temperature_2m"),
            "feelsLike": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "rain": current.get("precipitation"),
            "windSpeed": current.get("wind_speed_10m"),
            "condition": getWeatherDescription(current.get("weather_code", 0))
        }

        if time_period == "full_day":
            forecast = getForecastForDay(weather_data, day_index)
            weather_info = {
                "location": location["name"],
                "date": forecast["date"] if forecast else "N/A",
                "condition": forecast["condition"] if forecast else current_weather["condition"],
                "maxTemperature": forecast["maxTemperature"] if forecast else current_weather["temperature"],
                "minTemperature": forecast["minTemperature"] if forecast else current_weather["temperature"],
                "rainProbability": forecast["rainProbability"] if forecast else 0,
                "rainAmount": forecast["rainAmount"] if forecast else 0,
                "maxWindSpeed": forecast["maxWindSpeed"] if forecast else current_weather["windSpeed"],
                "sunrise": forecast["sunrise"] if forecast else "N/A",
                "sunset": forecast["sunset"] if forecast else "N/A",
                "current": current_weather
            }
        else:
            forecast = getHourlyForecast(weather_data, day_index, time_period)
            if forecast:
                temps = [item["temperature"] for item in forecast]
                hums = [item["humidity"] for item in forecast]
                rains = [item["rainProbability"] for item in forecast]
                winds = [item["windSpeed"] for item in forecast]
                conds = list(set([item["condition"] for item in forecast]))

                weather_info = {
                    "location": location["name"],
                    "dayIndex": day_index,
                    "timePeriod": time_period,
                    "temperatureMin": min(temps),
                    "temperatureMax": max(temps),
                    "humidityMin": min(hums),
                    "humidityMax": max(hums),
                    "rainProbabilityMax": max(rains),
                    "windSpeedMin": min(winds),
                    "windSpeedMax": max(winds),
                    "conditions": conds,
                    "current": current_weather
                }
            else:
                weather_info = {
                    "location": location["name"],
                    "dayIndex": day_index,
                    "timePeriod": time_period,
                    "current": current_weather
                }

        # Sector specific advisory guidance if applicable
        advisory_context = ""
        if intent == "AGRICULTURE":
            advisory_context = "User is asking an agriculture / farming question. Provide practical weather advice for farmers based strictly on the rain, wind, and temperature values."

        prompt = f"""
You are WeatherGPT, an advanced AI weather assistant.

User Question:
{question}

Language to Respond In:
{language}

Location:
{location["name"]}

Intent Detected:
{intent}

Verified Weather Data:
{weather_info}

{advisory_context}

STRICT GROUNDING RULES:
1. Use ONLY the verified weather data provided above.
2. Never invent temperature, rainfall, or weather details.
3. Do not mention source names (Open-Meteo, IMD, etc.) in your spoken text unless asked.
4. If rain probability is 0%, state clearly that there is 0% chance of rain.
5. If intent is AGRICULTURE, advise whether conditions (wind speed, rain probability) are suitable for farming/spraying based on data.
6. Answer in {language}.
7. Keep the response concise, informative, and easy to understand.
"""

        answer = None
        try:
            url = f"{OLLAMA_URL}/api/generate"
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                answer = res.json().get("response", "").strip()
        except Exception as e:
            logger.warning(f"Ollama generation unavailable or timed out: {e}")

        # Structured fallback response if LLM is unavailable
        if not answer:
            if time_period == "full_day" and forecast:
                answer = (
                    f"Weather for {location['name']} on {forecast['date']}: "
                    f"Condition: {forecast['condition']}, Max Temp: {forecast['maxTemperature']}°C, "
                    f"Min Temp: {forecast['minTemperature']}°C, Rain Probability: {forecast['rainProbability']}%, "
                    f"Max Wind: {forecast['maxWindSpeed']} km/h."
                )
            else:
                answer = (
                    f"Current Weather in {location['name']}: "
                    f"Condition: {current_weather['condition']}, Temp: {current_weather['temperature']}°C, "
                    f"Humidity: {current_weather['humidity']}%, Rain: {current_weather['rain']} mm, "
                    f"Wind: {current_weather['windSpeed']} km/h."
                )

        return {
            "question": question,
            "intent": intent,
            "location": location["name"],
            "coordinates": {
                "latitude": location["latitude"],
                "longitude": location["longitude"]
            },
            "language": language,
            "day_index": day_index,
            "time_period": time_period,
            "source": "Open-Meteo API",
            "confidence": "high",
            "data_time": datetime.utcnow().isoformat() + "Z",
            "answer": answer,
            "verified_data": weather_info,
            "forecast_details": forecast
        }

weather_agent = WeatherAgent()
