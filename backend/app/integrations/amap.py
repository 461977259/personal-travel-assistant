"""
高德地图开放平台 API 集成。
API Docs: https://lbs.amap.com
"""
import os
import httpx
from typing import Optional

AMAP_BASE_URL = "https://restapi.amap.com"


def _is_mock_mode() -> bool:
    """Check if mock mode is enabled."""
    return os.getenv("AMAP_MOCK_MODE", "true").lower() == "true"


def _get_amap_key() -> str:
    """Get AMap API key from environment variable."""
    key = os.getenv("AMAP_KEY", "")
    if not key:
        raise ValueError("AMAP_KEY environment variable is not set")
    return key


async def _call_amap(path: str, params: dict) -> dict:
    """Make a real call to AMap API."""
    key = _get_amap_key()
    params["key"] = key
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{AMAP_BASE_URL}{path}", params=params)
        response.raise_for_status()
        return response.json()


async def search_poi(keyword: str, city: Optional[str] = None) -> list[dict]:
    """
    Search POIs (Points of Interest) by keyword.
    Returns list of POIs with name, address, location, type, etc.
    """
    if _is_mock_mode():
        return _mock_pois(keyword, city)

    params = {
        "keywords": keyword,
        "city": city or "",
        "output": "json",
    }
    result = await _call_amap("/v5/place/text", params)
    pois = result.get("pois", [])
    return [_parse_poi(p) for p in pois]


async def get_route(
    origin: str,
    destination: str,
    mode: str = "walking",
) -> dict:
    """
    Get route between two locations.
    mode: walking | bus | driving
    Returns: {distance, duration, steps}
    """
    if _is_mock_mode():
        return _mock_route(origin, destination, mode)

    path_map = {
        "walking": "/v5/direction/walking",
        "driving": "/v5/direction/driving",
        "bus": "/v5/direction/transit/integrated",
    }
    path = path_map.get(mode, path_map["walking"])
    params = {
        "origin": origin,
        "destination": destination,
    }
    result = await _call_amap(path, params)
    return _parse_route(result, mode)


async def get_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate straight-line distance between two points (in meters).
    Uses Haversine formula for mock mode.
    """
    if _is_mock_mode():
        return _haversine_distance(lat1, lon1, lat2, lon2)

    params = {
        "origins": f"{lon1},{lat1}",
        "destination": f"{lon2},{lat2}",
        "type": 1,  # straight line
    }
    result = await _call_amap("/v5/distance", params)
    results = result.get("results", [])
    if results:
        return float(results[0].get("distance", 0))
    return 0.0


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

def _mock_pois(keyword: str, city: Optional[str]) -> list[dict]:
    """Return realistic mock POI data."""
    mock_data = {
        "景点": [
            {
                "id": "POI001",
                "name": f"{city}故宫博物院" if city else "故宫博物院",
                "address": "北京市东城区景山前街4号",
                "location": "116.3974,39.9088",
                "type": "景点",
                "distance": 0,
            },
            {
                "id": "POI002",
                "name": f"{city}天坛公园" if city else "天坛公园",
                "address": "北京市东城区天坛东路甲1号",
                "location": "116.4100,39.8800",
                "type": "景点",
                "distance": 0,
            },
        ],
        "餐厅": [
            {
                "id": "POI003",
                "name": f"{city}全聚德烤鸭店" if city else "全聚德烤鸭店",
                "address": "北京市东城区前门大街30号",
                "location": "116.3950,39.9050",
                "type": "餐厅",
                "distance": 0,
            },
        ],
        "酒店": [
            {
                "id": "POI004",
                "name": f"{city}贵宾楼饭店" if city else "贵宾楼饭店",
                "address": "北京市东城区东长安街35号",
                "location": "116.4100,39.9050",
                "type": "酒店",
                "distance": 0,
            },
        ],
    }
    for category, pois in mock_data.items():
        if category in keyword:
            return pois
    return [
        {
            "id": "POI999",
            "name": f"{city}{keyword}推荐地点" if city else f"{keyword}推荐地点",
            "address": "地址未知",
            "location": "116.3974,39.9088",
            "type": "未知",
            "distance": 0,
        }
    ]


def _mock_route(origin: str, destination: str, mode: str) -> dict:
    """Return realistic mock route data."""
    return {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "distance": 3500,
        "distance_text": "3.5公里",
        "duration": 2520,
        "duration_text": "约42分钟",
        "steps": [
            {
                "instruction": "从起点向东南方向出发",
                "road": "长安街",
                "distance": 500,
                "duration": 360,
            },
            {
                "instruction": "左转进入东单北大街",
                "road": "东单北大街",
                "distance": 1200,
                "duration": 900,
            },
            {
                "instruction": "右转进入景山前街",
                "road": "景山前街",
                "distance": 1800,
                "duration": 1260,
            },
            {
                "instruction": "到达目的地",
                "road": "",
                "distance": 0,
                "duration": 0,
            },
        ],
    }


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points (in meters)."""
    import math
    R = 6371000  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _parse_poi(poi: dict) -> dict:
    """Parse AMap POI response to simplified format."""
    return {
        "id": poi.get("id", ""),
        "name": poi.get("name", ""),
        "address": poi.get("address", ""),
        "location": poi.get("location", ""),
        "type": poi.get("type", ""),
        "distance": poi.get("distance", ""),
    }


def _parse_route(result: dict, mode: str) -> dict:
    """Parse AMap route response to simplified format."""
    paths = result.get("paths", [{}])
    path = paths[0] if paths else {}
    return {
        "distance": int(path.get("distance", 0)),
        "duration": int(path.get("duration", 0)),
        "steps": [
            {
                "instruction": step.get("instruction", ""),
                "road": step.get("road_name", ""),
                "distance": int(step.get("distance", 0)),
                "duration": int(step.get("duration", 0)),
            }
            for step in path.get("steps", [])
        ],
    }
