"""Main entry point for AI Disaster Prediction & Response Platform FastAPI Backend."""

import os
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import inspect, text

from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.models.user import User
from backend.app.security import get_optional_current_user
from backend.app.api.auth_routes import router as auth_router, seed_demo_account
from backend.app.api.incident_routes import router as incident_router
from backend.app.api.telemetry_routes import router as telemetry_router
from backend.app.api.prediction_routes import router as prediction_router
from backend.app.api.simulation_routes import router as simulation_router
from backend.app.api.decision_routes import router as decision_router
from backend.app.api.optimization_routes import router as optimization_router
from backend.app.api.websocket_routes import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes database tables on startup."""
    try:
        Base.metadata.create_all(bind=engine)
        _migrate_user_location_columns()
        seed_demo_account()
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Warning initializing database tables: {e}")
    yield


def _migrate_user_location_columns():
    """Add geocoded coordinates to user tables created by earlier versions."""
    columns = {column["name"] for column in inspect(engine).get_columns("users")}
    with engine.begin() as connection:
        if "latitude" not in columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN latitude FLOAT"))
        if "longitude" not in columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN longitude FLOAT"))


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-Grade Multi-Hazard AI Disaster Prediction, Physics Simulation, Decision Triage, and Resource Optimization Platform.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local and web development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(incident_router, prefix="/api")
app.include_router(telemetry_router, prefix="/api")
app.include_router(prediction_router, prefix="/api")
app.include_router(simulation_router, prefix="/api")
app.include_router(decision_router, prefix="/api")
app.include_router(optimization_router, prefix="/api")
app.include_router(websocket_router, prefix="/api")


@app.get("/health", tags=["System"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "HEALTHY",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


# Mount Static Frontend
if settings.STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

    @app.get("/login", include_in_schema=False)
    async def serve_login(user: User = Depends(get_optional_current_user)):
        if user is not None:
            return RedirectResponse("/", status_code=303)
        return FileResponse(str(settings.STATIC_DIR / "login.html"))

    @app.get("/register", include_in_schema=False)
    async def serve_register(user: User = Depends(get_optional_current_user)):
        if user is not None:
            return RedirectResponse("/", status_code=303)
        return FileResponse(str(settings.STATIC_DIR / "register.html"))

    @app.get("/", include_in_schema=False)
    async def serve_index(user: User = Depends(get_optional_current_user)):
        if user is None:
            return RedirectResponse("/login", status_code=303)
        index_file = settings.STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend index.html not found. Access API documentation at /docs."}
