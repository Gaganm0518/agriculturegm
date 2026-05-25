"""
Weather Service.
Integrates with OpenWeatherMap API to fetch real-time weather data.
Uses Flask-Caching to avoid excessive API calls (30-minute TTL).
"""

import os
import requests
import logging
from backend.extensions import cache

logger = logging.getLogger(__name__)


class WeatherService:
    """Service class for fetching weather data from OpenWeatherMap."""

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY', '')

    def _build_params(self, lat=None, lon=None, city=None):
        """Build query parameters for the API request."""
        params = {
            'appid': self.api_key,
            'units': 'metric'  # Celsius
        }
        if lat is not None and lon is not None:
            params['lat'] = lat
            params['lon'] = lon
        elif city:
            params['q'] = city
        else:
            raise ValueError("Provide either lat/lon or city name.")
        return params

    @staticmethod
    def _make_cache_key(lat=None, lon=None, city=None):
        """Generate a deterministic cache key from the query parameters."""
        if lat is not None and lon is not None:
            # Round to 2 decimal places so nearby coords share cache
            return f"weather:{round(float(lat), 2)}:{round(float(lon), 2)}"
        return f"weather:city:{city}"

    def get_weather(self, lat=None, lon=None, city=None):
        """
        Fetch weather data. Returns a dict with temperature, humidity,
        rainfall, description, and wind_speed. Cached for 30 minutes.
        """
        cache_key = self._make_cache_key(lat=lat, lon=lon, city=city)

        # Check cache first
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Weather cache HIT for key: {cache_key}")
            return cached

        # Validate API key
        if not self.api_key or self.api_key == 'your_openweathermap_key_here':
            logger.warning("No valid WEATHER_API_KEY configured, returning fallback.")
            return self._fallback_response("Weather API key not configured. Please set WEATHER_API_KEY in .env")

        try:
            params = self._build_params(lat=lat, lon=lon, city=city)
            logger.info(f"Fetching weather from OpenWeatherMap: {params}")
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            result = self._parse_response(data)

            # Cache for 30 minutes (1800 seconds)
            cache.set(cache_key, result, timeout=1800)
            logger.info(f"Weather cache SET for key: {cache_key}")

            return result

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else 'unknown'
            logger.error(f"OpenWeatherMap HTTP error ({status}): {e}")
            if status == 401:
                return self._fallback_response("Invalid API key. Check WEATHER_API_KEY in .env")
            if status == 404:
                return self._fallback_response("Location not found. Try different coordinates or city name.")
            return self._fallback_response(f"Weather API returned error {status}")

        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to OpenWeatherMap API")
            return self._fallback_response("Unable to reach weather service. Check your internet connection.")

        except requests.exceptions.Timeout:
            logger.error("OpenWeatherMap API request timed out")
            return self._fallback_response("Weather service timed out. Please try again.")

        except Exception as e:
            logger.error(f"Unexpected weather service error: {e}")
            return self._fallback_response("An unexpected error occurred fetching weather data.")

    def _parse_response(self, data):
        """Parse the OpenWeatherMap JSON response into our standard format."""
        # Rainfall: OWM stores rain in the last 1h or 3h under data.rain
        rain_data = data.get('rain', {})
        rainfall_mm = rain_data.get('1h', rain_data.get('3h', 0.0))

        weather_desc = data.get('weather', [{}])[0].get('description', 'N/A')
        icon_code = data.get('weather', [{}])[0].get('icon', '01d')

        return {
            'success': True,
            'temperature': round(data['main']['temp'], 1),
            'humidity': round(data['main']['humidity'], 1),
            'rainfall': round(rainfall_mm, 1),
            'description': weather_desc.capitalize(),
            'wind_speed': round(data.get('wind', {}).get('speed', 0), 1),
            'feels_like': round(data['main'].get('feels_like', data['main']['temp']), 1),
            'pressure': data['main'].get('pressure', 0),
            'city': data.get('name', 'Unknown'),
            'country': data.get('sys', {}).get('country', ''),
            'icon': f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        }

    @staticmethod
    def _fallback_response(message):
        """Return a standardized error/fallback response."""
        return {
            'success': False,
            'message': message,
            'temperature': None,
            'humidity': None,
            'rainfall': None,
            'description': 'Unavailable',
            'wind_speed': None
        }
