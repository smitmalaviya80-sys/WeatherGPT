import re

INTENTS = [
    "CURRENT_WEATHER",
    "FORECAST",
    "HOURLY_FORECAST",
    "RAIN",
    "TEMPERATURE",
    "WIND",
    "HUMIDITY",
    "SUNRISE_SUNSET",
    "HISTORICAL_WEATHER",
    "CLIMATE",
    "ALERT",
    "AGRICULTURE",
    "GENERAL_WEATHER"
]

def detect_intent(question: str, time_period: str = "full_day", day_index: int = 0) -> str:
    q = question.lower()

    if any(k in q for k in ["pesticide", "crop", "farming", "spray", "khet", "kheti", "farmer"]):
        return "AGRICULTURE"

    if any(k in q for k in ["alert", "warning", "cyclone", "storm", "tsunami", "flood", "che चेतावनी", "dharad"]):
        return "ALERT"

    if any(k in q for k in ["history", "yesterday", "last year", "last week", "past"]):
        return "HISTORICAL_WEATHER"

    if any(k in q for k in ["climate", "trend", "monthly average", "yearly average", "climate change"]):
        return "CLIMATE"

    if any(k in q for k in ["rain", "baarish", "varsad", "precipitation", "umbrella", "drizzle", "shower"]):
        return "RAIN"

    if any(k in q for k in ["temperature", "hot", "cold", "garmi", "thand", "garam", "thandu", "celsius"]):
        return "TEMPERATURE"

    if any(k in q for k in ["wind", "windy", "breeze", "pavan", "hawa"]):
        return "WIND"

    if any(k in q for k in ["humidity", "moisture", "hawa ma bhej", "bhej"]):
        return "HUMIDITY"

    if any(k in q for k in ["sunrise", "sunset", "suraj", "suryoday", "suryast"]):
        return "SUNRISE_SUNSET"

    if time_period != "full_day":
        return "HOURLY_FORECAST"

    if day_index > 0 or "forecast" in q or "next" in q or "week" in q:
        return "FORECAST"

    return "CURRENT_WEATHER"
