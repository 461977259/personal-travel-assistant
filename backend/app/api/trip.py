"""
Trip API endpoints.
POST /api/trip/generate
GET  /api/trip/{trip_id}
POST /api/trip/{trip_id}/save
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.trip import Trip
from app.models.wardrobe import WardrobeItem
from app.services.trip_engine import generate_trip
from app.services.trip_outfit_linker import link_outfit_to_trip, get_trip_outfits

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class TripGenerateRequest(BaseModel):
    destination: str
    days: int = Query(ge=1, le=14, description="行程天数 1-14天")
    start_date: str  # YYYY-MM-DD
    preferences: dict = {}  # {budget, style, mobility, interests, body_type, style_preference}
    user_id: Optional[str] = None


class PlaceResponse(BaseModel):
    name: str
    poi_id: Optional[str] = None
    arrival: str
    departure: str
    transport: str
    tips: str
    address: Optional[str] = None


class OutfitInTripResponse(BaseModel):
    outfit: list[dict]
    reason: str
    tips: str


class DayPlanResponse(BaseModel):
    day: int
    date: str
    weather: dict
    outfit_scene: str
    places: list
    outfit: dict
    warnings: Optional[list[str]] = None


class TripGenerateResponse(BaseModel):
    days: list[DayPlanResponse]
    traffic_summary: dict
    total_cost_estimate: str
    trip_data: Optional[dict] = None  # For saving


class TripResponse(BaseModel):
    id: int
    user_id: str
    destination: str
    start_date: str
    end_date: str
    days: int
    itinerary: Optional[dict] = None
    weather_summary: Optional[dict] = None
    transportation: Optional[dict] = None
    daily_outfits: Optional[dict] = None
    total_cost: Optional[float] = None
    notes: Optional[str] = None
    created_at: str
    trip_data: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class TripSaveRequest(BaseModel):
    trip_data: dict
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/trip/generate", response_model=TripGenerateResponse)
async def generate_trip_api(
    payload: TripGenerateRequest,
    db: Session = Depends(get_db),
):
    """
    Generate a complete travel itinerary.
    Searches for attractions, plans routes, fetches weather, and generates daily outfits.
    """
    # 1. Query user wardrobe if user_id provided
    wardrobe_items = None
    if payload.user_id:
        items = db.query(WardrobeItem).all()
        wardrobe_items = [
            {
                "id": item.id,
                "name": item.name,
                "type": item.type,
                "color": item.color,
                "thickness": item.thickness,
                "scene": item.scene,
            }
            for item in items
        ]

    # 2. Generate trip
    try:
        trip = await generate_trip(
            destination=payload.destination,
            days=payload.days,
            start_date=payload.start_date,
            user_preferences=payload.preferences,
            wardrobe_items=wardrobe_items,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"行程生成失败: {str(e)}")

    return TripGenerateResponse(
        days=[DayPlanResponse(**d) for d in trip["days"]],
        traffic_summary=trip["traffic_summary"],
        total_cost_estimate=trip["total_cost_estimate"],
        trip_data=trip,
    )


@router.get("/trip/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: int, db: Session = Depends(get_db)):
    """Get trip details by ID."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    return TripResponse(
        id=trip.id,
        user_id=trip.user_id,
        destination=trip.destination,
        start_date=trip.start_date.isoformat() if trip.start_date else "",
        end_date=trip.end_date.isoformat() if trip.end_date else "",
        days=trip.days,
        itinerary=trip.itinerary,
        weather_summary=trip.weather_summary,
        transportation=trip.transportation,
        daily_outfits=trip.daily_outfits,
        total_cost=trip.total_cost,
        notes=trip.notes,
        created_at=trip.created_at.isoformat() if trip.created_at else "",
        trip_data=getattr(trip, "trip_data", None),
    )


