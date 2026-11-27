"""Heatwave and thermal distress prediction model."""

import math
from typing import Dict, Any
from backend.app.services.ml.base_model import BaseHazardPredictor
from backend.app.schemas.prediction import HazardRiskScore


class HeatwavePredictor(BaseHazardPredictor):
    """Predicts extreme thermal stress and mortality risk using the Heat Index."""

    def __init__(self):
        super().__init__("heatwave")

    def predict_risk(self, telemetry: Dict[str, Any]) -> HazardRiskScore:
        temp_c = telemetry.get("temperature_c", 34.0)
        humidity = telemetry.get("relative_humidity", 65.0)

        # NOAA Apparent Heat Index approximation
        t_f = temp_c * 9.0 / 5.0 + 32.0
        hi_f = 0.5 * (t_f + 61.0 + ((t_f - 68.0) * 1.2) + (humidity * 0.094))
        if hi_f >= 80.0:
            hi_f = (-42.379 + 2.04901523 * t_f + 10.14333127 * humidity
                    - 0.22475541 * t_f * humidity - 0.00683783 * (t_f ** 2)
                    - 0.05481717 * (humidity ** 2) + 0.00122874 * (t_f ** 2) * humidity
                    + 0.00085282 * t_f * (humidity ** 2) - 0.00000199 * (t_f ** 2) * (humidity ** 2))
        hi_c = (hi_f - 32.0) * 5.0 / 9.0

        # Normalized heatwave score
        f_hi = min(1.0, max(0.0, (hi_c - 35.0) / 18.0))
        z = f_hi * 5.0 - 2.5
        score = 1.0 / (1.0 + math.exp(-z))
        score = round(max(0.01, min(0.99, score)), 3)
        level = self.classify_risk_level(score)

        factors = {
            "apparent_heat_index_c": round(hi_c, 1),
            "ambient_temp_c": round(temp_c, 1),
            "humidity_burden": round(humidity / 100.0, 2)
        }

        action = "Normal seasonal conditions."
        if level in ["high", "critical"]:
            action = "Open air-conditioned cooling centers, distribute electrolyte rations, and mandate hydration pauses for outdoor workers."

        return HazardRiskScore(
            disaster_type="heatwave",
            risk_score=score,
            risk_level=level,
            confidence=0.93,
            primary_trigger=f"Apparent Heat Index {hi_c:.1f}°C (Dry bulb {temp_c:.1f}°C @ {humidity:.0f}% RH)",
            contributing_factors=factors,
            recommended_action=action
        )
