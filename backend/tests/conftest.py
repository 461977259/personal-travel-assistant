import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
def test_client():
    from app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)

@pytest.fixture
def mock_weather_response():
    return {
        "temp": 22,
        "wind_level": 3,
        "humidity": 65,
        "precipitation": 0,
        "condition": "晴"
    }

@pytest.fixture
def mock_amap_response():
    return {
        "pois": [{"name": "故宫", "location": "116.3974,39.9088"}]
    }
