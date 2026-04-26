"""
Outfit API endpoints.
GET  /api/outfit/recommend?city=北京&scene=旅行&date=2026-05-01
POST /api/outfit/confirm
GET  /api/outfit/logs
GET  /api/outfit/logs/{log_id}
"""
from datetime import date as date_type
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.outfit_log import OutfitLog
from app.models.wardrobe import WardrobeItem
from app.integrations.weather import get_weather
from app.services.outfit_engine import recommend_outfit

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class OutfitItemResponse(BaseModel):
    item: str
    type: str
    layer: int
    item_id: Optional[int] = None
    color: Optional[str] = None


class OutfitRecommendationResponse(BaseModel):
    outfit: list[OutfitItemResponse]
    reason: str
    tips: str


class OutfitConfirmRequest(BaseModel):
    user_id: str
    date: str  # YYYY-MM-DD
    scene: str
    weather_summary: str
    outfit_items: list[dict]  # [{"item_id": 1, "name": "...", "type": "外套"}, ...]
    confirmed: bool = True


class OutfitLogResponse(BaseModel):
    id: int
    user_id: str
    date: str
    scene: str
    weather_summary: str
    outfit_items: list[dict]
    confirmed: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/outfit/recommend", response_model=OutfitRecommendationResponse)
async def recommend_outfit_api(
    city: str = Query(..., description="城市名称，如「北京」"),
    scene: str = Query(..., description="场景：通勤/休闲/商务/运动/旅行"),
    date: Optional[str] = Query(None, description="日期 YYYY-MM-DD（可选，默认今天）"),
    user_id: Optional[str] = Query(None, description="用户ID（可选）"),
    body_type: Optional[str] = Query(None, description="体型：苹果型/梨形/沙漏型/倒三角/矩形"),
    style_preference: Optional[str] = Query(None, description="风格偏好，逗号分隔"),
    db: Session = Depends(get_db),
):
    """
    Get outfit recommendation for a given city, scene, and date.
    Automatically fetches weather, queries user's wardrobe, and generates recommendation.
    """
    # 1. Fetch weather
    try:
        weather = await get_weather(city)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"天气获取失败: {str(e)}")

    # 2. Query user wardrobe
    query = db.query(WardrobeItem)
    if user_id:
        # If user_id is stored in wardrobe items, filter by it
        # Currently wardrobe doesn't have user_id field, so we return all items
        pass

    wardrobe_items = query.all()
    wardrobe_data = [
        {
            "id": item.id,
            "name": item.name,
            "type": item.type,
            "color": item.color,
            "thickness": item.thickness,
            "scene": item.scene,
        }
        for item in wardrobe_items
    ]

    if not wardrobe_data:
        return OutfitRecommendationResponse(
            outfit=[],
            reason="您的衣橱为空，请在衣橱管理中添加衣物后获取推荐",
            tips="先添加几件衣服吧！",
        )

    # 3. Parse style preference
    style_list = None
    if style_preference:
        style_list = [s.strip() for s in style_preference.split(",")]

    # 4. Generate recommendation
    recommendation = recommend_outfit(
        wardrobe_items=wardrobe_data,
        weather=weather,
        scene=scene,
        body_type=body_type,
        style_preference=style_list,
    )

    return OutfitRecommendationResponse(**recommendation)


@router.post("/outfit/confirm")
async def confirm_outfit(
    payload: OutfitConfirmRequest,
    db: Session = Depends(get_db),
):
    """
    Confirm and save the outfit for a given day.
    Records the outfit selection to the OutfitLog table.
    """
    try:
        log_date = date_type.fromisoformat(payload.date)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")

    # Check if a log already exists for this user and date
    existing = (
        db.query(OutfitLog)
        .filter(
            OutfitLog.user_id == payload.user_id,
            OutfitLog.date == log_date,
        )
        .first()
    )

    if existing:
        # Update existing log
        existing.scene = payload.scene
        existing.weather_summary = payload.weather_summary
        existing.outfit_items = payload.outfit_items
        existing.confirmed = payload.confirmed
        db.commit()
        db.refresh(existing)
        return {"message": "穿搭记录已更新", "id": existing.id, "log": existing}

    # Create new log
    log = OutfitLog(
        user_id=payload.user_id,
        date=log_date,
        scene=payload.scene,
        weather_summary=payload.weather_summary,
        outfit_items=payload.outfit_items,
        confirmed=payload.confirmed,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "穿搭记录已保存", "id": log.id}


@router.get("/outfit/logs", response_model=list[OutfitLogResponse])
async def list_outfit_logs(
    user_id: str = Query(..., description="用户ID"),
    start_date: Optional[str] = Query(None, description="起始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    scene: Optional[str] = Query(None, description="场景过滤"),
    db: Session = Depends(get_db),
):
    """
    List outfit logs for a user, with optional date range and scene filter.
    """
    query = db.query(OutfitLog).filter(OutfitLog.user_id == user_id)

    if start_date:
        try:
            start = date_type.fromisoformat(start_date)
            query = query.filter(OutfitLog.date >= start)
        except ValueError:
            raise HTTPException(status_code=400, detail="起始日期格式错误")

    if end_date:
        try:
            end = date_type.fromisoformat(end_date)
            query = query.filter(OutfitLog.date <= end)
        except ValueError:
            raise HTTPException(status_code=400, detail="结束日期格式错误")

    if scene:
        query = query.filter(OutfitLog.scene == scene)

    logs = query.order_by(OutfitLog.date.desc()).all()

    return [
        OutfitLogResponse(
            id=log.id,
            user_id=log.user_id,
            date=log.date.isoformat(),
            scene=log.scene,
            weather_summary=log.weather_summary,
            outfit_items=log.outfit_items or [],
            confirmed=log.confirmed,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.get("/outfit/logs/{log_id}", response_model=OutfitLogResponse)
async def get_outfit_log(log_id: int, db: Session = Depends(get_db)):
    """Get a specific outfit log by ID."""
    log = db.query(OutfitLog).filter(OutfitLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="穿搭记录不存在")

    return OutfitLogResponse(
        id=log.id,
        user_id=log.user_id,
        date=log.date.isoformat(),
        scene=log.scene,
        weather_summary=log.weather_summary,
        outfit_items=log.outfit_items or [],
        confirmed=log.confirmed,
        created_at=log.created_at.isoformat(),
    )
