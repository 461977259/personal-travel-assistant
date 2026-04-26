import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base


@pytest.fixture
def test_db():
    """File-based SQLite test database (to share across threads in TestClient)."""
    db_path = "/tmp/test_travel.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    # Import all models so Base knows about their tables
    from app.models import wardrobe  # noqa: F401
    from app.models import content  # noqa: F401
    from app.models import trip  # noqa: F401
    from app.models import user_pref  # noqa: F401
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
        if os.path.exists(db_path):
            os.remove(db_path)


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
