"""
Outfit Recommendation Engine.
Provides intelligent clothing recommendations based on weather, scene, and body type.
"""
import math
from typing import Optional


# ---------------------------------------------------------------------------
# Color coordination rules
# ---------------------------------------------------------------------------

# Color families for coordination
COLOR_FAMILIES = {
    "黑色": ["黑色", "灰色", "白色", "深蓝色", "藏青色"],
    "白色": ["白色", "浅灰色", "米色", "浅蓝色", "粉色"],
    "灰色": ["灰色", "黑色", "白色", "蓝色", "紫色"],
    "深蓝色": ["深蓝色", "藏青色", "白色", "浅蓝色", "灰色"],
    "浅蓝色": ["浅蓝色", "白色", "深蓝色", "米色", "浅灰"],
    "藏青色": ["藏青色", "深蓝色", "白色", "灰色", "浅蓝"],
    "米色": ["米色", "白色", "浅蓝", "棕色", "卡其色"],
    "卡其色": ["卡其色", "棕色", "深绿", "米色", "白色"],
    "棕色": ["棕色", "卡其色", "深绿", "米色", "橙色"],
    "深绿色": ["深绿色", "卡其色", "棕色", "黑色", "白色"],
    "粉色": ["粉色", "白色", "浅紫", "浅蓝", "灰色"],
    "红色": ["红色", "黑色", "白色", "深蓝", "灰色"],
    "橙色": ["橙色", "棕色", "米色", "深蓝", "白色"],
    "黄色": ["黄色", "白色", "浅蓝", "灰色", "卡其色"],
    "紫色": ["紫色", "灰色", "白色", "深蓝", "黑色"],
}

# High saturation colors that clash with each other
HIGH_SATURATION_COLORS = {"红色", "橙色", "黄色", "粉色", "紫色"}


def _get_color_family(color: str) -> str:
    """Get the color family for a given color."""
    for family, colors in COLOR_FAMILIES.items():
        if color in colors:
            return family
    return "其他"


def _colors_compatible(c1: str, c2: str) -> bool:
    """Check if two colors are compatible."""
    if c1 == c2:
        return True
    f1 = _get_color_family(c1)
    f2 = _get_color_family(c2)
    if f1 == f2:
        return True
    # Check if colors are in each other's family
    for family, colors in COLOR_FAMILIES.items():
        if c1 in colors and c2 in colors:
            return True
    # High saturation colors don't go with each other
    if c1 in HIGH_SATURATION_COLORS and c2 in HIGH_SATURATION_COLORS:
        return False
    return True


def _select_compatible_colors(items: list[dict], max_items: int = 3) -> list[dict]:
    """Select items with mutually compatible colors."""
    if not items:
        return []
    selected = [items[0]]
    for item in items[1:]:
        color = item.get("color", "")
        if all(_colors_compatible(color, s.get("color", "")) for s in selected):
            selected.append(item)
            if len(selected) >= max_items:
                break
    return selected


# ---------------------------------------------------------------------------
# Temperature-based layering rules
# ---------------------------------------------------------------------------

def _get_layer_count(temperature: float) -> int:
    """Determine number of clothing layers based on temperature."""
    if temperature < 5:
        return 3  # 保暖内衣+毛衣+厚外套
    elif temperature < 15:
        return 2  # 内搭+外套
    elif temperature < 25:
        return 2  # 轻薄上装+可选外套
    else:
        return 1  # 仅单层


# ---------------------------------------------------------------------------
# Scene-based clothing selection
# ---------------------------------------------------------------------------

SCENE_SUITABILITY = {
    "通勤": {"外套": 3, "上装": 2, "裤装": 2, "裙装": 1, "鞋": 2, "配饰": 1},
    "商务": {"外套": 3, "上装": 2, "裤装": 2, "裙装": 2, "鞋": 2, "配饰": 2},
    "休闲": {"外套": 2, "上装": 1, "裤装": 1, "裙装": 1, "鞋": 1, "配饰": 1},
    "运动": {"外套": 1, "上装": 1, "裤装": 1, "鞋": 3, "配饰": 1},
    "旅行": {"外套": 2, "上装": 1, "裤装": 1, "鞋": 2, "配饰": 1},
}


