"""API routers package."""

from backend.app.api.telemetry_routes import router as telemetry_router
from backend.app.api.prediction_routes import router as prediction_router
from backend.app.api.simulation_routes import router as simulation_router
from backend.app.api.decision_routes import router as decision_router
from backend.app.api.optimization_routes import router as optimization_router
from backend.app.api.websocket_routes import router as websocket_router

__all__ = [
    "telemetry_router",
    "prediction_router",
    "simulation_router",
    "decision_router",
    "optimization_router",
    "websocket_router",
]