@router.post("/trip/{trip_id}/save")
async def save_trip(
    trip_id: int,
    payload: TripSaveRequest,
    db: Session = Depends(get_db),
):
    """Save/update trip data for an existing trip."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    trip_data = payload.trip_data

    # Extract summary info from trip_data
    if trip_data:
        # Save full trip_data
        if hasattr(trip, "trip_data"):
            trip.trip_data = trip_data

        # Extract daily info for individual fields
        days_data = trip_data.get("days", [])
        if days_data:
            # Build weather summary
            weather_summary = {
                f"day_{d['day']}": d.get("weather", {}) for d in days_data
            }
            trip.weather_summary = weather_summary

            # Build daily outfits
            daily_outfits = {
                f"day_{d['day']}": d.get("outfit", {}) for d in days_data
            }
            trip.daily_outfits = daily_outfits

            # Build itinerary
            itinerary = {
                f"day_{d['day']}": {
                    "date": d.get("date", ""),
                    "places": d.get("places", []),
                    "outfit_scene": d.get("outfit_scene", ""),
                }
                for d in days_data
            }
            trip.itinerary = itinerary

        # Extract cost estimate
        total_cost_str = trip_data.get("total_cost_estimate", "")
        if total_cost_str:
            # Extract numeric value from "¥1500-2000" format
            import re
            numbers = re.findall(r"\d+", total_cost_str.replace(",", ""))
            if numbers:
                try:
                    trip.total_cost = float(numbers[0])
                except ValueError:
                    pass

        # Extract traffic summary
        trip.transportation = trip_data.get("traffic_summary")

    if payload.notes:
        trip.notes = payload.notes

    db.commit()
    db.refresh(trip)

    return {"message": "行程已保存", "id": trip.id}


@router.post("/trip")
async def create_trip(
    destination: str = Query(...),
    days: int = Query(ge=1, le=14),
    start_date: str = Query(...),
    user_id: str = Query(...),
    db: Session = Depends(get_db),
):
    """
    Create a new trip record (without generating itinerary).
    Use POST /api/trip/generate to generate the full itinerary.
    """
    try:
        start = datetime.fromisoformat(start_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")

    end = datetime(start.year, start.month, start.day)
    from datetime import timedelta
    end = start + timedelta(days=days - 1)

    trip = Trip(
        user_id=user_id,
        destination=destination,
        start_date=start,
        end_date=end,
        days=days,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)

    return {"message": "行程已创建", "id": trip.id, "trip_id": trip.id}


# ---------------------------------------------------------------------------
# Outfit-related schemas
# ---------------------------------------------------------------------------

class RegenerateOutfitRequest(BaseModel):
    day: Optional[int] = None  # None = all days
    user_id: Optional[str] = None


class DayOutfitResponse(BaseModel):
    day: int
    date: str
    outfit_scene: str
    outfit: dict


class TripOutfitsResponse(BaseModel):
    trip_id: int
    outfits: list[DayOutfitResponse]


# ---------------------------------------------------------------------------
# Outfit routes
# ---------------------------------------------------------------------------

@router.get("/trip/{trip_id}/outfits", response_model=TripOutfitsResponse)
async def get_trip_outfits_api(trip_id: int, db: Session = Depends(get_db)):
    """Get outfit recommendations for all days of a trip."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    trip_data = getattr(trip, "trip_data", None)
    if not trip_data or "days" not in trip_data:
        raise HTTPException(status_code=404, detail="行程数据不存在，请先生成行程")

    outfits = get_trip_outfits(trip_data)
    return TripOutfitsResponse(trip_id=trip_id, outfits=outfits)


@router.post("/trip/{trip_id}/regenerate-outfit")
async def regenerate_trip_outfit(
    trip_id: int,
    payload: RegenerateOutfitRequest,
    db: Session = Depends(get_db),
):
    """
    Regenerate outfit for a specific day or all days of a trip.

    - day=None : regenerate for all days
    - day=N    : regenerate only for day N
    """
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    trip_data = getattr(trip, "trip_data", None)
    if not trip_data or "days" not in trip_data:
        raise HTTPException(status_code=404, detail="行程数据不存在，请先生成行程")

    # Fetch user wardrobe
    wardrobe_items = db.query(WardrobeItem).all()
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

    user_id = payload.user_id or trip.user_id or "0"

    # Regenerate all days or just one
    if payload.day is None:
        # All days
        updated = link_outfit_to_trip(trip_data, user_id=user_id, wardrobe_items=wardrobe_data)
    else:
        # Single day: update only that day in-place, keep others
        days = list(trip_data.get("days", []))
        target_found = False
        for i, d in enumerate(days):
            if d.get("day") == payload.day:
                day_plan = dict(d)
                weather = day_plan.get("weather", {})
                weather_engine_fmt = {
                    "temperature": weather.get("temp", 22),
                    "condition": weather.get("condition", "晴"),
                    "wind_speed": weather.get("wind_speed", 12),
                    "humidity": weather.get("humidity", 65),
                }
                from app.services.outfit_engine import recommend_outfit
                scene = day_plan.get("outfit_scene", "休闲")
                try:
                    outfit = recommend_outfit(
                        wardrobe_items=wardrobe_data,
                        weather=weather_engine_fmt,
                        scene=scene,
                    )
                except Exception:
                    outfit = {
                        "outfit": [],
                        "reason": "穿搭生成失败",
                        "tips": "请稍后重试",
                    }
                day_plan["outfit"] = outfit
                days[i] = day_plan
                target_found = True
                break
        if not target_found:
            raise HTTPException(status_code=404, detail=f"第 {payload.day} 天不存在")
        updated = dict(trip_data)
        updated["days"] = days

    # Persist updated trip_data
    trip.trip_data = updated
    # Also update daily_outfits summary column
    daily_outfits = {f"day_{d['day']}": d.get("outfit", {}) for d in updated.get("days", [])}
    trip.daily_outfits = daily_outfits
    db.commit()
    db.refresh(trip)

    return {
        "message": f"穿搭已重新生成",
        "trip_id": trip_id,
        "days_updated": [payload.day] if payload.day else [d["day"] for d in updated.get("days", [])],
    }
