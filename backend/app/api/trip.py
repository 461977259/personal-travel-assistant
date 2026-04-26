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
