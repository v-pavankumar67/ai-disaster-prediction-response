"""Emergency response, shelter, and resource optimization database models."""

import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from backend.app.database import Base


class EmergencyShelter(Base):
    """Designated emergency relief camps and safe facilities."""
    __tablename__ = "emergency_shelters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    facility_type = Column(String(64), default="school_hall")  # stadium, school, hospital
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    total_capacity = Column(Integer, nullable=False)
    current_occupancy = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    has_medical_unit = Column(Boolean, default=True)
    has_generator = Column(Boolean, default=True)
    food_rations_days = Column(Float, default=7.0)
    potable_water_liters = Column(Float, default=10000.0)


class RescueUnit(Base):
    """Heterogeneous rescue response fleet."""
    __tablename__ = "rescue_units"

    id = Column(Integer, primary_key=True, index=True)
    callsign = Column(String(64), unique=True, index=True)
    vehicle_type = Column(String(32), nullable=False)  # 4x4_truck, inflatable_boat, drone, medevac_heli, ambulance
    capacity_passengers = Column(Integer, default=4)
    cargo_kg_capacity = Column(Float, default=500.0)
    current_latitude = Column(Float, nullable=False)
    current_longitude = Column(Float, nullable=False)
    status = Column(String(32), default="idle")  # idle, dispatched, refuelling, maintenance
    current_mission = Column(String(128), nullable=True)
    fuel_remaining_pct = Column(Float, default=100.0)


class ResourceInventory(Base):
    """Stock levels of emergency supplies at base depots."""
    __tablename__ = "resource_inventory"

    id = Column(Integer, primary_key=True, index=True)
    depot_name = Column(String(128), nullable=False)
    item_category = Column(String(64))  # medical, drinking_water, food_packs, blankets, life_jackets
    quantity = Column(Integer, nullable=False)
    unit = Column(String(32), default="units")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    allocated_quantity = Column(Integer, default=0)


class DispatchRoute(Base):
    """Calculated optimized convoy and rescue routes."""
    __tablename__ = "dispatch_routes"

    id = Column(Integer, primary_key=True, index=True)
    rescue_unit_id = Column(Integer, ForeignKey("rescue_units.id"), nullable=True)
    route_name = Column(String(128))
    target_cluster = Column(String(128))
    total_distance_km = Column(Float, nullable=False)
    estimated_duration_min = Column(Float, nullable=False)
    status = Column(String(32), default="planned")  # planned, en_route, completed
    waypoints_geojson = Column(JSON, nullable=False)  # Array of [lat, lon] or LineString GeoJSON
    assigned_cargo = Column(JSON)  # {medical_kits: 50, rations: 200, clean_water_liters: 1000}
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
