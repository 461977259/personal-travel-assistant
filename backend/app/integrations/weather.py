"""
HeFeng Weather API integration.
API Docs: https://dev.qweather.com/docs/api/
"""
import os
import httpx

HEFENG_BASE_URL = "https://devapi.qweather.com"
GEO_BASE_URL = "https://geoapi.qweather.com"


def _is_mock_mode() -> bool:
    """Check if mock mode is enabled via environment variable."""
    return os.getenv("WEATHER_MOCK_MODE", "true").lower() == "true"


async def _call_hefeng(url: str, params: dict) -> dict:
    """Make a real call to HeFeng API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def get_geo(city: str) -> dict:
    """
    Convert city name to coordinates using HeFeng Geocoding API.
    Returns {"lat": float, "lon": float, "name": str}
    """
    if _is_mock_mode():
        return _mock_geo(city)

    key = os.getenv("HEFENG_WEATHER_KEY", "")
    params = {
        "key": key,
        "location": city,
        "adm": "北京",  # default to Beijing
    }
    result = await _call_hefeng(f"{GEO_BASE_URL}/v2/city/lookup", params)
    # {"code": "200", "location": [{"lat": "39.904", "lon": "116.391", "name": "北京", ...}]}
    location = result.get("location", [{}])[0]
    return {
        "lat": float(location.get("lat", 0)),
        "lon": float(location.get("lon", 0)),
        "name": location.get("name", city),
    }


async def get_weather(city: str) -> dict:
    """
    Get current weather for a city.
    Returns: {temperature, wind_speed, wind_direction, humidity, precipitation, condition, icon}
    """
    if _is_mock_mode():
        return _mock_weather(city)

    geo = await get_geo(city)
    key = os.getenv("HEFENG_WEATHER_KEY", "")
    params = {
        "key": key,
        "location": f"{geo['lon']},{geo['lat']}",
    }
    result = await _call_hefeng(f"{HEFENG_BASE_URL}/v7/weather/now", params)
    now = result.get("now", {})
    return {
        "temperature": float(now.get("temp", 0)),
        "wind_speed": float(now.get("windSpeed", 0)),
        "wind_direction": now.get("windDir", ""),
        "humidity": float(now.get("humidity", 0)),
        "precipitation": float(now.get("precip", 0)),
        "condition": now.get("text", ""),
        "icon": now.get("icon", ""),
        "city": city,
    }


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

def _mock_geo(city: str) -> dict:
    """Return mock geo data for common Chinese cities."""
    mock_cities = {
        "北京": {"lat": 39.904, "lon": 116.391, "name": "北京"},
        "上海": {"lat": 31.230, "lon": 121.474, "name": "上海"},
        "广州": {"lat": 23.129, "lon": 113.264, "name": "广州"},
        "深圳": {"lat": 22.543, "lon": 114.058, "name": "深圳"},
        "杭州": {"lat": 30.274, "lon": 120.155, "name": "杭州"},
        "成都": {"lat": 30.572, "lon": 104.065, "name": "成都"},
        "西安": {"lat": 34.341, "lon": 108.940, "name": "西安"},
        "重庆": {"lat": 29.563, "lon": 106.551, "name": "重庆"},
    }
    return mock_cities.get(city, {"lat": 39.904, "lon": 116.391, "name": city})


def _mock_weather(city: str) -> dict:
    """Return realistic mock weather data."""
    geo = _mock_geo(city)
    # Available conditions: 晴, 多云, 阴, 小雨, 阵雨, 雷阵雨
    return {
        "temperature": 22.5,
        "wind_speed": 12.0,
        "wind_direction": "东南风",
        "humidity": 65.0,
        "precipitation": 0.0,
        "condition": "多云",
        "icon": "101",
        "city": geo["name"],
    }
