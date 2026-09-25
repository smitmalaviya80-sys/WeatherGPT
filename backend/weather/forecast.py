def getWeatherDescription(weatherCode: int) -> str:
    weatherCodes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weatherCodes.get(weatherCode, "Unknown weather")

def getForecastForDay(weatherData: dict, dayIndex: int):
    if not weatherData or "daily" not in weatherData:
        return None

    daily = weatherData["daily"]

    if dayIndex >= len(daily["time"]):
        return None

    return {
        "date": daily["time"][dayIndex],
        "condition": getWeatherDescription(daily["weather_code"][dayIndex]),
        "maxTemperature": daily["temperature_2m_max"][dayIndex],
        "minTemperature": daily["temperature_2m_min"][dayIndex],
        "rainProbability": daily["precipitation_probability_max"][dayIndex],
        "rainAmount": daily["precipitation_sum"][dayIndex],
        "maxWindSpeed": daily["wind_speed_10m_max"][dayIndex],
        "sunrise": daily["sunrise"][dayIndex],
        "sunset": daily["sunset"][dayIndex]
    }

def getHourlyForecast(weatherData: dict, dayIndex: int, timePeriod: str):
    if not weatherData or "hourly" not in weatherData:
        return None

    hourly = weatherData["hourly"]
    startIndex = dayIndex * 24

    if timePeriod == "morning":
        startHour = 6
        endHour = 12
    elif timePeriod == "afternoon":
        startHour = 12
        endHour = 18
    elif timePeriod == "evening":
        startHour = 18
        endHour = 21
    elif timePeriod == "night":
        startHour = 21
        endHour = 24
    else:
        startHour = 0
        endHour = 24

    forecast = []
    total_hours = len(hourly.get("time", []))

    for hour in range(startHour, endHour):
        index = startIndex + hour
        if index >= total_hours:
            break

        forecast.append({
            "time": hourly["time"][index],
            "temperature": hourly["temperature_2m"][index],
            "humidity": hourly["relative_humidity_2m"][index],
            "rainProbability": hourly["precipitation_probability"][index],
            "rainAmount": hourly["precipitation"][index],
            "condition": getWeatherDescription(hourly["weather_code"][index]),
            "windSpeed": hourly["wind_speed_10m"][index]
        })

    return forecast
