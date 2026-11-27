"""Disaster events and risk prediction database models."""

import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Enum
from backend.app.database import Base


class DisasterTypeEnum(str, enum.Enum):
    FLOOD = "flood"
    CYCLONE = "cyclone"
    WILDFIRE = "wildfire"
    LANDSLIDE = "landslide"
    HEATWAVE = "heatwave"
    DROUGHT = "drought"


class RiskLevelEnum(str, enum.Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class DisasterEvent(Base):
    """Active or historical declared disaster incidents."""
    __tablename__ = "disaster_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    disaster_type = Column(Enum(DisasterTypeEnum), nullable=False, index=True)
    severity = Column(Enum(RiskLevelEnum), default=RiskLevelEnum.MODERATE)
    region_name = Column(String(128), nullable=False)
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)
    radius_km = Column(Float, default=25.0)
    status = Column(String(32), default="active")  # active, contained, resolved
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class RiskPrediction(Base):
    """Computed AI risk assessments for spatial cells or regions."""
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(String(64), index=True)
    disaster_type = Column(Enum(DisasterTypeEnum), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)  # 0.0 to 1.0
    risk_level = Column(Enum(RiskLevelEnum), nullable=False)
    confidence = Column(Float, default=0.85)
    horizon_hours = Column(Integer, default=24)
    model_version = Column(String(64), default="ensemble-v1.0")
    contributing_factors = Column(JSON)  # {rainfall: 0.8, river_level: 0.9, slope: 0.6}
    recommended_action = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
