"""
Trip Generation Engine.
Generates multi-day travel itineraries with attractions, routes, weather, and outfit recommendations.
"""
import math
from datetime import datetime, timedelta
from typing import Optional

from app.integrations.amap import search_poi, get_route
from app.integrations.weather import get_weather
from app.services.outfit_engine import recommend_outfit


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default visit duration per POI type (in minutes)
VISIT_DURATION = {
    "景点": 180,   # 3 hours for scenic spots
    "博物馆": 150,  # 2.5 hours for museums
    "公园": 90,    # 1.5 hours for parks
    "餐厅": 60,    # 1 hour for restaurants
    "购物": 60,    # 1 hour for shopping
    "酒店": 30,    # 30 min for hotel check-in
    "未知": 120,   # 2 hours default
}

# Typical daily schedule
DAY_START_HOUR = 9   # 9 AM
DAY_END_HOUR = 21     # 9 PM
BREAKFAST_HOUR = 8
LUNCH_HOUR = 12
DINNER_HOUR = 18

# Scene mapping for outfit engine
OUTFIT_SCENES = {
    "城市漫游": "休闲",
    "户外徒步": "运动",
    "美食打卡": "休闲",
    "景点游览": "旅行",
    "商务出行": "商务",
    "海边度假": "休闲",
    "古镇探索": "旅行",
}


# ---------------------------------------------------------------------------
# POI clustering
# ---------------------------------------------------------------------------

def _parse_location(location_str: str) -> tuple[float, float]:
    """Parse 'lon,lat' string to (lon, lat)."""
    try:
        parts = location_str.split(",")
        return float(parts[0]), float(parts[1])
    except (ValueError, IndexError):
        return 0.0, 0.0


def _calculate_distance(loc1: str, loc2: str) -> float:
    """Calculate straight-line distance between two locations in meters."""
    lon1, lat1 = _parse_location(loc1)
    lon2, lat2 = _parse_location(loc2)
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _cluster_pois_by_proximity(
    pois: list[dict],
    max_per_day: int = 5,
    max_distance_km: float = 10.0,
) -> list[list[dict]]:
    """
    Cluster POIs into groups based on geographic proximity.
    Uses a greedy algorithm: start with the northernmost POI and add nearby POIs.
    """
    if not pois:
        return []

    # Filter out POIs without valid locations
    valid_pois = [p for p in pois if p.get("location")]
    if not valid_pois:
        return [pois[:max_per_day]] if pois else []

    clusters = []
    remaining = valid_pois.copy()

    while remaining:
        # Start a new cluster with the northernmost POI (highest lat)
        current_cluster = [remaining[0]]
        remaining = remaining[1:]

        # Add POIs that are within max_distance_km of any POI in the cluster
        added = True
        while added:
            added = False
            to_add = []
            for poi in remaining:
                # Check distance to all POIs in cluster
                min_dist = min(
                    _calculate_distance(poi["location"], cp["location"])
                    for cp in current_cluster
                )
                if min_dist <= max_distance_km * 1000:
                    to_add.append(poi)
            for poi in to_add:
                current_cluster.append(poi)
                remaining.remove(poi)
                added = True

        clusters.append(current_cluster)

    # If we have too few clusters, merge or split
    # If we have too many, consolidate the smallest clusters
    while len(clusters) > max_per_day:
        # Find the two closest clusters and merge them
        min_dist = float("inf")
        merge_idx = None
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                dist = min(
                    _calculate_distance(pois1["location"], pois2["location"])
                    for pois1 in clusters[i]
                    for pois2 in clusters[j]
                )
                if dist < min_dist:
                    min_dist = dist
                    merge_idx = (i, j)

        if merge_idx:
            i, j = merge_idx
            clusters[i].extend(clusters[j])
            clusters.pop(j)

    return clusters


