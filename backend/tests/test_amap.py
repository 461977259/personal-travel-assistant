import os
from app.integrations.amap import (
    _mock_pois,
    _mock_route,
    _haversine_distance,
)


class TestAmapMock:
    """Tests for mock data functions."""

    def test_mock_pois(self):
        results = _mock_pois("景点", "北京")
        assert len(results) == 2
        assert results[0]["name"] == "北京故宫博物院"
        assert "location" in results[0]

    def test_mock_pois_restaurant(self):
        results = _mock_pois("餐厅", "北京")
        assert len(results) == 1
        assert results[0]["type"] == "餐厅"

    def test_mock_route(self):
        result = _mock_route("116.3974,39.9088", "116.4100,39.8800", "walking")
        assert result["mode"] == "walking"
        assert result["distance"] == 3500
        assert result["duration"] == 2520
        assert len(result["steps"]) > 0

    def test_haversine_distance(self):
        # Beijing coordinates to a slightly different point
        d = _haversine_distance(39.9088, 116.3974, 39.9088, 116.3974)
        assert d == 0.0
        # Known distance: ~1km
        d = _haversine_distance(39.9088, 116.3974, 39.9188, 116.3974)
        assert 1000 < d < 1200


class TestAmapAPI:
    """Integration tests for /api/amap/* endpoints."""

    def test_poi_endpoint(self):
        os.environ["AMAP_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/amap/poi?keyword=景点&city=北京")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_route_endpoint(self):
        os.environ["AMAP_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.get(
            "/api/amap/route?origin=116.3974,39.9088&destination=116.4100,39.8800&mode=walking"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "distance" in data["data"]
        assert "duration" in data["data"]

    def test_route_driving_mode(self):
        os.environ["AMAP_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.get(
            "/api/amap/route?origin=116.3974,39.9088&destination=116.4100,39.8800&mode=driving"
        )
        assert response.status_code == 200
        assert response.json()["data"]["mode"] == "driving"

    def test_distance_endpoint(self):
        os.environ["AMAP_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.get(
            "/api/amap/distance?lat1=39.9088&lon1=116.3974&lat2=39.9088&lon2=116.3974"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["distance_meters"] == 0.0
        assert "distance_km" in data["data"]

    def test_distance_real_coordinates(self):
        os.environ["AMAP_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        # Distance from Beijing to Shanghai ~1000km
        response = client.get(
            "/api/amap/distance?lat1=31.2304&lon1=121.4737&lat2=39.9042&lon2=116.4074"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["distance_km"] > 1000
