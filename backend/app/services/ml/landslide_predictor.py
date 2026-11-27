"""Landslide and debris-flow susceptibility prediction model."""

import math
from typing import Dict, Any
from backend.app.services.ml.base_model import BaseHazardPredictor
from backend.app.schemas.prediction import HazardRiskScore


class LandslidePredictor(BaseHazardPredictor):
    """Predicts slope failure and debris flow risk using hydro-topographic indicators."""

    def __init__(self):
        super().__init__("landslide")

    def predict_risk(self, telemetry: Dict[str, Any]) -> HazardRiskScore:
        slope_deg = telemetry.get("slope_degrees", 28.0)
        soil_sat = telemetry.get("soil_saturation_pct", 65.0)
        rain_72h = telemetry.get("rainfall_72h_mm", 120.0)

        # Landslide triggers: Slope > 25 deg + high 72h rainfall (>150mm) + saturated soil
        f_slope = min(1.0, max(0.0, (slope_deg - 15.0) / 30.0))
        f_rain = min(1.0, rain_72h / 250.0)
        f_pore = max(0.0, (soil_sat - 60.0) / 40.0)

        z = (0.45 * f_slope + 0.35 * f_rain + 0.20 * f_pore) * 5.0 - 2.4
        score = 1.0 / (1.0 + math.exp(-z))
        score = round(max(0.01, min(0.99, score)), 3)
        level = self.classify_risk_level(score)

        factors = {
            "topographical_shear_stress": round(f_slope, 3),
            "antecedent_moisture_load": round(f_rain, 3),
            "pore_water_pressure": round(f_pore, 3)
        }

        action = "Geotechnical sensors normal."
        if level in ["high", "critical"]:
            action = "Pre-emptively close mountain pass corridors, evacuate downslope hamlets, and stage heavy earth-moving excavators."

        return HazardRiskScore(
            disaster_type="landslide",
            risk_score=score,
            risk_level=level,
            confidence=0.86,
            primary_trigger=f"Steep slope ({slope_deg:.1f}°) with {rain_72h:.1f}mm 72h rain accumulation",
            contributing_factors=factors,
            recommended_action=action
        )
