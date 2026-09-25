import requests
from utils.cache import cache
from utils.logging_config import logger

def getLocation(city: str):
    if not city or city.lower() == "none":
        return None

    cache_key = f"location_{city.strip().lower()}"
    cached = cache.get(cache_key)
    if cached:
        logger.info(f"Cache hit for geocoding city={city}")
        return cached

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            logger.error(f"Geocoding API returned status {response.status_code}")
            return None

        data = response.json()
        if "results" not in data or not data["results"]:
            return None

        location = data["results"][0]
        result = {
            "name": location["name"],
            "latitude": location["latitude"],
            "longitude": location["longitude"]
        }
        cache.set(cache_key, result, ttl=3600)  # Cache location for 1 hour
        return result
    except Exception as e:
        logger.error(f"Error fetching location for {city}: {e}")
        return None
