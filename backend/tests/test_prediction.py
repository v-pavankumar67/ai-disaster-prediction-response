"""Unit tests for the 6 AI Disaster Predictors and Ensemble Coordinator."""

import pytest
from backend.app.services.ml.flood_predictor import FloodPredictor
from backend.app.services.ml.cyclone_predictor import CyclonePredictor
from backend.app.services.ml.wildfire_predictor import WildfirePredictor
from backend.app.services.ml.landslide_predictor import LandslidePredictor
from backend.app.services.ml.heatwave_predictor import HeatwavePredictor
from backend.app.services.ml.drought_predictor import DroughtPredictor
from backend.app.services.ml.ensemble_engine import MultiHazardEnsembleEngine


def test_flood_predictor_heavy_rain():
    predictor = FloodPredictor()
    telemetry = {
        "precipitation_mm_h": 95.0,
        "soil_saturation_pct": 92.0,
        "river_level_ratio": 1.35
    }
    result = predictor.predict_risk(telemetry)
    assert result.disaster_type == "flood"
    assert result.risk_score >= 0.70
    assert result.risk_level in ["high", "critical"]


def test_cyclone_predictor_deep_depression():
    predictor = CyclonePredictor()
    telemetry = {
        "wind_speed_kmh": 110.0,
        "surface_pressure_hpa": 985.0,
        "sea_surface_temp_c": 29.5
    }
    result = predictor.predict_risk(telemetry)
    assert result.disaster_type == "cyclone"
    assert result.risk_score >= 0.75
    assert result.risk_level in ["high", "critical"]


def test_wildfire_predictor_dry_hot():
    predictor = WildfirePredictor()
    telemetry = {
        "temperature_c": 42.0,
        "relative_humidity": 14.0,
        "wind_speed_kmh": 50.0,
        "ndvi": 0.15
    }
    result = predictor.predict_risk(telemetry)
    assert result.disaster_type == "wildfire"
    assert result.risk_score >= 0.75


def test_landslide_predictor_steep_slope():
    predictor = LandslidePredictor()
    telemetry = {
        "slope_degrees": 38.0,
        "rainfall_72h_mm": 240.0,
        "soil_saturation_pct": 95.0
    }
    result = predictor.predict_risk(telemetry)
    assert result.disaster_type == "landslide"
    assert result.risk_score >= 0.70


def test_heatwave_predictor():
    predictor = HeatwavePredictor()
    telemetry = {
        "temperature_c": 46.0,
        "relative_humidity": 55.0
    }
    result = predictor.predict_risk(telemetry)
    assert result.disaster_type == "heatwave"
    assert result.risk_score >= 0.80


def test_drought_predictor():
    predictor = DroughtPredictor()
    telemetry = {
        "precipitation_deficit_90d_pct": 75.0,
        "reservoir_storage_pct": 18.0,
        "soil_saturation_pct": 12.0
    }
    result = predictor.predict_risk(telemetry)
    assert result.disaster_type == "drought"
    assert result.risk_score >= 0.70


def test_ensemble_coordinator():
    engine = MultiHazardEnsembleEngine()
    telemetry = {
        "precipitation_mm_h": 90.0,
        "soil_saturation_pct": 92.0,
        "river_level_ratio": 1.30,
        "wind_speed_kmh": 20.0,
        "surface_pressure_hpa": 1008.0,
        "temperature_c": 27.0,
        "relative_humidity": 90.0
    }
    resp = engine.evaluate_all_hazards(
        region_name="Test_Basin",
        lat=10.0,
        lon=76.0,
        telemetry=telemetry,
        horizon_hours=24
    )
    assert resp.primary_hazard == "flood"
    assert len(resp.hazards) == 6
