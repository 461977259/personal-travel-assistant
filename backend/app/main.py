from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.weather import router as weather_router
from app.api.wardrobe import router as wardrobe_router
from app.api.fliggy import router as fliggy_router
from app.api.amap import router as amap_router
from app.api.tencent_ci import router as tencent_ci_router
from app.api.copywriting import router as copywriting_router
from app.api.outfit import router as outfit_router
from app.api.trip import router as trip_router

app = FastAPI(title="Personal Travel Assistant", version="0.1.0")

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
