import os
from app.integrations.fliggy import (
    _mock_flights,
    _mock_trains,
    _mock_hotels,
)


class TestFliggyMock:
    """Tests for mock data functions."""

    def test_mock_flights(self):
        results = _mock_flights("北京", "上海", "2026-05-01")
        assert len(results) == 3
        assert results[0]["origin"] == "北京"
        assert results[0]["destination"] == "上海"
        assert "price" in results[0]
        assert "duration_minutes" in results[0]
        assert results[0]["price_unit"] == "CNY"

    def test_mock_trains(self):
        results = _mock_trains("北京", "上海", "2026-05-01")
        assert len(results) == 3
        assert results[0]["train_type"] in ["高铁", "动车"]
        assert "price" in results[0]
        assert results[0]["price_unit"] == "CNY"

    def test_mock_hotels(self):
        results = _mock_hotels("北京", "2026-05-01", "2026-05-03")
        assert len(results) == 3
        assert "故宫" not in results[0]["name"]  # hotel name contains city
        assert "price" in results[0]
        assert results[0]["rating"] > 0


class TestFliggyAPI:
    """Integration tests for /api/fliggy/* endpoints."""

    def test_flights_endpoint(self):
        os.environ["FLIGGY_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.get(
            "/api/fliggy/flights?origin=北京&destination=上海&date=2026-05-01"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_trains_endpoint(self):
        os.environ["FLIGGY_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.get(
            "/api/fliggy/trains?origin=北京&destination=上海&date=2026-05-01"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)

    def test_hotels_endpoint(self):
        os.environ["FLIGGY_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.get(
            "/api/fliggy/hotels?city=北京&checkin=2026-05-01&checkout=2026-05-03"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        hotel = data["data"][0]
        assert "rating" in hotel
        assert "amenities" in hotel
