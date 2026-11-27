"""Configuration module for AI Disaster Prediction & Response Platform."""

import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if available
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AI Disaster Prediction & Response Platform")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    AUTH_SECRET_KEY: str = os.getenv("AUTH_SECRET_KEY", "")
    AUTH_SESSION_TTL_SECONDS: int = int(os.getenv("AUTH_SESSION_TTL_SECONDS", "86400"))
    DEMO_LOGIN_ENABLED: bool = os.getenv(
        "DEMO_LOGIN_ENABLED",
        "false" if ENVIRONMENT.lower() in {"production", "prod"} else "true",
    ).lower() in ("true", "1", "yes")

    if not AUTH_SECRET_KEY:
        if ENVIRONMENT.lower() in {"production", "prod"}:
            raise ValueError("Set AUTH_SECRET_KEY to a stable secret in production.")
        AUTH_SECRET_KEY = secrets.token_urlsafe(32)
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'disaster_platform.db'}")

    # Thresholds
    RISK_THRESHOLD_MODERATE: float = float(os.getenv("RISK_THRESHOLD_MODERATE", "0.40"))
    RISK_THRESHOLD_HIGH: float = float(os.getenv("RISK_THRESHOLD_HIGH", "0.70"))
    RISK_THRESHOLD_CRITICAL: float = float(os.getenv("RISK_THRESHOLD_CRITICAL", "0.85"))

    # APIs
    OPEN_METEO_API_URL: str = os.getenv("OPEN_METEO_API_URL", "https://api.open-meteo.com/v1/forecast")
    NASA_FIRMS_API_KEY: str = os.getenv("NASA_FIRMS_API_KEY", "")

    # Paths
    STATIC_DIR: Path = BASE_DIR / "frontend"
    DATA_DIR: Path = BASE_DIR / "data"
    INCIDENT_MEDIA_DIR: Path = DATA_DIR / "incident_uploads"


settings = Settings()
