"""Pydantic schemas for physics-based spatial simulations."""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


class SimulationRequest(BaseModel):
    scenario_name: str = Field(default="Monsoon_Flash_Flood_Simulation", description="Simulation scenario label")
    disaster_type: str = Field(default="flood", description="flood, wildfire, landslide, or cyclone")
    total_hours: int = Field(default=48, ge=6, le=72)
    time_step_hours: float = Field(default=3.0, ge=0.5, le=6.0)
    center_latitude: float = Field(default=9.9312)
    center_longitude: float = Field(default=76.2673)
    rainfall_multiplier: float = Field(default=1.5, description="Scale rain intensity (1.0 = normal, 2.0 = extreme)")
    dam_discharge_m3_s: Optional[float] = Field(default=1200.0, description="Upstream reservoir release rate")
    wind_speed_kmh: Optional[float] = Field(default=45.0, description="Wind velocity for wildfire or cyclone")


class SeveredRoadResponse(BaseModel):
    id: int
    road_name: str
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    severance_cause: str
    water_depth_meters: float
    is_passable_for_trucks: bool
    is_passable_for_boats: bool


class SimulationStepData(BaseModel):
    step_index: int
    hour: float
    inundation_or_spread_cells: List[Dict[str, Any]]
    newly_severed_roads: List[str]
    newly_isolated_villages: List[str]
    cumulative_affected_pop: int


class SimulationResponse(BaseModel):
    simulation_id: int
    scenario_name: str
    disaster_type: str
    total_hours: int
    status: str
    submerged_area_sq_km: float
    affected_population_estimate: int
    severed_roads_count: int
    isolated_villages: List[Dict[str, Any]]
    severed_roads: List[SeveredRoadResponse]
    timesteps: List[SimulationStepData]
    created_at: datetime
