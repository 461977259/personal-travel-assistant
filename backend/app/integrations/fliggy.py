"""
飞猪AI开放平台接口框架。
API Docs: https://open.alitrip.com
当前阶段：MVP 使用 mock 数据，真实 API Key 注册后切换。
"""
import os
import httpx

FLIGGY_BASE_URL = "https://open.alitrip.com"


def _is_mock_mode() -> bool:
    """Check if mock mode is enabled."""
    return os.getenv("FLIGGY_MOCK_MODE", "true").lower() == "true"


async def _call_fliggy(url: str, params: dict) -> dict:
    """Make a real call to Fliggy API (when key is available)."""
    key = os.getenv("FLIGGY_KEY", "")
    headers = {"Authorization": f"Bearer {key}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


async def search_flights(origin: str, destination: str, date: str) -> list[dict]:
    """
    Search flights between two cities on a given date.
    Returns list of flight options with price, airline, duration, etc.
    """
    if _is_mock_mode():
        return _mock_flights(origin, destination, date)

    params = {
        "origin": origin,
        "destination": destination,
        "date": date,
    }
    result = await _call_fliggy(f"{FLIGGY_BASE_URL}/api/flights/search", params)
    return result.get("flights", [])


async def search_trains(origin: str, destination: str, date: str) -> list[dict]:
    """
    Search high-speed trains between two cities on a given date.
    Returns list of train options with price, departure/arrival times, duration, etc.
    """
    if _is_mock_mode():
        return _mock_trains(origin, destination, date)

    params = {
        "departure": origin,
        "arrival": destination,
        "date": date,
    }
    result = await _call_fliggy(f"{FLIGGY_BASE_URL}/api/trains/search", params)
    return result.get("trains", [])


async def search_hotels(city: str, checkin: str, checkout: str) -> list[dict]:
    """
    Search hotels in a city for given check-in/check-out dates.
    Returns list of hotel options with price, rating, amenities, etc.
    """
    if _is_mock_mode():
        return _mock_hotels(city, checkin, checkout)

    params = {
        "city": city,
        "checkin": checkin,
        "checkout": checkout,
    }
    result = await _call_fliggy(f"{FLIGGY_BASE_URL}/api/hotels/search", params)
    return result.get("hotels", [])


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

def _mock_flights(origin: str, destination: str, date: str) -> list[dict]:
    """Return realistic mock flight data."""
    return [
        {
            "flight_no": "CA1234",
            "airline": "中国国航",
            "airline_code": "CA",
            "origin": origin,
            "destination": destination,
            "departure_time": "08:30",
            "arrival_time": "11:00",
            "duration_minutes": 150,
            "price": 980.0,
            "price_unit": "CNY",
            "seats_available": 20,
            "stop_count": 0,
            "cabin": "经济舱",
            "date": date,
        },
        {
            "flight_no": "MU5678",
            "airline": "东方航空",
            "airline_code": "MU",
            "origin": origin,
            "destination": destination,
            "departure_time": "14:15",
            "arrival_time": "16:45",
            "duration_minutes": 150,
            "price": 1050.0,
            "price_unit": "CNY",
            "seats_available": 5,
            "stop_count": 0,
            "cabin": "经济舱",
            "date": date,
        },
        {
            "flight_no": "CZ9012",
            "airline": "南方航空",
            "airline_code": "CZ",
            "origin": origin,
            "destination": destination,
            "departure_time": "19:30",
            "arrival_time": "23:00",
            "duration_minutes": 150,
            "price": 890.0,
            "price_unit": "CNY",
            "seats_available": 12,
            "stop_count": 1,
            "cabin": "经济舱",
            "date": date,
        },
    ]


def _mock_trains(origin: str, destination: str, date: str) -> list[dict]:
    """Return realistic mock train data."""
    return [
        {
            "train_no": "G1234",
            "train_type": "高铁",
            "origin": origin,
            "destination": destination,
            "departure_time": "07:00",
            "arrival_time": "11:30",
            "duration_minutes": 270,
            "price": 553.0,
            "price_unit": "CNY",
            "seats_available": 45,
            "date": date,
        },
        {
            "train_no": "G5678",
            "train_type": "高铁",
            "origin": origin,
            "destination": destination,
            "departure_time": "12:30",
            "arrival_time": "17:00",
            "duration_minutes": 270,
            "price": 553.0,
            "price_unit": "CNY",
            "seats_available": 20,
            "date": date,
        },
        {
            "train_no": "D9012",
            "train_type": "动车",
            "origin": origin,
            "destination": destination,
            "departure_time": "18:00",
            "arrival_time": "22:30",
            "duration_minutes": 270,
            "price": 499.0,
            "price_unit": "CNY",
            "seats_available": 8,
            "date": date,
        },
    ]


def _mock_hotels(city: str, checkin: str, checkout: str) -> list[dict]:
    """Return realistic mock hotel data."""
    return [
        {
            "hotel_id": "HTL001",
            "name": f"{city}中心大酒店",
            "star_rating": 4,
            "address": f"{city}市朝阳区中心路88号",
            "latitude": 39.9088,
            "longitude": 116.3974,
            "price": 458.0,
            "price_unit": "CNY/晚",
            "checkin": checkin,
            "checkout": checkout,
            "rating": 4.5,
            "review_count": 1230,
            "amenities": ["免费WiFi", "早餐", "停车场", "健身房"],
            "thumbnail": "https://example.com/hotel1.jpg",
        },
        {
            "hotel_id": "HTL002",
            "name": f"{city}国际机场酒店",
            "star_rating": 5,
            "address": f"{city}市机场经济区1号",
            "latitude": 39.9150,
            "longitude": 116.4100,
            "price": 899.0,
            "price_unit": "CNY/晚",
            "checkin": checkin,
            "checkout": checkout,
            "rating": 4.7,
            "review_count": 890,
            "amenities": ["免费WiFi", "机场接送", "游泳池", "行政酒廊"],
            "thumbnail": "https://example.com/hotel2.jpg",
        },
        {
            "hotel_id": "HTL003",
            "name": f"{city}古韵客栈",
            "star_rating": 3,
            "address": f"{city}市老城区南锣鼓巷12号",
            "latitude": 39.9200,
            "longitude": 116.4000,
            "price": 228.0,
            "price_unit": "CNY/晚",
            "checkin": checkin,
            "checkout": checkout,
            "rating": 4.3,
            "review_count": 450,
            "amenities": ["免费WiFi", "早餐"],
            "thumbnail": "https://example.com/hotel3.jpg",
        },
    ]