def _sort_cluster_by_route(cluster: list[dict]) -> list[dict]:
    """
    Sort POIs in a cluster to minimize travel distance.
    Uses nearest-neighbor heuristic starting from the westernmost POI.
    """
    if len(cluster) <= 1:
        return cluster

    # Start with the westernmost POI (lowest lon)
    sorted_pois = [min(cluster, key=lambda p: _parse_location(p.get("location", "0,0"))[0])]
    remaining = [p for p in cluster if p not in sorted_pois]

    while remaining:
        current = sorted_pois[-1]
        current_loc = current.get("location", "0,0")
        nearest = min(remaining, key=lambda p: _calculate_distance(current_loc, p.get("location", "0,0")))
        sorted_pois.append(nearest)
        remaining.remove(nearest)

    return sorted_pois


# ---------------------------------------------------------------------------
# Daily schedule building
# ---------------------------------------------------------------------------

def _build_daily_schedule(
    pois: list[dict],
    day_date: datetime,
    mode: str = "walking",
) -> list[dict]:
    """
    Build a daily schedule from a list of POIs.
    Assigns arrival/departure times and transport between POIs.
    """
    schedule = []
    current_time = datetime(day_date.year, day_date.month, day_date.day, DAY_START_HOUR)

    # Insert breakfast if not at hotel
    if pois and "酒店" not in pois[0].get("type", ""):
        schedule.append({
            "type": "breakfast",
            "name": "早餐",
            "arrival": current_time.strftime("%H:%M"),
            "departure": (current_time + timedelta(hours=1)).strftime("%H:%M"),
            "tips": "建议在酒店附近用餐",
        })
        current_time += timedelta(hours=1)

    prev_loc = None
    for i, poi in enumerate(pois):
        poi_type = poi.get("type", "未知")
        duration_min = VISIT_DURATION.get(poi_type, VISIT_DURATION["未知"])

        # Add transport from previous location
        if prev_loc and poi.get("location"):
            try:
                transport_info = get_route_sync(prev_loc, poi["location"], mode)
                travel_min = transport_info.get("duration", 1800) // 60
                current_time += timedelta(minutes=travel_min)
            except Exception:
                travel_min = 30  # default 30 min
                current_time += timedelta(minutes=travel_min)

        arrival = current_time
        departure = current_time + timedelta(minutes=duration_min)

        place = {
            "name": poi.get("name", "未知地点"),
            "poi_id": poi.get("id", ""),
            "arrival": arrival.strftime("%H:%M"),
            "departure": departure.strftime("%H:%M"),
            "transport": _get_transport_desc(prev_loc, poi.get("location"), mode) if prev_loc else "",
            "tips": _get_poi_tip(poi),
            "address": poi.get("address", ""),
        }

        schedule.append(place)
        current_time = departure
        prev_loc = poi.get("location", "")

        # Insert lunch break around noon
        if i == 1 and departure.hour >= 11 and departure.hour < 14:
            current_time = departure + timedelta(minutes=30)
            schedule.append({
                "type": "lunch",
                "name": "午餐",
                "arrival": departure.strftime("%H:%M"),
                "departure": (departure + timedelta(hours=1)).strftime("%H:%M"),
                "tips": "可在景区附近选择餐厅",
            })
            current_time = departure + timedelta(hours=1)

        # Insert dinner at end of day
        if i == len(pois) - 1 and current_time.hour >= DINNER_HOUR - 2:
            schedule.append({
                "type": "dinner",
                "name": "晚餐",
                "arrival": current_time.strftime("%H:%M"),
                "departure": (current_time + timedelta(hours=1, minutes=30)).strftime("%H:%M"),
                "tips": "体验当地美食",
            })
            current_time += timedelta(hours=1, minutes=30)

    return schedule


def get_route_sync(origin: str, destination: str, mode: str = "walking") -> dict:
    """Synchronous wrapper for route API call."""
    import asyncio
    return asyncio.run(get_route(origin, destination, mode))


def _get_transport_desc(from_loc: str, to_loc: str, mode: str) -> str:
    """Get a human-readable transport description."""
    try:
        route = get_route_sync(from_loc, to_loc, mode)
        dist_km = route.get("distance", 0) / 1000
        duration_min = route.get("duration", 0) / 60
        mode_desc = {"walking": "步行", "driving": "驾车", "bus": "公交"}.get(mode, mode)
        return f"{mode_desc}约{dist_km:.1f}公里，耗时约{int(duration_min)}分钟"
    except Exception:
        return f"{mode}交通"


