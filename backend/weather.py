# Weather Module Facade for Backward Compatibility
from weather.weather_service import getWeather
from weather.geocoding import getLocation
from weather.forecast import getWeatherDescription, getForecastForDay, getHourlyForecast
from weather.parser import extractCity, detectLanguage, detectDay, detectTimePeriod

__all__ = [
    "getWeather",
    "getLocation",
    "extractCity",
    "detectLanguage",
    "getWeatherDescription",
    "getForecastForDay",
    "detectDay",
    "detectTimePeriod",
    "getHourlyForecast"
]