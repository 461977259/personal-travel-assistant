from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.weather import router as weather_router

app = FastAPI(title="Personal Travel Assistant", version="0.1.0")

app.include_router(health_router, prefix="/api")
app.include_router(weather_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