def _get_poi_tip(poi: dict) -> str:
    """Generate a tip for visiting a POI."""
    poi_type = poi.get("type", "未知")
    tips = {
        "景点": "建议提前了解开放时间和门票信息",
        "博物馆": "周一闭馆，请留意开放时间",
        "公园": "注意防晒，随身携带饮用水",
        "餐厅": "高峰时段可能需要等位，建议提前预约",
        "购物": "记得索要发票，注意保管好随身物品",
        "酒店": "记得携带身份证件办理入住",
    }
    return tips.get(poi_type, "祝您旅途愉快！")


# ---------------------------------------------------------------------------
# Weather for multi-day trip
# ---------------------------------------------------------------------------

async def _get_multi_day_weather(
    destination: str,
    start_date: datetime,
    days: int,
) -> list[dict]:
    """
    Get weather forecast for multiple days.
    In mock mode, returns realistic mock data.
    """
    weather_list = []
    try:
        # Try to get real weather (HeFeng supports up to 7 days forecast)
        current = await get_weather(destination)
        # Use current weather as template, vary temperature slightly per day
        for i in range(days):
            temp_adjust = (i % 3 - 1) * 2  # slight variation
            day_weather = {
                "temperature": current.get("temperature", 22) + temp_adjust,
                "condition": _rotate_conditions(current.get("condition", "晴"), i),
                "wind_speed": current.get("wind_speed", 12),
                "humidity": current.get("humidity", 65),
                "city": current.get("city", destination),
            }
            weather_list.append(day_weather)
    except Exception:
        # Fallback to mock weather
        conditions = ["晴", "多云", "晴", "多云转晴", "晴"]
        for i in range(days):
            weather_list.append({
                "temperature": 22 + (i % 3 - 1) * 3,
                "condition": conditions[i % len(conditions)],
                "wind_speed": 12,
                "humidity": 65,
                "city": destination,
            })

    return weather_list


def _rotate_conditions(base_condition: str, day_offset: int) -> str:
    """Rotate through weather conditions for multi-day forecast."""
    conditions = ["晴", "多云", "阴", "晴", "多云转晴", "晴间多云"]
    return conditions[day_offset % len(conditions)]


# ---------------------------------------------------------------------------
# Outfit scene determination
# ---------------------------------------------------------------------------

def _determine_outfit_scene(places: list[dict], weather: dict) -> str:
    """Determine the outfit scene based on day's activities and weather."""
    if not places:
        return "休闲"

    # Count activity types
    activity_types = [p.get("type", "景点") for p in places]
    has_museum = any("博物馆" in t for t in activity_types)
    has_outdoor = any(t in ["公园", "景点"] for t in activity_types)
    has_food = any(t == "餐厅" for t in activity_types)

    temperature = weather.get("temperature", 22)

    if has_museum and not has_outdoor:
        return "城市漫游"
    elif has_outdoor and temperature > 25:
        return "户外徒步"
    elif has_food and len(places) <= 2:
        return "美食打卡"
    else:
        return "城市漫游"


# ---------------------------------------------------------------------------
# LLM validation (simplified heuristic validation)
# ---------------------------------------------------------------------------

def _validate_itinerary(day_plan: dict) -> list[str]:
    """
    Validate a day's itinerary and return a list of warnings.
    Uses heuristic rules to check reasonableness.
    """
    warnings = []
    places = [p for p in day_plan.get("places", []) if isinstance(p, dict) and "name" in p]

    if not places:
        warnings.append("当日没有安排景点，建议添加活动")
        return warnings

    # Check if too many places in one day
    if len(places) > 6:
        warnings.append("当日景点较多，可能过于紧张，建议拆分到其他日期")

    # Check for meal安排
    meal_count = sum(1 for p in places if p.get("type") in ["breakfast", "lunch", "dinner"] or p.get("name") in ["早餐", "午餐", "晚餐"])
    if meal_count < 2:
        warnings.append("建议合理安排用餐时间")

    # Check time span
    if places:
        try:
            first_arrival = places[0].get("arrival", "09:00")
            last_departure = places[-1].get("departure", "21:00")
            first_hour = int(first_arrival.split(":")[0])
            last_hour = int(last_departure.split(":")[0])
            if last_hour - first_hour > 12:
                warnings.append("行程时间跨度较长，注意休息和体力分配")
        except (ValueError, IndexError):
            pass

    # Check weather appropriateness
    weather = day_plan.get("weather", {})
    temp = weather.get("temperature", 20)
    if temp > 35:
        warnings.append("高温天气，请注意防暑降温")
    if temp < 0:
        warnings.append("低温天气，请注意保暖")

    return warnings


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

