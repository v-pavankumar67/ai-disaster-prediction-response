"""Tropical Cyclone and Storm Surge risk prediction model."""

import math
from typing import Dict, Any
from backend.app.services.ml.base_model import BaseHazardPredictor
from backend.app.schemas.prediction import HazardRiskScore


class CyclonePredictor(BaseHazardPredictor):
    """Predicts tropical cyclone intensification and coastal landfall hazard."""

    def __init__(self):
        super().__init__("cyclone")

    def predict_risk(self, telemetry: Dict[str, Any]) -> HazardRiskScore:
        wind_speed = telemetry.get("wind_speed_kmh", 30.0)
        pressure = telemetry.get("surface_pressure_hpa", 1012.0)
        sst = telemetry.get("sea_surface_temp_c", 28.0)

        # Cyclone triggers: Low central pressure (<1000 hPa) & high winds (>65 km/h) & warm waters (>26.5 C)
        pressure_drop = max(0.0, 1013.25 - pressure)
        f_pressure = min(1.0, pressure_drop / 35.0)
        f_wind = min(1.0, wind_speed / 120.0)
        f_sst = 1.0 if sst >= 26.5 else 0.2

        z = (0.50 * f_wind + 0.40 * f_pressure + 0.10 * f_sst) * 5.0 - 2.2
        score = 1.0 / (1.0 + math.exp(-z))
        score = round(max(0.01, min(0.99, score)), 3)
        level = self.classify_risk_level(score)

        factors = {
            "pressure_deficit": round(f_pressure, 3),
            "sustained_wind_intensity": round(f_wind, 3),
            "thermodynamic_potential": round(f_sst, 3)
        }

        action = "Standard coastal marine watch."
        if level in ["high", "critical"]:
            action = "Activate storm shelters, halt harbor operations, secure coastal power lines, and stage multi-utility evacuation units."

        return HazardRiskScore(
            disaster_type="cyclone",
            risk_score=score,
            risk_level=level,
            confidence=0.88,
            primary_trigger=f"Wind gusts {wind_speed:.1f} km/h with central pressure drop to {pressure:.1f} hPa",
            contributing_factors=factors,
            recommended_action=action
        )
