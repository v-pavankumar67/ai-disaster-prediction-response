"""Pydantic schemas for AI risk prediction across the 6 disaster types."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class PredictionRequest(BaseModel):
    region_name: str = Field(default="Kerala_Coastal_Basin", description="Target region name")
    latitude: float = Field(default=9.9312, description="Target center latitude")
    longitude: float = Field(default=76.2673, description="Target center longitude")
    horizon_hours: int = Field(default=24, ge=1, le=72, description="Forecast horizon in hours")
    include_sensor_telemetry: bool = Field(default=True, description="Query live/cached sensor telemetry")


class HazardRiskScore(BaseModel):
    disaster_type: str
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Normalized risk score 0.0 - 1.0")
    risk_level: str = Field(..., description="low, moderate, high, critical")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    primary_trigger: str
    contributing_factors: Dict[str, float]
    recommended_action: str


class MultiHazardPredictionResponse(BaseModel):
    region_name: str
    latitude: float
    longitude: float
    evaluation_time: datetime
    horizon_hours: int
    overall_threat_level: str
    primary_hazard: str
    hazards: List[HazardRiskScore]
    summary: str
