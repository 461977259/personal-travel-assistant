from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.weather import router as weather_router
from app.api.wardrobe import router as wardrobe_router
from app.api.fliggy import router as fliggy_router
from app.api.amap import router as amap_router
from app.api.tencent_ci import router as tencent_ci_router
from app.api.copywriting import router as copywriting_router
from app.api.outfit import router as outfit_router
from app.api.trip import router as trip_router

from app.models.base import Base
from app.models.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import all models so Base.metadata knows about all tables
    from app.models import wardrobe, trip, content, user_pref, outfit_log  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Personal Travel Assistant", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(weather_router, prefix="/api")
app.include_router(wardrobe_router, prefix="/api")
app.include_router(fliggy_router, prefix="/api")
app.include_router(amap_router, prefix="/api")
app.include_router(tencent_ci_router, prefix="/api")
app.include_router(copywriting_router, prefix="/api")
app.include_router(outfit_router, prefix="/api")
app.include_router(trip_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
