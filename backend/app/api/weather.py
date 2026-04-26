"""
Weather API endpoint.
GET /api/weather?city=北京
"""
from fastapi import APIRouter, Query
from app.integrations.weather import get_weather

router = APIRouter()


@router.get("/weather")
async def weather(city: str = Query(..., description="城市名称，如「北京」")):
    """
    Get current weather for a given city.
    Returns temperature, wind, humidity, precipitation, and condition.
    """
    result = await get_weather(city)
    return {"code": 0, "data": result, "message": "success"}
