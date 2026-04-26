"""
文案生成引擎 - 核心生成逻辑。
基于照片场景和行程数据，生成 Vlog 脚本 / 朋友圈文案 / 小红书笔记。
"""

import os
import random
from typing import Optional

from app.services.copywriting_templates import (
    PLATFORM_HASHTAGS,
    get_template,
)


# ---------------------------------------------------------------------------
# LLM 调用（当前为 mock，生产环境替换为 MiniMax / OpenAI 等）
# ---------------------------------------------------------------------------

def _is_mock_mode() -> bool:
    """Check if mock mode is enabled."""
    return os.getenv("LLM_COPY_MODE", "mock").lower() == "true"


async def _call_llm_generate(
    template: str,
    context: dict,
    style: str,
) -> str:
    """
    调用 LLM 生成文案（mock 模式）。

    生产环境应替换为 MiniMax / OpenAI 等实际 LLM 调用。
    当前 mock 模式下，基于模板 + 上下文进行简单的规则替换。
    """
    if _is_mock_mode():
        return _mock_generate(template, context, style)

    # TODO: 真实 LLM 调用
    # response = await openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[...],
    # )
    # return response.choices[0].message.content
    return _mock_generate(template, context, style)


def _mock_generate(template: str, context: dict, style: str) -> str:
    """
    Mock 文案生成器 - 基于模板和上下文进行规则替换。

    生成逻辑：
    1. 模板变量替换（{landmark}, {location} 等）
    2. 风格化润色（基于 style 参数调整语气）
    3. 内容补全（根据已有信息推断缺失字段）
    """
    result = template

    # 基础变量替换
    replacements = {
        "{landmark}": context.get("landmark", "远方"),
        "{location}": context.get("location", "未知地点"),
        "{highlight}": context.get("highlight", "一切都刚刚好"),
        "{view}": context.get("view", "美得让人窒息"),
        "{best_time}": context.get("best_time", "清晨"),
        "{title}": context.get("title", "一场说走就走的旅行"),
        "{description}": context.get("description", "这里的每一刻都值得被记住"),
        "{tags}": context.get("tags", ""),
        "{hashtags}": context.get("hashtags", ""),
        "{music}": context.get("music", "轻快的背景音乐"),
        "{date}": context.get("date", ""),
        "{day_num}": str(context.get("day_num", 1)),
        "{duration}": context.get("duration", "2小时"),
        "{cost}": context.get("cost", "约100元"),
        "{opening_hours}": context.get("opening_hours", "全天开放"),
        "{ticket_info}": context.get("ticket_info", "免费"),
        "{best_photo_spot}": context.get("best_photo_spot", "观景台"),
        "{food_recommendation}": context.get("food_recommendation", "当地特色美食"),
        "{practical_tips}": context.get("practical_tips", "建议提前购票，错峰出行"),
        "{route_description}": context.get("route_description", "建议从入口右侧开始游览"),
        "{start_time}": context.get("start_time", "09:00"),
        "{end_time}": context.get("end_time", "18:00"),
        "{diary_entry}": context.get("diary_entry", "又是完美的一天"),
        "{morning_activity}": context.get("morning_activity", "元气满满地出发"),
        "{afternoon_activity}": context.get("afternoon_activity", "享受午后的阳光"),
        "{evening_activity}": context.get("evening_activity", "在夜色中回望这一天"),
        "{distance}": context.get("distance", "10000"),
        "{cup_count}": context.get("cup_count", "3"),
        "{view_count}": context.get("view_count", "无数次"),
    }

    for key, value in replacements.items():
        result = result.replace(key, value)

    # 风格化润色
    result = _apply_style_tone(result, style)

    return result


def _apply_style_tone(text: str, style: str) -> str:
    """根据风格调整文案语气。"""
    if style == "活泼":
        text = text.replace("。", "！")
        if "！" not in text and "✨" not in text:
            text += "✨"
    elif style == "简约":
        # 简约风格：去除多余换行，精简文字
        lines = [line for line in text.split("\n") if line.strip()]
        text = "\n".join(lines[:3])  # 最多保留3行
    elif style == "攻略型":
        if "⚠️" not in text and "实用" not in text:
            text = text.replace("建议", "⚠️ 建议")
    elif style == "日记型":
        if "🌤️" not in text:
            text = text.replace("今天的", "🌤️ 今天的")
    return text


# ---------------------------------------------------------------------------
# 核心生成函数
# ---------------------------------------------------------------------------

