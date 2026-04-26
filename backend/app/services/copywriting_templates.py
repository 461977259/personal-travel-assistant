"""
文案模板库 - 文案生成引擎的核心模板配置。
预置 5 种风格模板，每种包含标题公式、正文结构、平台适配。
"""

from typing import Dict

# ---------------------------------------------------------------------------
# 文案模板库
# ---------------------------------------------------------------------------

TEMPLATES: Dict[str, dict] = {
    "文艺": {
        "vlog_script": (
            "【分镜1】清晨的{landmark}，光影斑驳，像是时光静止的地方。\n"
            "【分镜2】转角遇见一家小店，{highlight}，岁月在此刻温柔。\n"
            "【分镜3】登高望远，{view}，心中涌起莫名的感动。\n"
            "【旁白】旅行，是一场与自己的对话。每一步，都是归途。"
        ),
        "friend_circle": (
            "🌿 {landmark}\n"
            "光影穿过树梢的样子，像极了某个遥远的梦。\n\n"
            "📍 {location}\n"
            "⏰ {best_time}"
        ),
        "xiaohongshu": (
            "## {title}\n\n"
            "🌅 在{landmark}，我找到了属于自己的小确幸。\n\n"
            "{description}\n\n"
            "✨ 那些被光影记录的瞬间，\n"
            "是旅途中最温柔的注脚。"
        ),
        "weibo": (
            "【{title}】\n\n"
            "{landmark}的光影，像是写在风里的诗句。\n"
            "{highlight}\n\n"
            "{tags}"
        ),
        "douyin": (
            "📍 {landmark}\n"
            "{description}\n\n"
            "🎵 {music}\n"
            "✨ {hashtags}"
        ),
    },
    "活泼": {
        "vlog_script": (
            "【分镜1】哇！{landmark}也太美了吧！📸\n"
            "【分镜2】快看这里！{highlight}，绝绝子！\n"
            "【分镜3】这个角度拍超好看！{view}\n"
            "【旁白】旅行就是要疯狂拍照呀！冲冲冲！🎉"
        ),
        "friend_circle": (
            "📸 {landmark}\n"
            "暴走模式开启！{highlight}\n\n"
            "✨OOTD | 今日份快乐碎片\n"
            "📍 {location} | {best_time}"
        ),
        "xiaohongshu": (
            "## {title}\n\n"
            "🏃‍♀️ 姐妹们！{landmark}真的绝绝子！\n\n"
            "📌 {description}\n\n"
            "👀 答应我一定要来！\n"
            "📸 超好拍，随手一拍就是大片感！"
        ),
        "weibo": (
            "【{title}】\n\n"
            "冲冲冲！{landmark}太好玩啦！\n"
            "{highlight}\n\n"
            "{tags}"
        ),
        "douyin": (
            "📍 {landmark}\n"
            "{highlight}\n\n"
            "🎵 {music}\n"
            "✨ {hashtags}"
        ),
    },
    "简约": {
        "vlog_script": (
            "【分镜1】{landmark}\n"
            "【分镜2】{highlight}\n"
            "【旁白】{view}"
        ),
        "friend_circle": (
            "{landmark}\n"
            "{highlight}"
        ),
        "xiaohongshu": (
            "## {title}\n\n"
            "{landmark}\n\n"
            "{description}"
        ),
        "weibo": (
            "{landmark} · {highlight}"
        ),
        "douyin": (
            "{landmark}\n"
            "{hashtags}"
        ),
    },
    "攻略型": {
        "vlog_script": (
            "【分镜1】{landmark} | 游玩时长：{duration}\n"
            "【分镜2】门票信息：{ticket_info}\n"
            "【分镜3】最佳拍照点：{best_photo_spot}\n"
            "【分镜4】必吃美食：{food_recommendation}\n"
            "【旁白】实用Tips：{practical_tips}"
        ),
        "friend_circle": (
            "📍 {landmark} | {location}\n\n"
            "⏰ 游玩时长：{duration}\n"
            "💰 人均花费：{cost}\n"
            "📸 拍照点：{best_photo_spot}\n"
            "🍜 必吃：{food_recommendation}\n\n"
            "✨ {practical_tips}"
        ),
        "xiaohongshu": (
            "## {title}\n\n"
            "📍 地点：{landmark}（{location}）\n"
            "⏰ 开放时间：{opening_hours}\n"
            "💰 门票：{ticket_info}\n\n"
            "### 🚶 游览路线\n"
            "{route_description}\n\n"
            "### 📸 拍照点\n"
            "{best_photo_spot}\n\n"
            "### 🍜 周边美食\n"
            "{food_recommendation}\n\n"
            "### ⚠️ 实用Tips\n"
            "{practical_tips}"
        ),
        "weibo": (
            "【{title}】\n\n"
            "📍 {landmark}\n"
            "⏰ {duration} | 💰 {cost}\n\n"
            "{route_description}\n\n"
            "{tags}"
        ),
        "douyin": (
            "📍 {landmark}攻略\n"
            "⏰ {duration} | 💰 {cost}\n"
            "{practical_tips}\n\n"
            "🎵 {music}\n"
            "✨ {hashtags}"
        ),
    },
    "日记型": {
        "vlog_script": (
            "【Day {day_num} | {date}】\n\n"
            "早上九点，我们出发去{landmark}。\n"
            "阳光正好，心情正好。\n\n"
            "下午在{highlight}，偶遇了一场日落。\n\n"
            "【旁白】今天走了{distance}步，但一点都不觉得累。"
        ),
        "friend_circle": (
            "Day {day_num} 🗓️\n\n"
            "🌤️ 今天的行程：{landmark}\n\n"
            "早上{start_time}出发，下午{end_time}回程。\n"
            "{highlight}\n\n"
            "📝 {diary_entry}"
        ),
        "xiaohongshu": (
            "## {title}\n\n"
            "🗓️ 第{day_num}天 | {date}\n\n"
            "今天的目的地是{landmark}。\n\n"
            "### 🌅 早晨\n"
            "{morning_activity}\n\n"
            "### 🌇 下午\n"
            "{afternoon_activity}\n\n"
            "### 🌙 夜晚\n"
            "{evening_activity}\n\n"
            "今天一共走了{distance}步，喝了{cup_count}杯水，看了{view_count}次风景。\n"
            "明天继续！✨"
        ),
        "weibo": (
            "Day {day_num} | {date}\n\n"
            "{landmark}\n"
            "{diary_entry}\n\n"
            "{tags}"
        ),
        "douyin": (
            "Day {day_num} 旅行日记 📖\n"
            "{diary_entry}\n\n"
            "🎵 {music}\n"
            "✨ {hashtags}"
        ),
    },
}

