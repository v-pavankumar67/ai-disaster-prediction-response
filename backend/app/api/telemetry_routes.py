"""Telemetry and Sensor ingestion API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Any, Dict, List

from backend.app.database import get_db
from backend.app.services.ingestion.weather_service import WeatherIngestionService
from backend.app.services.ingestion.iot_service import IoTSensorService
from backend.app.services.ingestion.satellite_service import SatelliteService
from backend.app.services.ingestion.social_nlp_service import SocialNLPService
from backend.app.schemas.telemetry import CrowdReportCreate, CrowdReportResponse

router = APIRouter(prefix="/telemetry", tags=["Telemetry & Data Ingestion"])


@router.get("/weather", summary="Get live atmospheric weather data")
def get_weather(lat: float = Query(9.9312), lon: float = Query(76.2673)):
    return WeatherIngestionService.get_weather_forecast(lat, lon)


@router.get("/river-gauges", summary="Get real-time river stage & flood sensors")
def get_river_gauges(lat: float = Query(9.9312), lon: float = Query(76.2673)):
    return IoTSensorService.get_river_gauges(lat, lon)


@router.get("/soil-moisture", summary="Get soil saturation probe telemetry")
def get_soil_moisture(lat: float = Query(9.9312), lon: float = Query(76.2673)):
    return IoTSensorService.get_soil_moisture_sensors(lat, lon)


@router.get("/satellite", summary="Get remote sensing thermal hotspots and SAR water mask")
def get_satellite(lat: float = Query(9.9312), lon: float = Query(76.2673)):
    return {
        "thermal_anomalies": SatelliteService.get_thermal_anomalies(lat, lon),
        "sar_water_mask": SatelliteService.get_sar_surface_water_mask(lat, lon)
    }


@router.get("/alerts", summary="Return deduplicated user-local disaster warnings from live weather and satellite sources")
def get_local_alerts(
    lat: float = Query(9.9312),
    lon: float = Query(76.2673),
    radius_km: float = Query(60.0, ge=1.0, le=500.0),
):
    weather = WeatherIngestionService.get_weather_forecast(lat, lon)
    alerts: List[Dict[str, Any]] = []

    weather_source = weather.get("source", "")
    if weather_source == "Open-Meteo Live API":
        if weather.get("precipitation_mm_h", 0) >= 30:
            alerts.append({
                "type": "flood",
                "source": "Open-Meteo Live API",
                "title": "Heavy rainfall alert",
                "message": f"Rainfall intensity {weather.get('precipitation_mm_h')} mm/h near {lat}, {lon} may raise local flood risk.",
                "latitude": lat,
                "longitude": lon,
                "severity": "high",
            })
        if weather.get("wind_speed_kmh", 0) >= 40:
            alerts.append({
                "type": "wind",
                "source": "Open-Meteo Live API",
                "title": "High wind warning",
                "message": f"Wind speed {weather.get('wind_speed_kmh')} km/h may threaten exposed settlements.",
                "latitude": lat,
                "longitude": lon,
                "severity": "moderate",
            })

    for anomaly in SatelliteService.get_thermal_anomalies(lat, lon):
        warning = {
            "type": "wildfire",
            "source": "VIIRS-SNPP",
            "title": "Satellite hotspot alert",
            "message": "Thermal anomaly detected near the user region by satellite observation.",
            "latitude": anomaly.get("latitude", lat),
            "longitude": anomaly.get("longitude", lon),
            "severity": "high",
            "satellite": anomaly.get("satellite", "VIIRS-SNPP"),
        }
        if SatelliteService.haversine_km(lat, lon, warning["latitude"], warning["longitude"]) <= radius_km:
            alerts.append(warning)

    water_mask = SatelliteService.get_sar_surface_water_mask(lat, lon)
    water_distance = SatelliteService.haversine_km(lat, lon, lat, lon)
    if water_mask.get("detected_water_expansion_pct", 0) >= 150:
        alerts.append({
            "type": "flood",
            "source": "Sentinel-1A SAR",
            "title": "Satellite inundation warning",
            "message": "Sentinel-1 SAR detected major water expansion near the active area.",
            "latitude": lat,
            "longitude": lon,
            "severity": "critical",
            "satellite": water_mask.get("satellite", "Sentinel-1A SAR"),
        })

    deduped = SatelliteService.deduplicate_alerts(alerts)
    filtered = []
    for alert in deduped:
        px = float(alert.get("latitude", lat))
        py = float(alert.get("longitude", lon))
        dist = SatelliteService.haversine_km(lat, lon, px, py)
        if dist <= radius_km:
            alert["distance_km"] = round(dist, 2)
            filtered.append(alert)

    return {
        "location": {"latitude": lat, "longitude": lon},
        "radius_km": radius_km,
        "alert_count": len(filtered),
        "alerts": filtered,
    }


@router.post("/crowd-report", summary="Submit crowdsourced citizen distress report")
def submit_crowd_report(report: CrowdReportCreate):
    nlp_analysis = SocialNLPService.analyze_report(report.raw_text)
    return {
        "status": "INGESTED_AND_TRIAGED",
        "input": report.dict(),
        "nlp_analysis": nlp_analysis
    }
