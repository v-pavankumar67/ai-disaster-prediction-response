"""Wildfire and brushfire danger prediction model."""

import math
from typing import Dict, Any
from backend.app.services.ml.base_model import BaseHazardPredictor
from backend.app.schemas.prediction import HazardRiskScore


class WildfirePredictor(BaseHazardPredictor):
    """Predicts wildfire ignition potential and rate-of-spread hazard (FWI-derived)."""

    def __init__(self):
        super().__init__("wildfire")

    def predict_risk(self, telemetry: Dict[str, Any]) -> HazardRiskScore:
        temp_c = telemetry.get("temperature_c", 25.0)
        humidity = telemetry.get("relative_humidity", 50.0)
        wind_speed = telemetry.get("wind_speed_kmh", 15.0)
        ndvi = telemetry.get("ndvi", 0.4)  # Low NDVI indicates dead/dry vegetation

        # High risk: High temp, low humidity (<30%), high wind, dry vegetation
        f_temp = max(0.0, min(1.0, (temp_c - 20.0) / 25.0))
        f_dry_air = max(0.0, min(1.0, (70.0 - humidity) / 50.0))
        f_wind = min(1.0, wind_speed / 60.0)
        f_fuel = max(0.0, min(1.0, (0.6 - ndvi) / 0.5))

        z = (0.35 * f_temp + 0.35 * f_dry_air + 0.20 * f_wind + 0.10 * f_fuel) * 5.0 - 2.5
        score = 1.0 / (1.0 + math.exp(-z))
        score = round(max(0.01, min(0.99, score)), 3)
        level = self.classify_risk_level(score)

        factors = {
            "thermal_forcing": round(f_temp, 3),
            "atmospheric_dryness": round(f_dry_air, 3),
            "wind_propagation": round(f_wind, 3),
            "fuel_aridity": round(f_fuel, 3)
        }

        action = "Maintain routine forest perimeter monitoring."
        if level in ["high", "critical"]:
            action = "Issue red flag warning, deploy aerial fire retardant units, and mobilize community containment corridors."

        return HazardRiskScore(
            disaster_type="wildfire",
            risk_score=score,
            risk_level=level,
            confidence=0.89,
            primary_trigger=f"Temp {temp_c:.1f}°C with dry air ({humidity:.1f}%) and wind {wind_speed:.1f} km/h",
            contributing_factors=factors,
            recommended_action=action
        )
