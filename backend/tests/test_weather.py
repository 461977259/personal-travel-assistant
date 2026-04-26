import os
from app.integrations.weather import _mock_weather, _mock_geo


class TestWeatherMock:
    """Tests using mock data (default mode)."""

    def test_mock_geo(self):
        result = _mock_geo("北京")
        assert result["name"] == "北京"
        assert result["lat"] == 39.904
        assert result["lon"] == 116.391

    def test_mock_geo_unknown_city(self):
        result = _mock_geo("未知城市")
        assert result["name"] == "未知城市"

    def test_mock_weather(self):
        result = _mock_weather("北京")
        assert "temperature" in result
        assert "wind_speed" in result
        assert "humidity" in result
        assert "condition" in result
        assert result["city"] == "北京"


class TestWeatherAPI:
    """Integration tests for the /api/weather endpoint."""

    def test_weather_endpoint(self):
        os.environ["WEATHER_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/weather?city=北京")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        weather = data["data"]
        assert "temperature" in weather
        assert "condition" in weather

    def test_weather_endpoint_multiple_cities(self):
        os.environ["WEATHER_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        for city in ["上海", "广州", "深圳"]:
            response = client.get(f"/api/weather?city={city}")
            assert response.status_code == 200
            assert response.json()["data"]["city"] == city