def _estimate_daily_cost(places: list[dict], destination: str) -> str:
    """Estimate daily cost based on planned activities."""
    place_count = len([p for p in places if isinstance(p, dict) and p.get("name") not in ["早餐", "午餐", "晚餐", "breakfast", "lunch", "dinner"]])
    meal_cost = 150  # 3 meals
    attraction_cost = place_count * 100  # ~100 per attraction
    transport_cost = 50  # daily transport

    total = meal_cost + attraction_cost + transport_cost
    return f"¥{total - 50}-{total + 100}"


# ---------------------------------------------------------------------------
# Core trip generation
# ---------------------------------------------------------------------------

async def generate_trip(
    destination: str,
    days: int,
    start_date: str,
    user_preferences: dict,
    wardrobe_items: Optional[list[dict]] = None,
) -> dict:
    """
    Generate a complete multi-day travel itinerary.

    Args:
        destination: Destination city name
        days: Number of travel days
        start_date: Start date string (YYYY-MM-DD)
        user_preferences: Dict with budget, style, mobility, interests
        wardrobe_items: Optional list of wardrobe items for outfit recommendations

    Returns:
        {
            "days": [
                {
                    "day": 1,
                    "date": "2026-05-01",
                    "weather": {"temp": 22, "condition": "晴"},
                    "outfit_scene": "城市漫游",
                    "places": [...],
                    "outfit": {...},
                },
                ...
            ],
            "traffic_summary": {...},
            "total_cost_estimate": "¥1500-2000",
        }
    """
    # Parse start date
    try:
        start = datetime.fromisoformat(start_date)
    except ValueError:
        start = datetime.now()

    # 1. Search for POIs at destination
    search_keywords = _get_search_keywords(user_preferences)
    all_pois = []
    for keyword in search_keywords:
        try:
            pois = await search_poi(keyword, destination)
            all_pois.extend(pois)
        except Exception:
            pass

    # Deduplicate POIs by ID
    seen_ids = set()
    unique_pois = []
    for poi in all_pois:
        if poi.get("id") not in seen_ids:
            seen_ids.add(poi.get("id"))
            unique_pois.append(poi)

    # Filter out POIs without locations
    unique_pois = [p for p in unique_pois if p.get("location")]

    if not unique_pois:
        # Fallback to mock POIs
        unique_pois = _get_mock_pois_fallback(destination)

    # 2. Cluster POIs by proximity
    clusters = _cluster_pois_by_proximity(unique_pois, max_per_day=min(days * 4, 5))

    # Ensure we have at least `days` clusters
    while len(clusters) < days:
        # Split the largest cluster
        largest_idx = max(range(len(clusters)), key=lambda i: len(clusters[i]))
        cluster = clusters[largest_idx]
        mid = len(cluster) // 2
        clusters.insert(largest_idx + 1, cluster[mid:])
        clusters[largest_idx] = cluster[:mid]

    # Trim to exact days
    clusters = clusters[:days]

    # 3. Get weather for each day
    weather_list = await _get_multi_day_weather(destination, start, days)

    # 4. Build daily itineraries
    daily_plans = []
    for day_idx in range(days):
        day_num = day_idx + 1
        day_date = start + timedelta(days=day_idx)
        date_str = day_date.strftime("%Y-%m-%d")

        # Get POIs for this day
        day_pois = clusters[day_idx] if day_idx < len(clusters) else []
        day_pois = _sort_cluster_by_route(day_pois)

        # Build schedule
        places = _build_daily_schedule(day_pois, day_date)

        # Get weather
        weather = weather_list[day_idx] if day_idx < len(weather_list) else {
            "temperature": 22,
            "condition": "晴",
            "wind_speed": 12,
            "humidity": 65,
        }

        # Determine outfit scene
        outfit_scene = _determine_outfit_scene(places, weather)

        # Generate outfit recommendation
        outfit = {}
        if wardrobe_items:
            try:
                outfit = recommend_outfit(
                    wardrobe_items=wardrobe_items,
                    weather=weather,
                    scene=outfit_scene,
                    body_type=user_preferences.get("body_type"),
                    style_preference=user_preferences.get("style_preference"),
                )
            except Exception:
                outfit = {"outfit": [], "reason": "穿搭生成失败", "tips": "请手动选择穿搭"}

        # Validate itinerary
        day_plan_base = {
            "day": day_num,
            "date": date_str,
            "weather": {
                "temp": weather.get("temperature", 22),
                "condition": weather.get("condition", "晴"),
            },
            "outfit_scene": outfit_scene,
            "places": places,
            "outfit": outfit,
        }
        warnings = _validate_itinerary(day_plan_base)
        if warnings:
            day_plan_base["warnings"] = warnings

        daily_plans.append(day_plan_base)

    # 5. Build traffic summary
    traffic_summary = _build_traffic_summary(destination, daily_plans)

    # 6. Estimate total cost
    total_cost = _estimate_total_cost(daily_plans, user_preferences.get("budget", "中等"))

    return {
        "days": daily_plans,
        "traffic_summary": traffic_summary,
        "total_cost_estimate": total_cost,
    }


