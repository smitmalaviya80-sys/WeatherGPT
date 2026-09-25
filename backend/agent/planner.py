from weather.parser import extractCity, detectLanguage, detectDay, detectTimePeriod
from .intent import detect_intent

def build_plan(question: str) -> dict:
    city = extractCity(question)
    language = detectLanguage(question)
    day_index = detectDay(question)
    time_period = detectTimePeriod(question)
    intent = detect_intent(question, time_period=time_period, day_index=day_index)

    return {
        "question": question,
        "city": city,
        "language": language,
        "day_index": day_index,
        "time_period": time_period,
        "intent": intent,
        "tools_required": ["geocoding", "weather_service", "forecast_extractor"]
    }
