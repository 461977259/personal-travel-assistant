"""
高德地图 API endpoint.
GET /api/amap/poi?keyword=故宫&city=北京
GET /api/amap/route?origin=116.3974,39.9088&destination=116.4100,39.8800&mode=walking
GET /api/amap/distance?lat1=39.9088&lon1=116.3974&lat2=39.8800&lon2=116.4100
"""
from fastapi import APIRouter, Query
from app.integrations.amap import search_poi, get_route, get_distance

router = APIRouter()


@router.get("/amap/poi")
async def poi_search(
    keyword: str = Query(..., description="搜索关键词，如「故宫」或「餐厅」"),
    city: str = Query(None, description="城市名称，如「北京」"),
):
    """
    Search POIs (Points of Interest) by keyword in a given city.
    Returns a list of POIs with name, address, location, type, distance.
    """
    results = await search_poi(keyword, city)
    return {"code": 0, "data": results, "message": "success"}


@router.get("/amap/route")
async def route_planning(
    origin: str = Query(..., description="起点坐标，经纬度用逗号分隔，如「116.3974,39.9088」"),
    destination: str = Query(..., description="终点坐标，经纬度用逗号分隔"),
    mode: str = Query("walking", description="出行方式：walking / bus / driving"),
):
    """
    Get route planning between two points.
    Returns distance, duration, and navigation steps.
    """
    result = await get_route(origin, destination, mode)
    return {"code": 0, "data": result, "message": "success"}


@router.get("/amap/distance")
async def distance(
    lat1: float = Query(..., description="第一个点的纬度"),
    lon1: float = Query(..., description="第一个点的经度"),
    lat2: float = Query(..., description="第二个点的纬度"),
    lon2: float = Query(..., description="第二个点的经度"),
):
    """
    Calculate straight-line distance between two coordinates (in meters).
    Uses Haversine formula.
    """
    distance_m = await get_distance(lat1, lon1, lat2, lon2)
    return {
        "code": 0,
        "data": {
            "distance_meters": round(distance_m, 2),
            "distance_km": round(distance_m / 1000, 3),
        },
        "message": "success",
    }
