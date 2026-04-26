import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./personal_travel.db")

# Third-party API keys (to be configured via environment variables)
HEFENG_WEATHER_KEY = os.getenv("HEFENG_WEATHER_KEY", "")
AMAP_KEY = os.getenv("AMAP_KEY", "")
FLIGGY_KEY = os.getenv("FLIGGY_KEY", "")
TENCENT_CI_SECRET_ID = os.getenv("TENCENT_CI_SECRET_ID", "")
TENCENT_CI_SECRET_KEY = os.getenv("TENCENT_CI_SECRET_KEY", "")
