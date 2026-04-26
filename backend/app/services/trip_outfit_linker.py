"""
Trip Outfit Linker Service.

Links wardrobe data to a generated trip by injecting daily outfit recommendations
into each day's plan. Can be called:
  1. Automatically after trip generation (in generate_trip pipeline)
  2. On-demand via POST /api/trip/{trip_id}/regenerate-outfit
"""
from typing import Optional

from app.services.outfit_engine import recommend_outfit


def link_outfit_to_trip(
    trip_data: dict,
    user_id: int,
    wardrobe_items: list[dict],
) -> dict:
    """
    Inject outfit recommendations into each day's plan of a trip.

    Flow:
      1. Iterate over each day in trip_data["days"]
      2. Read the day's weather (already embedded by trip_engine)
      3. Determine outfit scene from day's activities
      4. Call outfit_engine.recommend_outfit() for that day
      5. Write the result back into trip_data[day]["outfit"]

    Args:
        trip_data: The full trip_data dict (returned by generate_trip).
                   Expected shape: {"days": [{"day": 1, "weather": {...},
                                            "outfit_scene": "...", ...}, ...]}
        user_id: User ID (for logging / audit).
        wardrobe_items: List of wardrobe item dicts from the wardrobe DB.

    Returns:
        Updated trip_data dict with "outfit" filled in for each day.
    """
    if not wardrobe_items:
        # No wardrobe: write a friendly empty outfit for every day
        return _fill_empty_outfit(trip_data, reason="您的衣橱为空，请在衣橱管理中添加衣物后获取穿搭推荐。")

    if "days" not in trip_data:
        return trip_data

    updated_days = []
    for day_plan in trip_data["days"]:
        day_plan = dict(day_plan)  # shallow copy to avoid mutating caller's dict

        weather = _extract_weather(day_plan)
        scene = day_plan.get("outfit_scene", "休闲")

        try:
            outfit = recommend_outfit(
                wardrobe_items=wardrobe_items,
                weather=weather,
                scene=scene,
                body_type=None,   # could be extended to accept from trip_data
                style_preference=None,
            )
        except Exception:
            outfit = {
                "outfit": [],
                "reason": "穿搭生成失败，请稍后重试",
                "tips": "如有疑问请联系客服",
            }

        day_plan["outfit"] = outfit
        updated_days.append(day_plan)

    trip_data = dict(trip_data)  # shallow copy
    trip_data["days"] = updated_days
    return trip_data


def _extract_weather(day_plan: dict) -> dict:
    """
    Extract a weather dict from a day_plan.

    Supports two weather shapes:
      - trip_engine shape: {"weather": {"temp": 22, "condition": "晴"}}
      - outfit_engine shape: {"temperature": 22, "condition": "晴", "wind_speed": 12, "humidity": 65}

    Normalises to outfit_engine shape.
    """
    weather = day_plan.get("weather", {})

    # Already in outfit_engine format
    if "temperature" in weather or "temp" not in weather:
        return weather

    # Convert from trip_engine format
    return {
        "temperature": weather.get("temp", 22),
        "condition": weather.get("condition", "晴"),
        "wind_speed": weather.get("wind_speed", 12),
        "humidity": weather.get("humidity", 65),
    }


def _fill_empty_outfit(trip_data: dict, reason: str = "") -> dict:
    """Fill every day with a friendly empty-outfit response."""
    if "days" not in trip_data:
        return trip_data

    empty_outfit = {
        "outfit": [],
        "reason": reason or "您的衣橱为空，请在衣橱管理中添加衣物后获取穿搭推荐。",
        "tips": "先添加几件衣服吧！",
    }

    updated_days = []
    for day_plan in trip_data["days"]:
        day_plan = dict(day_plan)
        day_plan["outfit"] = empty_outfit
        updated_days.append(day_plan)

    trip_data = dict(trip_data)
    trip_data["days"] = updated_days
    return trip_data


def get_trip_outfits(trip_data: dict) -> list[dict]:
    """
    Extract outfit summary from each day of a trip.

    Returns a list of {"day": int, "date": str, "outfit_scene": str, "outfit": dict}.
    """
    if "days" not in trip_data:
        return []

    results = []
    for day_plan in trip_data["days"]:
        results.append({
            "day": day_plan.get("day"),
            "date": day_plan.get("date"),
            "outfit_scene": day_plan.get("outfit_scene", "休闲"),
            "outfit": day_plan.get("outfit", {}),
        })
    return results
