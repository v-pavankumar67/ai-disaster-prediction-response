"""Pydantic schemas for emergency response, triage, and route optimization."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ShelterResponse(BaseModel):
    id: int
    name: str
    facility_type: str
    latitude: float
    longitude: float
    total_capacity: int
    current_occupancy: int
    available_capacity: int
    is_active: bool
    has_medical_unit: bool
    has_generator: bool
    food_rations_days: float
    potable_water_liters: float


class RescueUnitResponse(BaseModel):
    id: int
    callsign: str
    vehicle_type: str
    capacity_passengers: int
    cargo_kg_capacity: float
    current_latitude: float
    current_longitude: float
    status: str
    fuel_remaining_pct: float


class OptimizationRequest(BaseModel):
    simulation_id: Optional[int] = None
    target_villages: Optional[List[str]] = None
    prioritize_medical: bool = Field(default=True, description="Prioritize high-vulnerability casualties")
    allow_boat_transfers: bool = Field(default=True, description="Include boat routes for flooded links")
    allow_drone_drops: bool = Field(default=True, description="Deploy drones for completely isolated zones")


class DispatchRouteStep(BaseModel):
    step_number: int
    instruction: str
    lat: float
    lon: float
    action: str  # pickup, dropoff_aid, evacuate_civilians, cross_bridge


class AssignedDispatchRoute(BaseModel):
    route_id: str
    unit_callsign: str
    vehicle_type: str
    origin_base: str
    destination_clusters: List[str]
    total_distance_km: float
    estimated_duration_min: float
    cargo_manifest: Dict[str, Any]
    civilians_to_evacuate: int
    waypoints: List[List[float]]  # [[lat, lon], ...]
    steps: List[DispatchRouteStep]


class OptimizationResponse(BaseModel):
    optimization_id: str
    status: str
    solver_used: str
    total_isolated_demand: int
    total_evacuated_capacity: int
    assigned_routes: List[AssignedDispatchRoute]
    activated_shelters: List[str]
    critical_unreachable_zones: List[str]
    summary: str
