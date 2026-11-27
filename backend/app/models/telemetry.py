"""Telemetry, Sensor, and Weather database models."""

import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from backend.app.database import Base


class SensorReading(Base):
    """IoT Environmental Telemetry (Rainfall, Soil Moisture, Temp, Wind)."""
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(64), index=True)
    sensor_type = Column(String(32))  # rain_gauge, soil_moisture, anemometer, thermometer
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(16))
    battery_level = Column(Float, default=100.0)
    status = Column(String(16), default="active")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)


class RiverGaugeReading(Base):
    """River hydrological telemetry (water level, discharge rate)."""
    __tablename__ = "river_gauge_readings"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(64), index=True)
    river_name = Column(String(128))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    water_level_meters = Column(Float, nullable=False)
    danger_level_meters = Column(Float, nullable=False)
    discharge_m3_s = Column(Float, default=0.0)
    rate_of_rise_m_h = Column(Float, default=0.0)
    is_overflowing = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)


class WeatherObservation(Base):
    """Atmospheric conditions from weather stations or satellite models."""
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(128))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=False)
    relative_humidity = Column(Float, nullable=False)
    precipitation_mm_h = Column(Float, default=0.0)
    wind_speed_kmh = Column(Float, default=0.0)
    wind_direction_deg = Column(Float, default=0.0)
    surface_pressure_hpa = Column(Float, default=1013.25)
    source = Column(String(64), default="open-meteo")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)


class CrowdReport(Base):
    """Crowdsourced and social media distress alerts with NLP extraction."""
    __tablename__ = "crowd_reports"

    id = Column(Integer, primary_key=True, index=True)
    source_platform = Column(String(32), default="citizen_app")  # twitter, app, sms
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    raw_text = Column(Text, nullable=False)
    extracted_disaster_type = Column(String(32))  # flood, fire, landslide, etc.
    urgency_score = Column(Float, default=0.5)    # 0.0 to 1.0
    verified = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