def _get_search_keywords(preferences: dict) -> list[str]:
    """Get search keywords based on user preferences."""
    interests = preferences.get("interests", [])
    if not interests or not isinstance(interests, list):
        interests = ["景点", "美食", "公园"]

    # Add variety
    keywords = list(set(interests + ["景点", "美食", "热门"]))
    return keywords[:5]


def _get_mock_pois_fallback(destination: str) -> list[dict]:
    """Return fallback mock POIs when API fails."""
    return [
        {
            "id": f"MOCK_{destination}_1",
            "name": f"{destination}热门景点A",
            "address": f"{destination}市某区某街",
            "location": "116.3974,39.9088",
            "type": "景点",
        },
        {
            "id": f"MOCK_{destination}_2",
            "name": f"{destination}博物馆",
            "address": f"{destination}市文化区",
            "location": "116.4000,39.9100",
            "type": "博物馆",
        },
        {
            "id": f"MOCK_{destination}_3",
            "name": f"{destination}特色餐厅",
            "address": f"{destination}市美食街",
            "location": "116.3950,39.9050",
            "type": "餐厅",
        },
    ]


def _build_traffic_summary(destination: str, daily_plans: list[dict]) -> dict:
    """Build a summary of transportation for the trip."""
    total_places = 0
    transport_modes = {}

    for day in daily_plans:
        for place in day.get("places", []):
            if isinstance(place, dict) and place.get("transport"):
                total_places += 1
                # Extract transport mode
                transport = place.get("transport", "")
                if "步行" in transport:
                    transport_modes["walking"] = transport_modes.get("walking", 0) + 1
                elif "驾车" in transport:
                    transport_modes["driving"] = transport_modes.get("driving", 0) + 1
                elif "公交" in transport:
                    transport_modes["bus"] = transport_modes.get("bus", 0) + 1

    return {
        "destination": destination,
        "total_days": len(daily_plans),
        "total_places": total_places,
        "transport_breakdown": transport_modes,
        "recommendation": "建议购买当地交通卡或使用地图APP导航",
    }


def _estimate_total_cost(daily_plans: list[dict], budget_level: str = "中等") -> str:
    """Estimate total trip cost based on daily plans and budget level."""
    base_multiplier = {"经济": 0.7, "中等": 1.0, "豪华": 1.5}.get(budget_level, 1.0)

    total = 0
    for day in daily_plans:
        place_count = len([p for p in day.get("places", []) if isinstance(p, dict) and p.get("name") not in ["早餐", "午餐", "晚餐", "breakfast", "lunch", "dinner"]])
        daily = (150 + place_count * 100 + 50) * base_multiplier
        total += daily

    low = int(total * 0.85)
    high = int(total * 1.2)
    return f"¥{low}-{high}"
