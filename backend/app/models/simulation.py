"""Simulation and spatial impact database models."""

import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from backend.app.database import Base


class SimulationRun(Base):
    """Execution records for physical/cellular simulation runs."""
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(128), nullable=False)
    disaster_type = Column(String(32), nullable=False)
    total_hours = Column(Integer, default=48)
    time_step_hours = Column(Float, default=1.0)
    parameters = Column(JSON)  # {rainfall_rate_mm: 85, wind_speed: 60, dam_discharge: 1200}
    affected_population_estimate = Column(Integer, default=0)
    severed_roads_count = Column(Integer, default=0)
    submerged_area_sq_km = Column(Float, default=0.0)
    status = Column(String(32), default="completed")  # running, completed, failed
    result_geojson = Column(JSON)  # Spatial polygons / hex heatmaps per timestep
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)


class SeveredRoadSegment(Base):
    """Road segments compromised by flood, fire, or landslide debris."""
    __tablename__ = "severed_road_segments"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulation_runs.id"), nullable=True)
    road_name = Column(String(128))
    start_lat = Column(Float, nullable=False)
    start_lon = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lon = Column(Float, nullable=False)
    severance_cause = Column(String(64))  # flood_inundation, fire_front, landslide_debris
    water_depth_meters = Column(Float, default=0.0)
    is_passable_for_trucks = Column(Boolean, default=False)
    is_passable_for_boats = Column(Boolean, default=True)
    estimated_clear_hours = Column(Float, default=24.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