async def generate_copywriting(
    photos: list[dict],
    trip: Optional[dict] = None,
    style: str = "文艺",
    platform: str = "朋友圈",
) -> dict:
    """
    生成文案（朋友圈 / 小红书 / 抖音 / 微博）。

    Args:
        photos: 照片列表，每张照片包含 scene/location/time 等信息。
                 例如: [{"scene": "故宫", "location": "北京", "time": "09:30"}, ...]
        trip: 行程数据（可选），包含目的地、日期等信息。
        style: 风格（文艺/活泼/简约/攻略型/日记型），默认"文艺"。
        platform: 目标平台（朋友圈/小红书/抖音/微博），默认"朋友圈"。

    Returns:
        生成结果字典，包含:
        - platform: 目标平台
        - style: 使用的风格
        - title: 文案标题
        - content: 正文内容
        - hashtags: 话题标签列表
        - photo_suggestions: 每张照片的配文建议
    """
    # 获取模板
    template = get_template(style, platform)

    # 从照片和行程中提取上下文
    context = _extract_context(photos, trip)

    # 生成文案
    content = await _call_llm_generate(template, context, style)

    # 生成标题
    title = _generate_title(photos, trip, style, platform)

    # 生成 hashtags
    hashtags = _generate_hashtags(photos, trip, style, platform)

    # 生成照片配文建议
    photo_suggestions = _generate_photo_suggestions(photos, style)

    return {
        "platform": platform,
        "style": style,
        "title": title,
        "content": content,
        "hashtags": hashtags,
        "photo_suggestions": photo_suggestions,
    }


async def generate_vlog_script(
    trip: dict,
    style: str = "文艺",
) -> dict:
    """
    生成 Vlog 分镜脚本。

    Args:
        trip: 完整行程数据，包含每日行程安排。
        style: 风格，默认"文艺"。

    Returns:
        Vlog 脚本字典，包含:
        - title: 视频标题
        - total_duration: 预估总时长
        - scenes: 分镜列表，每项包含 location/duration/shots/narration/music
    """
    if style == "简约":
        total_duration = "~2分钟"
    elif style == "活泼":
        total_duration = "~3分钟"
    else:
        total_duration = "~5分钟"

    # 从行程中提取场景
    scenes = _extract_scenes_from_trip(trip, style)

    # 生成标题
    destination = trip.get("destination", "未知目的地") if trip else "未知"
    days = trip.get("days", 3) if trip else 3
    title = _generate_vlog_title(destination, days, style)

    return {
        "title": title,
        "total_duration": total_duration,
        "scenes": scenes,
    }


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------

def _extract_context(photos: list[dict], trip: Optional[dict]) -> dict:
    """从照片和行程中提取文案上下文。"""
    context = {}

    # 从照片提取信息
    if photos:
        first_photo = photos[0]
        context["landmark"] = first_photo.get("scene", "远方")
        context["location"] = first_photo.get("location", "未知地点")
        context["best_time"] = _suggest_best_time(first_photo.get("time", ""))
        if len(photos) > 1:
            context["highlight"] = f"还有{len(photos) - 1}个地方值得打卡"
        else:
            context["highlight"] = "一切都刚刚好"

    # 从行程补充信息
    if trip:
        destination = trip.get("destination", "")
        if destination and "landmark" not in context:
            context["landmark"] = destination
        if destination and "location" not in context:
            context["location"] = destination
        if "notes" in trip:
            context["description"] = trip["notes"]
        if "itinerary" in trip:
            # 从行程中提取更多信息
            itinerary = trip["itinerary"]
            if isinstance(itinerary, dict) and "days" in itinerary:
                days = itinerary["days"]
                if days and len(days) > 0:
                    first_day = days[0]
                    if isinstance(first_day, dict):
                        context["morning_activity"] = first_day.get("morning", "出发探索")
                        context["afternoon_activity"] = first_day.get("afternoon", "继续游览")

    # 默认值
    context.setdefault("landmark", "远方")
    context.setdefault("location", "未知地点")
    context.setdefault("best_time", "清晨")
    context.setdefault("title", "一场说走就走的旅行")
    context.setdefault("description", "这里的每一刻都值得被记住")
    context.setdefault("highlight", "一切都刚刚好")
    context.setdefault("view", "美得让人窒息")

    return context


def _suggest_best_time(time_str: str) -> str:
    """根据时间字符串建议最佳拍摄时段描述。"""
    if not time_str:
        return "清晨"
    try:
        hour = int(time_str.split(":")[0])
        if 5 <= hour < 9:
            return "清晨"
        elif 9 <= hour < 12:
            return "上午"
        elif 12 <= hour < 14:
            return "中午"
        elif 14 <= hour < 18:
            return "下午"
        elif 18 <= hour < 21:
            return "傍晚"
        else:
            return "夜晚"
    except (ValueError, IndexError):
        return "清晨"


