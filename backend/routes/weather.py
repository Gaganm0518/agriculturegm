"""
Weather Routes.
Provides an API endpoint to fetch real-time weather data.
"""

from flask import Blueprint, request
from backend.services.weather_service import WeatherService
from backend.utils.helpers import api_response, api_error

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/', methods=['GET'])
def get_weather():
    """
    GET /api/weather?lat=...&lon=...  OR  GET /api/weather?city=...
    Returns current weather data for the given location.
    """
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    city = request.args.get('city')

    # Validate: need either lat+lon or city
    if (lat is None or lon is None) and not city:
        return api_error("Provide either 'lat' & 'lon' query params or a 'city' name.", 400)

    # Validate numeric lat/lon
    if lat is not None and lon is not None:
        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            return api_error("'lat' and 'lon' must be valid numbers.", 400)

        if not (-90 <= lat <= 90):
            return api_error("'lat' must be between -90 and 90.", 400)
        if not (-180 <= lon <= 180):
            return api_error("'lon' must be between -180 and 180.", 400)

    service = WeatherService()
    result = service.get_weather(lat=lat, lon=lon, city=city)

    if result.get('success'):
        return api_response(data=result, message="Weather data retrieved successfully")
    else:
        return api_response(
            data=result,
            message=result.get('message', 'Could not fetch weather data'),
            status_code=200  # Still 200 — the API responded, just with fallback data
        )
