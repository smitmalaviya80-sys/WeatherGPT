import re
import requests
import os
from utils.logging_config import logger

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

KNOWN_CITIES = [
    "ahmedabad", "mumbai", "delhi", "bengaluru", "bangalore", "kolkata", "chennai", "hyderabad",
    "pune", "surat", "jaipur", "lucknow", "kanpur", "nagpur", "indore", "thane", "bhopal",
    "visakhapatnam", "vadodara", "firozabad", "ludhiana", "rajkot", "agra", "siliguri",
    "nashik", "faridabad", "patiala", "meerut", "kalyan", "vasai", "varanasi", "srinagar",
    "dhanbad", "amritsar", "navi mumbai", "allahabad", "prayagraj", "ranchi", "howrah",
    "coimbatore", "jabalpur", "gwalior", "vijayawada", "jodhpur", "madurai", "raipur",
    "kota", "guwahati", "chandigarh", "solapur", "hubli", "bareilly", "moradabad", "mysore",
    "london", "new york", "tokyo", "paris", "sydney", "berlin", "dubai", "singapore"
]

def extractCity(question: str) -> str:
    question_lower = question.lower()
    for city in KNOWN_CITIES:
        pattern = r'\b' + re.escape(city) + r'\b'
        if re.search(pattern, question_lower):
            return city.capitalize()

    prompt = f"""
Extract only the city name from this question.

Question:
{question}

Return only the city name.

If there is no city, return None.
"""

    try:
        url = f"{OLLAMA_URL}/api/generate"
        data = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            city = result.get("response", "").strip()
            city_cleaned = re.sub(r'[^a-zA-Z\s]', '', city).strip()
            if city_cleaned.lower() in ["none", "null", "not specified", "no city"]:
                return "None"
            return city_cleaned
    except Exception as e:
        logger.warning(f"Ollama city extraction failed, falling back to heuristics: {e}")

    return "None"

def detectLanguage(question: str) -> str:
    questionLower = question.lower()

    gujaratiWords = [
        "chhe", "chhe?", "aaje", "kaale", "aavti", "havaaman", "varsad", "ketlu", "kevu", "thase", "savare", "bapore", "sanje", "raatre"
    ]

    hindiWords = [
        "mein", "kaisa", "kaisi", "kaise", "aaj", "kal", "mausam", "baarish", "hoga", "hogi", "kitna", "kitni", "batao", "bataiye"
    ]

    for word in gujaratiWords:
        if re.search(r'\b' + re.escape(word) + r'\b', questionLower):
            return "Gujarati"

    for word in hindiWords:
        if re.search(r'\b' + re.escape(word) + r'\b', questionLower):
            return "Hindi"

    return "English"

def detectDay(question: str) -> int:
    questionLower = question.lower()

    if "aavti kale" in questionLower or "tomorrow" in questionLower or "kal" in questionLower:
        return 1

    if "today" in questionLower or "aaje" in questionLower or "aaj" in questionLower:
        return 0

    return 0

def detectTimePeriod(question: str) -> str:
    questionLower = question.lower()

    if "morning" in questionLower or "savare" in questionLower or "subah" in questionLower:
        return "morning"

    if "afternoon" in questionLower or "bapore" in questionLower or "dopahar" in questionLower:
        return "afternoon"

    if "evening" in questionLower or "sanje" in questionLower or "shaam" in questionLower:
        return "evening"

    if "night" in questionLower or "raatre" in questionLower or "raat" in questionLower:
        return "night"

    return "full_day"