def _generate_title(photos: list[dict], trip: Optional[dict], style: str, platform: str) -> str:
    """生成文案标题。"""
    location = ""
    if photos:
        location = photos[0].get("scene", "")
    if not location and trip:
        location = trip.get("destination", "")
    if not location:
        location = "远方"

    title_templates = {
        "文艺": [
            "《{loc}的光影》",
            "{loc}，时光在此静止",
            "{loc}的温柔笔记",
            "在{loc}，遇见慢时光",
        ],
        "活泼": [
            "冲鸭！{loc}太好拍了！",
            "姐妹们！{loc}绝绝子！",
            "OMG去{loc}啦！",
            "{loc}打卡成功！✨",
        ],
        "简约": [
            "{loc}",
            "· {loc}",
        ],
        "攻略型": [
            "{loc}超全攻略｜建议收藏",
            "去{loc}看这一篇就够了",
            "{loc}懒人攻略·建议收藏",
        ],
        "日记型": [
            "Day 1 | {loc}",
            "第1天 · {loc}",
            "{loc}旅行日记",
        ],
    }

    templates = title_templates.get(style, title_templates["文艺"])
    template = random.choice(templates)
    return template.format(loc=location)


def _generate_vlog_title(destination: str, days: int, style: str) -> str:
    """生成 Vlog 视频标题。"""
    title_templates = {
        "文艺": [
            "{dest}{days}日｜一场与自己的对话",
            "在{dest}的{days}天，找回内心的宁静",
            "{dest}漫游记",
        ],
        "活泼": [
            "Vlog｜{dest}{days}日游！超全记录！",
            "{dest}冲冲冲！{days}天玩个够！",
            "Plog·{dest}｜这趟旅行太值了！",
        ],
        "简约": [
            "{dest}",
            "{dest} {days}日",
        ],
        "攻略型": [
            "{dest}{days}日游超全攻略｜建议收藏",
            "必收藏！{dest}{days}日游完整记录",
        ],
        "日记型": [
            "Day {days} in {dest}",
            "我的{dest}日记｜{days}天行程记录",
        ],
    }

    templates = title_templates.get(style, title_templates["文艺"])
    template = random.choice(templates)

    # 中文数字转换
    cn_days = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七"}
    cn_day = cn_days.get(days, str(days))

    return template.format(dest=destination, days=days, cn_days=cn_day)


def _generate_hashtags(photos: list[dict], trip: Optional[dict], style: str, platform: str) -> list[str]:
    """生成话题标签。"""
    hashtags = []

    # 基础平台标签
    platform_tags = PLATFORM_HASHTAGS.get(platform, PLATFORM_HASHTAGS["朋友圈"])
    hashtags.extend(platform_tags)

    # 地点标签
    if photos:
        for photo in photos[:3]:  # 最多取3个地点
            scene = photo.get("scene", "")
            location = photo.get("location", "")
            if scene and scene not in [h.strip("#") for h in hashtags]:
                hashtags.append(f"#{scene}")
            if location and location not in [h.strip("#") for h in hashtags]:
                hashtags.append(f"#{location}")

    # 行程目的地标签
    if trip:
        destination = trip.get("destination", "")
        if destination and destination not in [h.strip("#") for h in hashtags]:
            hashtags.append(f"#{destination}")

    # 风格相关标签
    style_tags = {
        "文艺": ["#旅行的意义", "#治愈系", "#生活美学"],
        "活泼": ["#旅行打卡", "#出片", "#ootd"],
        "简约": ["#极简生活", "#简单记录"],
        "攻略型": ["#旅行攻略", "#干货分享", "#避坑指南"],
        "日记型": ["#旅行日记", "#记录生活", "#日常碎片"],
    }
    hashtags.extend(style_tags.get(style, []))

    # 去重（保留顺序）
    seen = set()
    unique = []
    for h in hashtags:
        clean = h.strip("#")
        if clean not in seen:
            seen.add(clean)
            unique.append(h if h.startswith("#") else f"#{h}")

    return unique[:10]  # 最多10个标签


