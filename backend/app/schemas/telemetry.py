"""Pydantic schemas for telemetry and observation ingestion."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class SensorDataCreate(BaseModel):
    sensor_id: str
    sensor_type: str = Field(..., description="rain_gauge, soil_moisture, anemometer, thermometer")
    latitude: float
    longitude: float
    value: float
    unit: str
    battery_level: Optional[float] = 100.0


class SensorDataResponse(SensorDataCreate):
    id: int
    status: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


class RiverGaugeCreate(BaseModel):
    station_id: str
    river_name: str
    latitude: float
    longitude: float
    water_level_meters: float
    danger_level_meters: float
    discharge_m3_s: Optional[float] = 0.0
    rate_of_rise_m_h: Optional[float] = 0.0


class RiverGaugeResponse(RiverGaugeCreate):
    id: int
    is_overflowing: bool
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


class WeatherReportResponse(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    temperature_c: float
    relative_humidity: float
    precipitation_mm_h: float
    wind_speed_kmh: float
    wind_direction_deg: float
    surface_pressure_hpa: float
    source: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


class CrowdReportCreate(BaseModel):
    source_platform: Optional[str] = "citizen_app"
    latitude: float
    longitude: float
    raw_text: str


class CrowdReportResponse(CrowdReportCreate):
    id: int
    extracted_disaster_type: Optional[str]
    urgency_score: float
    verified: bool
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