def _score_item_for_scene(item: dict, scene: str) -> float:
    """Score how suitable an item is for the given scene (0-10)."""
    item_scene = item.get("scene", "")
    item_type = item.get("type", "")
    score = 0.0
    # Direct scene match
    if item_scene == scene:
        score += 5.0
    # Scene proximity
    if scene == "通勤" and item_scene in ["商务", "休闲"]:
        score += 3.0
    if scene == "旅行" and item_scene in ["休闲", "运动"]:
        score += 3.0
    if scene == "运动" and item_scene in ["休闲"]:
        score += 2.0
    # Type suitability
    if SCENE_SUITABILITY.get(scene, {}).get(item_type, 0) > 0:
        score += 2.0
    return score


# ---------------------------------------------------------------------------
# Body type adaptation rules
# ---------------------------------------------------------------------------

BODY_TYPE_RULES = {
    "苹果型": {
        "highlight": ["上装", "配饰"],
        "avoid": ["紧身裤装", "紧身裙装"],
        "strategy": "突出腰部以上，避免紧身下装",
    },
    "梨形": {
        "highlight": ["上装", "外套"],
        "avoid": ["紧身裤装", "紧身裙装"],
        "strategy": "强调上装，避免紧身下装",
    },
    "沙漏型": {
        "highlight": ["上装", "裙装"],
        "avoid": ["超宽松上装"],
        "strategy": "收腰设计突出曲线",
    },
    "倒三角": {
        "highlight": ["裤装", "裙装"],
        "avoid": ["肩部装饰多的上装"],
        "strategy": "弱化肩部，下装有存在感",
    },
    "矩形": {
        "highlight": ["上装", "外套"],
        "avoid": [],
        "strategy": "层叠感塑造立体轮廓",
    },
}


# ---------------------------------------------------------------------------
# Thickness rules
# ---------------------------------------------------------------------------

def _get_thickness_score(item: dict, temperature: float) -> float:
    """Score how appropriate the item thickness is for the temperature."""
    thickness = item.get("thickness", "中等")
    if temperature < 5:
        if thickness in ["厚", "极厚"]:
            return 3.0
        elif thickness == "中等":
            return 1.0
        else:
            return 0.0
    elif temperature < 15:
        if thickness in ["中等", "厚"]:
            return 3.0
        elif thickness == "薄":
            return 1.5
        else:
            return 0.0
    elif temperature < 25:
        if thickness in ["薄", "中等"]:
            return 3.0
        else:
            return 0.5
    else:
        if thickness == "薄":
            return 3.0
        elif thickness == "中等":
            return 1.0
        else:
            return 0.0


# ---------------------------------------------------------------------------
# Core recommendation logic
# ---------------------------------------------------------------------------