def _generate_photo_suggestions(photos: list[dict], style: str) -> list[dict]:
    """为每张照片生成配文建议。"""
    suggestions = []

    caption_templates = {
        "文艺": [
            "光影斑驳的清晨",
            "转角遇见的温柔",
            "岁月静好的模样",
            "此刻即是永恒",
            "远方不远",
        ],
        "活泼": [
            "绝绝子！",
            "冲冲冲！",
            "超好看！",
            "打卡成功✨",
            "也太美了吧！",
        ],
        "简约": [
            ".",
            "·",
            "·",
            "",
            "",
        ],
        "攻略型": [
            "📸 必拍点",
            "最佳机位",
            "建议游览30分钟",
            "不容错过",
            "拍照超好看",
        ],
        "日记型": [
            "早安，这里",
            "下午茶时光",
            "日落时分",
            "今日份快乐",
            "继续出发",
        ],
    }

    templates = caption_templates.get(style, caption_templates["文艺"])

    for idx, photo in enumerate(photos):
        caption_idx = idx % len(templates)
        suggestions.append({
            "photo_idx": idx,
            "caption": templates[caption_idx],
            "scene": photo.get("scene", ""),
            "location": photo.get("location", ""),
        })

    return suggestions


def _extract_scenes_from_trip(trip: dict, style: str) -> list[dict]:
    """从行程数据中提取 Vlog 分镜场景。"""
    scenes = []

    if not trip:
        # 默认场景
        return [{
            "scene": 1,
            "location": "未知",
            "duration": "~1分钟",
            "shots": ["全景", "特写"],
            "narration": "出发啦！",
            "music": "轻快钢琴曲",
        }]

    itinerary = trip.get("itinerary", {})
    days = itinerary.get("days", []) if isinstance(itinerary, dict) else []

    if not days:
        # 使用目的地作为单一场景
        return [{
            "scene": 1,
            "location": trip.get("destination", "未知"),
            "duration": _get_scene_duration(style),
            "shots": _get_default_shots(style),
            "narration": f"终于来到了{trip.get('destination', '远方')}",
            "music": _get_default_music(style),
        }]

    for day_idx, day in enumerate(days[:3], start=1):  # 最多取3天
        if not isinstance(day, dict):
            continue

        scenes.append({
            "scene": day_idx,
            "location": day.get("name", trip.get("destination", "未知地点")),
            "duration": _get_scene_duration(style),
            "shots": _get_shots_from_day(day, style),
            "narration": _generate_scene_narration(day, day_idx, style),
            "music": _get_default_music(style),
        })

    return scenes


def _get_scene_duration(style: str) -> str:
    """根据风格返回默认场景时长。"""
    durations = {
        "文艺": "1分30秒",
        "活泼": "1分钟",
        "简约": "45秒",
        "攻略型": "2分钟",
        "日记型": "1分30秒",
    }
    return durations.get(style, "1分钟")


def _get_default_shots(style: str) -> list[str]:
    """根据风格返回默认镜头列表。"""
    shots = {
        "文艺": ["航拍全景", "缓慢推镜", "光影特写", "空镜"],
        "活泼": ["自拍", "跟拍", "快切", "特写"],
        "简约": ["全景", "特写"],
        "攻略型": ["全景", "中景", "特写", "细节"],
        "日记型": ["跟拍", "自拍", "空镜"],
    }
    return shots.get(style, ["全景", "特写"])


def _get_shots_from_day(day: dict, style: str) -> list[str]:
    """从每日行程中提取拍摄建议。"""
    default = _get_default_shots(style)
    highlights = day.get("highlights", [])
    if highlights:
        return [h if isinstance(h, str) else str(h) for h in highlights[:3]]
    return default


def _generate_scene_narration(day: dict, day_num: int, style: str) -> str:
    """生成分镜旁白。"""
    location = day.get("name", "远方")

    narrations = {
        "文艺": [
            f"Day {day_num}，我们来到了{location}。",
            f"阳光正好，微风不燥。{location}在光影中显得格外温柔。",
            "在这里，时间仿佛慢了下来。",
        ],
        "活泼": [
            f"Day {day_num}！冲鸭！",
            f"哇！{location}也太好拍了吧！",
            "快跟我一起来看看这里有多美！",
        ],
        "简约": [
            "{location}",
            f"Day {day_num}",
        ],
        "攻略型": [
            f"【{location}】游玩攻略",
            f"今日游览{location}，建议用时2小时",
            "必打卡点推荐：",
        ],
        "日记型": [
            f"第{day_num}天，我们的目的地是{location}。",
            f"早上{day.get('start_time', '9点')}出发，心情格外舒畅。",
            f"在{location}，度过了完美的一天。",
        ],
    }

    templates = narrations.get(style, narrations["文艺"])
    return random.choice(templates)


def _get_default_music(style: str) -> str:
    """根据风格返回推荐背景音乐。"""
    music = {
        "文艺": "舒缓钢琴曲",
        "活泼": "轻快电子乐",
        "简约": "轻音乐",
        "攻略型": "节奏感强的背景音乐",
        "日记型": "民谣/吉他弹唱",
    }
    return music.get(style, "轻音乐")