# ---------------------------------------------------------------------------
# 风格指南
# ---------------------------------------------------------------------------

STYLE_GUIDE: Dict[str, str] = {
    "文艺": "语言优美，善用比喻和通感，节奏慢而舒缓，适合表达内心感受",
    "活泼": "语气轻快，多用感叹号和emoji，适合打卡类、分享类内容",
    "简约": "惜字如金，一句话点题，适合朋友圈封面图配文",
    "攻略型": "信息密度高，实用性优先，包含路线/时间/花费等干货信息",
    "日记型": "第一人称叙事，有时间线，像写日记一样自然记录行程",
}

# ---------------------------------------------------------------------------
# 平台适配
# ---------------------------------------------------------------------------

PLATFORM_HASHTAGS: Dict[str, list[str]] = {
    "朋友圈": ["#旅行", "#记录生活"],
    "小红书": ["#旅行#", "#小众旅行地#", "#旅行打卡#"],
    "抖音": ["#旅行#", "#每日穿搭#", "#风景#"],
    "微博": ["#旅行#", "#带着小红书去旅行#"],
}

# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def get_template(style: str, platform: str) -> str:
    """
    根据风格和平台获取对应的文案模板。

    Args:
        style: 风格类型（文艺/活泼/简约/攻略型/日记型）
        platform: 目标平台（朋友圈/小红书/抖音/微博）

    Returns:
        对应的文案模板字符串
    """
    templates = TEMPLATES.get(style, TEMPLATES["文艺"])
    platform_key = _normalize_platform(platform)
    return templates.get(platform_key, templates["friend_circle"])


def get_style_guide(style: str) -> str:
    """获取风格的描述指南。"""
    return STYLE_GUIDE.get(style, STYLE_GUIDE["文艺"])


def get_hashtags(style: str, platform: str) -> list[str]:
    """获取对应平台的基础 hashtag 列表。"""
    base = PLATFORM_HASHTAGS.get(platform, PLATFORM_HASHTAGS["朋友圈"])
    return list(base)


def get_all_styles() -> list[str]:
    """获取所有可用的风格列表。"""
    return list(STYLE_GUIDE.keys())


def get_all_platforms() -> list[str]:
    """获取所有支持的目标平台。"""
    return list(PLATFORM_HASHTAGS.keys())


def _normalize_platform(platform: str) -> str:
    """将平台名称标准化为内部 key。"""
    mapping = {
        "朋友圈": "friend_circle",
        "小红书": "xiaohongshu",
        "抖音": "douyin",
        "微博": "weibo",
        "vlog": "vlog_script",
    }
    return mapping.get(platform, "friend_circle")
