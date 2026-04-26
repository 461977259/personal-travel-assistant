"""
飞猪旅行 API endpoint.
GET /api/fliggy/flights?origin=北京&destination=上海&date=2026-05-01
GET /api/fliggy/trains?origin=北京&destination=上海&date=2026-05-01
GET /api/fliggy/hotels?city=北京&checkin=2026-05-01&checkout=2026-05-03
"""
from fastapi import APIRouter, Query
from app.integrations.fliggy import search_flights, search_trains, search_hotels

router = APIRouter()


@router.get("/fliggy/flights")
async def flights(
    origin: str = Query(..., description="出发城市"),
    destination: str = Query(..., description="到达城市"),
    date: str = Query(..., description="出发日期，格式 YYYY-MM-DD"),
):
    """
    Search available flights between two cities on a given date.
    """
    results = await search_flights(origin, destination, date)
    return {"code": 0, "data": results, "message": "success"}


@router.get("/fliggy/trains")
async def trains(
    origin: str = Query(..., description="出发城市"),
    destination: str = Query(..., description="到达城市"),
    date: str = Query(..., description="出发日期，格式 YYYY-MM-DD"),
):
    """
    Search available high-speed trains between two cities on a given date.
    """
    results = await search_trains(origin, destination, date)
    return {"code": 0, "data": results, "message": "success"}


@router.get("/fliggy/hotels")
async def hotels(
    city: str = Query(..., description="城市"),
    checkin: str = Query(..., description="入住日期，格式 YYYY-MM-DD"),
    checkout: str = Query(..., description="退房日期，格式 YYYY-MM-DD"),
):
    """
    Search available hotels in a city for given check-in/check-out dates.
    """
    results = await search_hotels(city, checkin, checkout)
    return {"code": 0, "data": results, "message": "success"}
