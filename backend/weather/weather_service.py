import requests
from utils.cache import cache
from utils.logging_config import logger

def getWeather(latitude: float, longitude: float):
    cache_key = f"weather_{latitude:.4f}_{longitude:.4f}"
    cached = cache.get(cache_key)
    if cached:
        logger.info(f"Cache hit for weather lat={latitude}, lon={longitude}")
        return cached

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,sunrise,sunset",
        "forecast_days": 7,
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            logger.error(f"Open-Meteo returned status {response.status_code}")
            return None

        data = response.json()
        cache.set(cache_key, data)
        return data
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        return None
