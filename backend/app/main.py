from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.weather import router as weather_router
from app.api.wardrobe import router as wardrobe_router
from app.api.fliggy import router as fliggy_router
from app.api.amap import router as amap_router

app = FastAPI(title="Personal Travel Assistant", version="0.1.0")

app.include_router(health_router, prefix="/api")
app.include_router(weather_router, prefix="/api")
app.include_router(wardrobe_router, prefix="/api")
app.include_router(fliggy_router, prefix="/api")
app.include_router(amap_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
