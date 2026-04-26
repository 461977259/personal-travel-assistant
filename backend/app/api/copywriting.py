"""
文案生成 API 接口。
提供文案生成、Vlog 脚本生成、风格列表查询、文案保存等功能。
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.content import Content
from app.services.copywriting_engine import generate_copywriting, generate_vlog_script
from app.services.copywriting_templates import (
    get_all_styles,
    get_all_platforms,
    STYLE_GUIDE,
)


router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class PhotoInput(BaseModel):
    """单张照片的输入数据。"""
    scene: str = Field(default="", description="场景/地标名称")
    location: str = Field(default="", description="地点/城市")
    time: str = Field(default="", description="拍摄时间，格式 HH:MM")
    url: Optional[str] = Field(default=None, description="照片URL（预留）")


class CopywritingGenerateRequest(BaseModel):
    """文案生成请求。"""
    photos: list[PhotoInput] = Field(default_factory=list, description="照片列表")
    trip: Optional[dict] = Field(default=None, description="行程数据（可选）")
    style: str = Field(default="文艺", description="文案风格")
    platform: str = Field(default="朋友圈", description="目标平台")


class VlogScriptRequest(BaseModel):
    """Vlog 脚本生成请求。"""
    trip: dict = Field(..., description="完整行程数据")
    style: str = Field(default="文艺", description="脚本风格")


class CopywritingSaveRequest(BaseModel):
    """文案保存请求。"""
    content_type: str = Field(..., description="内容类型: copywriting / vlog_script")
    title: str = Field(default="", description="文案标题")
    body: Optional[str] = Field(default=None, description="文案正文内容（字符串，方便前端展示）")
    content_body: Optional[dict] = Field(default=None, description="文案内容（JSON格式）")
    style: Optional[str] = Field(default=None, description="风格")
    tags: Optional[str] = Field(default=None, description="话题标签，逗号分隔")
    photos: Optional[list[dict]] = Field(default=None, description="关联照片")
    trip_id: Optional[int] = Field(default=None, description="关联行程ID")
    user_id: str = Field(default="default_user", description="用户ID")


class StyleInfo(BaseModel):
    """风格信息。"""
    name: str
    guide: str
    platforms: list[str]


class PhotoSuggestion(BaseModel):
    """照片配文建议。"""
    photo_idx: int
    caption: str
    scene: str = ""
    location: str = ""


class CopywritingResponse(BaseModel):
    """文案生成响应。"""
    platform: str
    style: str
    title: str
    content: str
    hashtags: list[str]
    photo_suggestions: list[PhotoSuggestion]


class VlogScene(BaseModel):
    """Vlog 分镜场景。"""
    scene: int
    location: str
    duration: str
    shots: list[str]
    narration: str
    music: str


class VlogScriptResponse(BaseModel):
    """Vlog 脚本响应。"""
    title: str
    total_duration: str
    scenes: list[VlogScene]


class CopywritingSaveResponse(BaseModel):
    """文案保存响应。"""
    id: int
    content_type: str
    title: str
    message: str


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@router.post("/copywriting/generate", response_model=CopywritingResponse)
async def create_copywriting(request: CopywritingGenerateRequest):
    """
    生成文案（朋友圈 / 小红书 / 抖音 / 微博）。

    **请求体**:
    ```json
    {
        "photos": [
            {"scene": "故宫", "location": "北京", "time": "09:30"},
            {"scene": "长城", "location": "北京", "time": "14:00"}
        ],
        "trip": {"destination": "北京", "days": 3},
        "style": "文艺",
        "platform": "朋友圈"
    }
    ```

    **返回**:
    ```json
    {
        "platform": "朋友圈",
        "style": "文艺",
        "title": "京华烟云深处的光影",
        "content": "🌿 故宫\n光影穿过树梢的样子...",
        "hashtags": ["#旅行", "#北京", "#故宫"],
        "photo_suggestions": [
            {"photo_idx": 0, "caption": "光影斑驳的清晨", "scene": "故宫", "location": "北京"}
        ]
    }
    ```
    """
    # 验证风格
    if request.style not in get_all_styles():
        raise HTTPException(
            status_code=400,
            detail=f"不支持的风格: {request.style}，可选: {get_all_styles()}"
        )

    # 验证平台
    if request.platform not in get_all_platforms():
        raise HTTPException(
            status_code=400,
            detail=f"不支持的平台: {request.platform}，可选: {get_all_platforms()}"
        )

    # 转换为 dict 格式
    photos_data = [p.model_dump() for p in request.photos]

    # 生成文案
    result = await generate_copywriting(
        photos=photos_data,
        trip=request.trip,
        style=request.style,
        platform=request.platform,
    )

    # 构建响应
    return CopywritingResponse(
        platform=result["platform"],
        style=result["style"],
        title=result["title"],
        content=result["content"],
        hashtags=result["hashtags"],
        photo_suggestions=[
            PhotoSuggestion(**s) for s in result["photo_suggestions"]
        ],
    )


@router.post("/copywriting/vlog", response_model=VlogScriptResponse)
async def create_vlog_script(request: VlogScriptRequest):
    """
    生成 Vlog 分镜脚本。

    **请求体**:
    ```json
    {
        "trip": {
            "destination": "北京",
            "days": 3,
            "itinerary": {
                "days": [
                    {
                        "name": "故宫",
                        "highlights": ["航拍全景", "红墙特写"],
                        "morning": "参观故宫",
                        "afternoon": "景山公园看日落"
                    }
                ]
            }
        },
        "style": "文艺"
    }
    ```

    **返回**:
    ```json
    {
        "title": "北京3日｜一场与自己的对话",
        "total_duration": "~5分钟",
        "scenes": [
            {
                "scene": 1,
                "location": "故宫",
                "duration": "1分30秒",
                "shots": ["航拍全景", "红墙特写"],
                "narration": "Day 1，我们来到了故宫...",
                "music": "舒缓钢琴曲"
            }
        ]
    }
    ```
    """
    if request.style not in get_all_styles():
        raise HTTPException(
            status_code=400,
            detail=f"不支持的风格: {request.style}，可选: {get_all_styles()}"
        )

    result = await generate_vlog_script(
        trip=request.trip,
        style=request.style,
    )

    return VlogScriptResponse(
        title=result["title"],
        total_duration=result["total_duration"],
        scenes=[VlogScene(**s) for s in result["scenes"]],
    )


@router.get("/copywriting/styles", response_model=list[StyleInfo])
async def list_styles():
    """
    获取所有支持的文案风格列表。

    **返回**:
    ```json
    [
        {
            "name": "文艺",
            "guide": "语言优美，善用比喻和通感，节奏慢而舒缓，适合表达内心感受",
            "platforms": ["朋友圈", "小红书", "抖音", "微博"]
        }
    ]
    ```
    """
    platforms = get_all_platforms()
    styles = []
    for name, guide in STYLE_GUIDE.items():
        styles.append(StyleInfo(
            name=name,
            guide=guide,
            platforms=platforms,
        ))
    return styles


@router.post("/copywriting/save", response_model=CopywritingSaveResponse)
async def save_copywriting(
    request: CopywritingSaveRequest,
    db: Session = Depends(get_db),
):
    """
    保存生成的文案到数据库（Content 表）。

    **请求体**:
    ```json
    {
        "content_type": "copywriting",
        "title": "北京3日｜一场与自己的对话",
        "body": "🌿 故宫\n光影穿过树梢...",
        "content_body": {
            "platform": "朋友圈",
            "style": "文艺",
            "content": "...",
            "hashtags": ["#旅行", "#北京"],
            "photo_suggestions": []
        },
        "style": "文艺",
        "tags": "旅行,北京,摄影",
        "trip_id": 1,
        "user_id": "default_user"
    }
    ```

    **返回**:
    ```json
    {
        "id": 1,
        "content_type": "copywriting",
        "title": "北京3日｜一场与自己的对话",
        "message": "文案保存成功"
    }
    ```
    """
    # 验证 content_type
    valid_types = ["copywriting", "vlog_script"]
    if request.content_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的 content_type: {request.content_type}，可选: {valid_types}"
        )

    # 构造 Content 记录
    # content_body 优先使用 content_body 字段（dict），否则将 body 转为 JSON
    if request.content_body:
        content_body_json = request.content_body
    elif request.body:
        content_body_json = {
            "content": request.body,
            "platform": "朋友圈",
            "style": request.style or "文艺",
        }
    else:
        content_body_json = {}

    db_content = Content(
        user_id=request.user_id,
        trip_id=request.trip_id,
        content_type=request.content_type,
        title=request.title,
        body=request.body,
        style=request.style,
        tags=request.tags,
        photos=request.photos,
        exported_text=json.dumps(content_body_json, ensure_ascii=False) if content_body_json else None,
    )

    db.add(db_content)
    db.commit()
    db.refresh(db_content)

    return CopywritingSaveResponse(
        id=db_content.id,
        content_type=db_content.content_type,
        title=db_content.title,
        message="文案保存成功",
    )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

import json  # noqa: E402