def recommend_outfit(
    wardrobe_items: list[dict],
    weather: dict,
    scene: str,
    body_type: Optional[str] = None,
    style_preference: Optional[list[str]] = None,
) -> dict:
    """
    Generate outfit recommendation based on wardrobe, weather, scene, and body type.

    Args:
        wardrobe_items: List of wardrobe items, each as dict with keys:
            id, name, type, color, thickness, scene, etc.
        weather: Weather dict with temperature, wind_speed, humidity, condition
        scene: One of 通勤/休闲/商务/运动/旅行
        body_type: Optional body type (苹果型/梨形/沙漏型/倒三角/矩形)
        style_preference: Optional list of preferred styles

    Returns:
        {
            "outfit": [{"item": "...", "type": "...", "layer": int}, ...],
            "reason": "...",
            "tips": "...",
        }
    """
    temperature = weather.get("temperature", 20)
    wind_speed = weather.get("wind_speed", 0)
    humidity = weather.get("humidity", 50)
    condition = weather.get("condition", "")
    layer_count = _get_layer_count(temperature)

    # Group items by type
    items_by_type = {}
    for item in wardrobe_items:
        item_type = item.get("type", "未知")
        if item_type not in items_by_type:
            items_by_type[item_type] = []
        items_by_type[item_type].append(item)

    # Select items based on scene and body type
    outfit = []

    # Determine which item types we need
    required_types = _get_required_types(scene, layer_count)

    for item_type in required_types:
        candidates = items_by_type.get(item_type, [])

        # Apply body type rules
        if body_type and body_type in BODY_TYPE_RULES:
            rules = BODY_TYPE_RULES[body_type]
            # Filter out items to avoid
            avoid_types = rules.get("avoid", [])
            # Convert avoid_types to check item type + scene
            candidates = [c for c in candidates if not _item_should_avoid(c, avoid_types)]
            # Prioritize highlighted types
            if item_type in rules.get("highlight", []):
                # Boost score
                for c in candidates:
                    c["_body_type_boost"] = 2.0

        # Score and sort candidates
        scored = []
        for item in candidates:
            scene_score = _score_item_for_scene(item, scene)
            thickness_score = _get_thickness_score(item, temperature)
            body_boost = item.get("_body_type_boost", 0.0)
            total = scene_score + thickness_score + body_boost
            scored.append((total, item))

        scored.sort(key=lambda x: x[0], reverse=True)

        if scored:
            best = scored[0][1]
            layer = _get_layer_for_type(item_type, temperature, layer_count)
            outfit.append({
                "item": best.get("name", "未知"),
                "type": item_type,
                "layer": layer,
                "item_id": best.get("id"),
                "color": best.get("color", ""),
            })

    # Ensure color compatibility
    outfit = _ensure_color_harmony(outfit)

    # Generate reason text
    reason = _generate_reason(temperature, condition, scene, body_type)

    # Generate tips
    tips = _generate_tips(weather, scene, body_type)

    return {
        "outfit": outfit,
        "reason": reason,
        "tips": tips,
    }


def _get_required_types(scene: str, layer_count: int) -> list[str]:
    """Get the required item types based on scene and layer count."""
    base = []
    if layer_count >= 3:
        base = ["上装", "外套", "裤装", "鞋"]
    elif layer_count == 2:
        base = ["上装", "外套", "裤装", "鞋"]
    else:
        base = ["上装", "裤装", "鞋"]

    # Scene-specific additions
    if scene == "旅行":
        base.append("外套")  # Always include a jacket for travel
    if scene == "商务" or scene == "通勤":
        if "外套" not in base:
            base.insert(0, "外套")
    return base


def _get_layer_for_type(item_type: str, temperature: float, total_layers: int) -> int:
    """Determine which layer a specific item type belongs to."""
    if item_type == "外套":
        return total_layers
    elif item_type in ["上装"]:
        if total_layers >= 3:
            return 2
        return 1
    elif item_type in ["裤装", "裙装"]:
        return 1
    elif item_type == "鞋":
        return 1
    elif item_type == "配饰":
        return total_layers
    return 1


def _item_should_avoid(item: dict, avoid_patterns: list[str]) -> bool:
    """Check if item should be avoided based on patterns."""
    item_str = f"{item.get('type', '')} {item.get('scene', '')}".lower()
    for pattern in avoid_patterns:
        if pattern.lower() in item_str:
            return True
    return False


def _ensure_color_harmony(outfit: list[dict]) -> list[dict]:
    """Ensure outfit colors are harmonious."""
    if len(outfit) <= 1:
        return outfit

    # Select items with compatible colors
    compatible = []
    for item in outfit:
        color = item.get("color", "")
        if not compatible:
            compatible.append(item)
            continue
        # Check if color is compatible with all selected
        is_compatible = all(
            _colors_compatible(color, c.get("color", "")) for c in compatible
        )
        if is_compatible:
            compatible.append(item)
        elif len(compatible) < 3:  # Allow some variety if few items
            compatible.append(item)

    return compatible


