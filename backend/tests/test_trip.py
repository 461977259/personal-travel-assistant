"""
Tests for Trip API endpoints.
"""
import os
from fastapi.testclient import TestClient


class TestTripAPI:
    """Tests for /api/trip/* endpoints."""

    def test_trip_generate_basic(self, test_db):
        os.environ["FLIGGY_MOCK_MODE"] = "true"
        os.environ["AMAP_MOCK_MODE"] = "true"
        os.environ["WEATHER_MOCK_MODE"] = "true"
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            payload = {
                "destination": "北京",
                "days": 1,
                "start_date": "2026-05-01",
                "preferences": {"budget": "中等"},
            }
            response = client.post("/api/trip/generate", json=payload)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            assert "days" in data
            assert len(data["days"]) == 1
            assert data["days"][0]["day"] == 1
            assert data["days"][0]["date"] == "2026-05-01"
            assert "weather" in data["days"][0]
            assert "places" in data["days"][0]
            assert "outfit" in data["days"][0]
            assert "traffic_summary" in data
            assert "total_cost_estimate" in data
        finally:
            app.dependency_overrides.clear()

    def test_trip_generate_3_days(self, test_db):
        os.environ["FLIGGY_MOCK_MODE"] = "true"
        os.environ["AMAP_MOCK_MODE"] = "true"
        os.environ["WEATHER_MOCK_MODE"] = "true"
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            payload = {
                "destination": "北京",
                "days": 3,
                "start_date": "2026-05-01",
                "preferences": {"budget": "中等"},
            }
            response = client.post("/api/trip/generate", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert len(data["days"]) == 3
            for i, day in enumerate(data["days"]):
                assert day["day"] == i + 1
                assert f"2026-05-0{i + 1}" == day["date"]
                # Each day should have places and outfit
                assert "places" in day
                assert "outfit" in day
                # Verify weather is included
                assert "weather" in day
        finally:
            app.dependency_overrides.clear()

    def test_trip_weather_integrated(self, test_db):
        os.environ["FLIGGY_MOCK_MODE"] = "true"
        os.environ["AMAP_MOCK_MODE"] = "true"
        os.environ["WEATHER_MOCK_MODE"] = "true"
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            payload = {
                "destination": "杭州",
                "days": 2,
                "start_date": "2026-06-01",
                "preferences": {"budget": "中等"},
            }
            response = client.post("/api/trip/generate", json=payload)
            assert response.status_code == 200
            data = response.json()
            for day in data["days"]:
                # Verify weather data is present for each day
                assert "weather" in day
                assert "temp" in day["weather"]
                assert "condition" in day["weather"]
                # Destination city should be reflected somewhere
                assert "outfit_scene" in day
        finally:
            app.dependency_overrides.clear()

    def test_trip_outfit_linked(self, test_db):
        os.environ["FLIGGY_MOCK_MODE"] = "true"
        os.environ["AMAP_MOCK_MODE"] = "true"
        os.environ["WEATHER_MOCK_MODE"] = "true"
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            # Pre-populate wardrobe
            client.post("/api/wardrobe/items", json={
                "name": "白色T恤",
                "type": "上装",
                "color": "白色",
                "thickness": "薄",
                "scene": "日常",
            })
            client.post("/api/wardrobe/items", json={
                "name": "黑色裤",
                "type": "裤装",
                "color": "黑色",
                "thickness": "中等",
                "scene": "日常",
            })
            payload = {
                "destination": "上海",
                "days": 1,
                "start_date": "2026-07-01",
                "preferences": {"budget": "中等"},
                "user_id": "test_user",
            }
            response = client.post("/api/trip/generate", json=payload)
            assert response.status_code == 200
            data = response.json()
            day = data["days"][0]
            # Outfit should be linked to trip day
            assert "outfit" in day
            outfit = day["outfit"]
            assert "reason" in outfit
            assert "tips" in outfit
            # Outfit items should be from wardrobe
            if outfit.get("outfit"):
                item_names = [oi.get("item", "") for oi in outfit["outfit"]]
                assert any("白色T恤" in n or "黑色裤" in n for n in item_names)
        finally:
            app.dependency_overrides.clear()

    def test_fliggy_search_flights_mock(self):
        """Verify Fliggy flight search returns mock data correctly."""
        os.environ["FLIGGY_MOCK_MODE"] = "true"
        from app.integrations.fliggy import _mock_flights
        results = _mock_flights("北京", "上海", "2026-05-01")
        assert len(results) == 3
        assert results[0]["origin"] == "北京"
        assert results[0]["destination"] == "上海"
        assert "price" in results[0]
        assert "flight_no" in results[0]
        assert results[0]["price_unit"] == "CNY"

    def test_amap_poi_search_mock(self):
        """Verify AMap POI search returns mock data correctly."""
        os.environ["AMAP_MOCK_MODE"] = "true"
        from app.integrations.amap import _mock_pois
        results = _mock_pois("景点", "北京")
        assert len(results) == 2
        assert "name" in results[0]
        assert "location" in results[0]
        assert "type" in results[0]

    def test_tencent_ci_classify_mock(self):
        """Verify Tencent CI image classification returns mock tags."""
        os.environ["TENCENT_CI_MOCK_MODE"] = "true"
        from app.integrations.tencent_ci import _mock_classify
        # Portrait image
        tags = _mock_classify("https://example.com/portrait.jpg")
        assert "人物" in tags
        assert "人像" in tags
        # Landscape image
        tags = _mock_classify("https://example.com/landscape.jpg")
        assert "自然" in tags or "风景" in tags
        # Food image
        tags = _mock_classify("https://example.com/food_dish.jpg")
        assert "美食" in tags
        # Building image
        tags = _mock_classify("https://example.com/building.jpg")
        assert "建筑" in tags

    def test_fliggy_api_endpoint(self):
        """Verify /api/fliggy/flights endpoint with mock data."""
        os.environ["FLIGGY_MOCK_MODE"] = "true"
        from app.main import app
        client = TestClient(app)
        response = client.get(
            "/api/fliggy/flights?origin=北京&destination=上海&date=2026-05-01"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 3
        assert data["data"][0]["origin"] == "北京"
        assert data["data"][0]["destination"] == "上海"

    def test_amap_api_endpoint(self):
        """Verify /api/amap/poi endpoint with mock data."""
        os.environ["AMAP_MOCK_MODE"] = "true"
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/amap/poi?keyword=景点&city=北京")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 2

    def test_tencent_ci_api_endpoint(self):
        """Verify /api/tencent-ci/classify endpoint with mock data."""
        os.environ["TENCENT_CI_MOCK_MODE"] = "true"
        from app.main import app
        client = TestClient(app)
        response = client.post(
            "/api/tencent-ci/classify",
            json={"image_url": "https://example.com/portrait.jpg"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"]["tags"], list)
        assert len(data["data"]["tags"]) > 0
        assert "人物" in data["data"]["tags"]
