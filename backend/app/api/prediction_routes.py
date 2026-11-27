"""AI Multi-Hazard Risk Prediction API routes."""

from fastapi import APIRouter, Body
from backend.app.schemas.prediction import PredictionRequest, MultiHazardPredictionResponse
from backend.app.services.ml.ensemble_engine import MultiHazardEnsembleEngine
from backend.app.services.ingestion.weather_service import WeatherIngestionService
from backend.app.services.ingestion.iot_service import IoTSensorService

router = APIRouter(prefix="/prediction", tags=["AI Multi-Hazard Risk Prediction"])
ensemble_engine = MultiHazardEnsembleEngine()


@router.post("/evaluate", response_model=MultiHazardPredictionResponse, summary="Evaluate 6 disaster risks")
def evaluate_disaster_risk(req: PredictionRequest = Body(...)):
    # 1. Fetch live telemetry or assemble state vector
    weather = WeatherIngestionService.get_weather_forecast(req.latitude, req.longitude)
    river_gauges = IoTSensorService.get_river_gauges(req.latitude, req.longitude)
    soil_probes = IoTSensorService.get_soil_moisture_sensors(req.latitude, req.longitude)

    # 2. Extract composite telemetry parameters
    max_river_ratio = max(g["water_level_meters"] / g["danger_level_meters"] for g in river_gauges)
    avg_soil_sat = sum(s["volumetric_water_content_pct"] for s in soil_probes) / len(soil_probes)

    telemetry_state = {
        "precipitation_mm_h": weather.get("precipitation_mm_h", 65.0),
        "temperature_c": weather.get("temperature_c", 28.0),
        "relative_humidity": weather.get("relative_humidity", 85.0),
        "wind_speed_kmh": weather.get("wind_speed_kmh", 55.0),
        "surface_pressure_hpa": weather.get("surface_pressure_hpa", 1002.0),
        "soil_saturation_pct": avg_soil_sat,
        "river_level_ratio": max_river_ratio,
        "slope_degrees": 28.5,
        "rainfall_72h_mm": 195.0,
        "ndvi": 0.32,
        "precipitation_deficit_90d_pct": 15.0,
        "reservoir_storage_pct": 75.0,
        "sea_surface_temp_c": 29.2
    }

    # 3. Execute multi-hazard ensemble scoring
    response = ensemble_engine.evaluate_all_hazards(
        region_name=req.region_name,
        lat=req.latitude,
        lon=req.longitude,
        telemetry=telemetry_state,
        horizon_hours=req.horizon_hours
    )
    return response


@router.get("/hazards-list", summary="List supported disaster types")
def list_supported_hazards():
    return {
        "supported_disasters": [
            {"id": "flood", "name": "Flood & Inundation", "physics_engine": "2D Hydro Cellular Automata"},
            {"id": "cyclone", "name": "Tropical Cyclone & Surge", "physics_engine": "Pressure Gradient & Wind Field"},
            {"id": "wildfire", "name": "Wildfire & Bushfire", "physics_engine": "Rothermel Rate of Spread"},
            {"id": "landslide", "name": "Landslide & Mudflow", "physics_engine": "Infinite Slope Factor of Safety"},
            {"id": "heatwave", "name": "Extreme Heatwave", "physics_engine": "Apparent Heat Index & Wet-Bulb"},
            {"id": "drought", "name": "Severe Drought", "physics_engine": "SPI / SPEI Deficit Accumulation"}
        ]
    }