def _generate_reason(temperature: float, condition: str, scene: str, body_type: Optional[str]) -> str:
    """Generate human-readable reasoning for the outfit recommendation."""
    temp_desc = ""
    if temperature < 5:
        temp_desc = "寒冷"
    elif temperature < 15:
        temp_desc = "微凉"
    elif temperature < 25:
        temp_desc = "温和"
    else:
        temp_desc = "炎热"

    layer_desc = ""
    if temperature < 5:
        layer_desc = "采用三层穿搭法：保暖内衣+毛衣+厚外套，全方位御寒"
    elif temperature < 15:
        layer_desc = "采用两层穿搭：内搭配合外套，应对温差"
    elif temperature < 25:
        layer_desc = "轻便穿搭为主，外套可选，方便穿脱"
    else:
        layer_desc = "轻薄透气为主，应对高温天气"

    scene_desc = {
        "通勤": "适合通勤场景，得体大方",
        "商务": "适合商务场合，正式得体",
        "休闲": "适合日常休闲，舒适自在",
        "运动": "适合运动场景，功能性强",
        "旅行": "适合旅行场景，舒适便携",
    }.get(scene, "")

    body_desc = ""
    if body_type and body_type in BODY_TYPE_RULES:
        body_desc = f"针对{body_type}体型优化：{BODY_TYPE_RULES[body_type]['strategy']}"

    parts = [f"{temp_desc}天气（{temperature}°C），{layer_desc}，{scene_desc}"]
    if body_desc:
        parts.append(body_desc)

    return "".join(parts)


def _generate_tips(weather: dict, scene: str, body_type: Optional[str]) -> str:
    """Generate practical tips based on weather and scene."""
    tips = []
    condition = weather.get("condition", "")
    wind_speed = weather.get("wind_speed", 0)
    humidity = weather.get("humidity", 50)
    temperature = weather.get("temperature", 20)

    # Weather-based tips
    if "雨" in condition:
        tips.append("今日有降水，记得带伞或雨衣")
    if wind_speed > 20:
        tips.append(f"风力较强（{wind_speed}级），建议选择防风外套")
    if humidity > 80:
        tips.append("湿度较高，衣物可能不易干燥，建议多带一套备用")
    if temperature > 30 and "晴" in condition:
        tips.append("紫外线较强，建议涂抹防晒霜，配戴遮阳帽和墨镜")
    if temperature < 10:
        tips.append("早晚温差大，建议携带保暖围巾和手套")

    # Scene-based tips
    if scene == "旅行":
        tips.append("旅行建议穿舒适好走的鞋，方便长时间步行")
        tips.append("建议携带一个小背包，装下外套、水杯和必需品")
    elif scene == "运动":
        tips.append("运动时穿着透气排汗衣物，及时补充水分")
    elif scene == "通勤":
        tips.append("通勤建议提前查看天气预报，避免着装与天气不匹配")

    if not tips:
        tips.append("今日天气适宜，注意适时增减衣物")

    return "；".join(tips)


# ---------------------------------------------------------------------------
# Outfit confirmation / logging
# ---------------------------------------------------------------------------


def format_outfit_log(
    outfit: dict,
    weather: dict,
    scene: str,
    user_id: str,
    date_str: str,
) -> dict:
    """
    Format outfit data for storage in OutfitLog.

    Args:
        outfit: The outfit recommendation dict from recommend_outfit()
        weather: Weather dict
        scene: Scene string
        user_id: User identifier
        date_str: Date string (YYYY-MM-DD)

    Returns:
        Dict suitable for OutfitLog creation
    """
    weather_summary = (
        f"{weather.get('temperature', '?')}°C，"
        f"{weather.get('condition', '未知天气')}，"
        f"风力{weather.get('wind_speed', 0)}级"
    )

    outfit_items = [
        {
            "item_id": item.get("item_id"),
            "name": item.get("item"),
            "type": item.get("type"),
            "layer": item.get("layer"),
            "color": item.get("color", ""),
        }
        for item in outfit.get("outfit", [])
    ]

    return {
        "user_id": user_id,
        "date": date_str,
        "scene": scene,
        "weather_summary": weather_summary,
        "outfit_items": outfit_items,
        "confirmed": False,
    }
