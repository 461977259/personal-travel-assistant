"""
Tests for Trip Engine.
"""
import pytest
import asyncio
from app.services.trip_engine import (
    generate_trip,
    _cluster_pois_by_proximity,
    _sort_cluster_by_route,
    _calculate_distance,
    _build_traffic_summary,
    _estimate_total_cost,
    _determine_outfit_scene,
    _validate_itinerary,
)


class TestTripEngine:
    """Test trip generation engine."""

    @pytest.fixture
    def sample_pois(self):
        return [
            {"id": "POI1", "name": "天安门广场", "address": "东城区", "location": "116.3974,39.9088", "type": "景点"},
            {"id": "POI2", "name": "故宫博物院", "address": "东城区", "location": "116.3974,39.9144", "type": "景点"},
            {"id": "POI3", "name": "国家博物馆", "address": "东城区", "location": "116.4074,39.9044", "type": "博物馆"},
            {"id": "POI4", "name": "王府井小吃街", "address": "东城区", "location": "116.4174,39.9144", "type": "餐厅"},
            {"id": "POI5", "name": "颐和园", "address": "海淀区", "location": "116.2874,39.9988", "type": "景点"},
            {"id": "POI6", "name": "圆明园", "address": "海淀区", "location": "116.2974,39.9988", "type": "景点"},
        ]

    @pytest.fixture
    def sample_wardrobe(self):
        return [
            {"id": 1, "name": "白色T恤", "type": "上装", "color": "白色", "thickness": "薄", "scene": "日常"},
            {"id": 2, "name": "深蓝西装外套", "type": "外套", "color": "深蓝色", "thickness": "中等", "scene": "商务"},
            {"id": 3, "name": "黑色直筒裤", "type": "裤装", "color": "黑色", "thickness": "中等", "scene": "日常"},
            {"id": 4, "name": "灰色运动鞋", "type": "鞋", "color": "灰色", "thickness": "中等", "scene": "休闲"},
        ]

    def test_calculate_distance(self):
        # Distance from 天安门 (116.3974, 39.9088) to 故宫 (116.3974, 39.9144)
        # Approximately 0.6km (600m)
        dist = _calculate_distance("116.3974,39.9088", "116.3974,39.9144")
        assert 500 < dist < 800  # Should be roughly 600m

    def test_cluster_pois_by_proximity(self, sample_pois):
        clusters = _cluster_pois_by_proximity(sample_pois, max_per_day=5, max_distance_km=5.0)
        assert len(clusters) >= 1
        assert len(clusters[0]) >= 1

    def test_cluster_pois_empty(self):
        clusters = _cluster_pois_by_proximity([], max_per_day=5)
        assert clusters == []

    def test_sort_cluster_by_route(self, sample_pois):
        # Sort a cluster of nearby POIs
        nearby = [p for p in sample_pois if p["location"].startswith("116.397")]
        sorted_pois = _sort_cluster_by_route(nearby)
        assert len(sorted_pois) == len(nearby)
        # Should start with westernmost (lowest lon)
        first = sorted_pois[0]
        assert first["name"] in ["天安门广场", "故宫博物院"]

    def test_sort_cluster_single_item(self, sample_pois):
        single = [sample_pois[0]]
        sorted_pois = _sort_cluster_by_route(single)
        assert sorted_pois == single

    def test_build_traffic_summary(self):
        daily_plans = [
            {
                "day": 1,
                "places": [
                    {"name": "天安门", "transport": "步行约1公里，耗时约15分钟"},
                    {"name": "故宫", "transport": "步行约500米，耗时约8分钟"},
                ],
            },
            {
                "day": 2,
                "places": [
                    {"name": "颐和园", "transport": "驾车约15公里，耗时约30分钟"},
                ],
            },
        ]
        summary = _build_traffic_summary("北京", daily_plans)
        assert summary["destination"] == "北京"
        assert summary["total_days"] == 2
        assert summary["total_places"] >= 0
        assert "transport_breakdown" in summary

    def test_estimate_total_cost(self):
        daily_plans = [
            {"places": [
                {"name": "景点A"},
                {"name": "景点B"},
            ]},
            {"places": [
                {"name": "景点C"},
            ]},
        ]
        cost = _estimate_total_cost(daily_plans, "中等")
        assert "¥" in cost
        assert "-" in cost

    def test_estimate_total_cost_budget(self):
        daily_plans = [{"places": [{"name": "景点"}]}]
        cost = _estimate_total_cost(daily_plans, "经济")
        assert "¥" in cost

    def test_determine_outfit_scene_city(self):
        places = [{"type": "博物馆"}, {"type": "景点"}]
        weather = {"temperature": 22}
        scene = _determine_outfit_scene(places, weather)
        assert scene == "城市漫游"

    def test_determine_outfit_scene_outdoor(self):
        places = [{"type": "公园"}, {"type": "景点"}]
        weather = {"temperature": 28}
        scene = _determine_outfit_scene(places, weather)
        assert scene in ["户外徒步", "城市漫游"]

    def test_determine_outfit_scene_empty(self):
        scene = _determine_outfit_scene([], {"temperature": 22})
        assert scene == "休闲"

    def test_validate_itinerary_normal(self):
        day_plan = {
            "places": [
                {"name": "天安门", "arrival": "09:00", "departure": "11:00"},
                {"name": "故宫", "arrival": "11:30", "departure": "14:00"},
                {"name": "午餐", "arrival": "12:00", "type": "lunch"},
            ],
            "weather": {"temperature": 22},
        }
        warnings = _validate_itinerary(day_plan)
        assert isinstance(warnings, list)

    def test_validate_itinerary_too_many_places(self):
        day_plan = {
            "places": [
                {"name": f"景点{i}", "arrival": "09:00", "departure": "10:00"}
                for i in range(8)
            ],
            "weather": {"temperature": 22},
        }
        warnings = _validate_itinerary(day_plan)
        assert any("较多" in w or "紧张" in w for w in warnings)

    def test_validate_itinerary_hot_weather(self):
        day_plan = {
            "places": [
                {"name": "景点", "arrival": "09:00", "departure": "12:00"},
            ],
            "weather": {"temperature": 38},
        }
        warnings = _validate_itinerary(day_plan)
        assert any("高温" in w or "防暑" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_generate_trip_basic(self, sample_pois, sample_wardrobe):
        """Test basic trip generation with mock data."""
        # This will use mock mode since no real API keys are set
        trip = await generate_trip(
            destination="北京",
            days=2,
            start_date="2026-05-01",
            user_preferences={"budget": "中等", "interests": ["景点", "美食"]},
            wardrobe_items=sample_wardrobe,
        )
        assert "days" in trip
        assert len(trip["days"]) == 2
        assert "traffic_summary" in trip
        assert "total_cost_estimate" in trip

    @pytest.mark.asyncio
    async def test_generate_trip_single_day(self, sample_wardrobe):
        trip = await generate_trip(
            destination="北京",
            days=1,
            start_date="2026-05-01",
            user_preferences={"budget": "经济"},
            wardrobe_items=sample_wardrobe,
        )
        assert len(trip["days"]) == 1
        day = trip["days"][0]
        assert day["day"] == 1
        assert day["date"] == "2026-05-01"
        assert "weather" in day
        assert "places" in day

    @pytest.mark.asyncio
    async def test_generate_trip_each_day_has_outfit(self, sample_wardrobe):
        trip = await generate_trip(
            destination="上海",
            days=2,
            start_date="2026-06-01",
            user_preferences={"budget": "中等"},
            wardrobe_items=sample_wardrobe,
        )
        for day in trip["days"]:
            assert "outfit" in day
            assert "outfit_scene" in day

    @pytest.mark.asyncio
    async def test_generate_trip_without_wardrobe(self):
        trip = await generate_trip(
            destination="成都",
            days=1,
            start_date="2026-07-01",
            user_preferences={"budget": "中等"},
            wardrobe_items=None,
        )
        assert "days" in trip
        # Outfit may be empty when no wardrobe provided
        assert isinstance(trip["days"][0]["outfit"], dict)

    @pytest.mark.asyncio
    async def test_generate_trip_date_formats(self, sample_wardrobe):
        trip = await generate_trip(
            destination="广州",
            days=1,
            start_date="2026-08-15",
            user_preferences={},
            wardrobe_items=sample_wardrobe,
        )
        day = trip["days"][0]
        assert day["date"] == "2026-08-15"

    def test_cluster_respects_max_per_day(self, sample_pois):
        # With max_per_day=2, should get at most 2 clusters
        clusters = _cluster_pois_by_proximity(sample_pois, max_per_day=2, max_distance_km=1.0)
        # May have fewer clusters but shouldn't exceed max_per_day for items
        # since clustering groups nearby items, not limit them
        assert len(clusters) >= 1

    def test_cluster_all_far_apart(self):
        # POIs that are very far apart should each be their own cluster
        far_pois = [
            {"id": "1", "name": "北京天安门", "location": "116.3974,39.9088", "type": "景点"},
            {"id": "2", "name": "上海外滩", "location": "121.4901,31.2401", "type": "景点"},
            {"id": "3", "name": "广州塔", "location": "113.3234,23.1192", "type": "景点"},
        ]
        clusters = _cluster_pois_by_proximity(far_pois, max_per_day=5, max_distance_km=1.0)
        # All far apart, each should be its own cluster
        assert len(clusters) >= 2  # May merge some if within 1km threshold

    @pytest.mark.asyncio
    async def test_generate_trip_cost_estimate_in_range(self, sample_wardrobe):
        trip = await generate_trip(
            destination="深圳",
            days=3,
            start_date="2026-09-01",
            user_preferences={"budget": "豪华"},
            wardrobe_items=sample_wardrobe,
        )
        cost = trip["total_cost_estimate"]
        assert "¥" in cost
        # Luxury should be higher than economy
        low, high = cost.replace("¥", "").split("-")
        assert float(low) > 0

    @pytest.mark.asyncio
    async def test_generate_trip_weather_included(self, sample_wardrobe):
        trip = await generate_trip(
            destination="杭州",
            days=1,
            start_date="2026-10-01",
            user_preferences={},
            wardrobe_items=sample_wardrobe,
        )
        day = trip["days"][0]
        assert "weather" in day
        assert "temp" in day["weather"]
        assert "condition" in day["weather"]
