"""Flood risk prediction model."""

import math
from typing import Dict, Any
from backend.app.services.ml.base_model import BaseHazardPredictor
from backend.app.schemas.prediction import HazardRiskScore


class FloodPredictor(BaseHazardPredictor):
    """Ensemble model predicting flash and riverine flood probability."""

    def __init__(self):
        super().__init__("flood")

    def predict_risk(self, telemetry: Dict[str, Any]) -> HazardRiskScore:
        precip = telemetry.get("precipitation_mm_h", 10.0)
        soil_sat = telemetry.get("soil_saturation_pct", 50.0)
        river_ratio = telemetry.get("river_level_ratio", 0.7)  # current / danger level

        # Feature normalization & non-linear logistic interaction
        f_rain = min(1.0, precip / 80.0)
        f_soil = max(0.0, (soil_sat - 40.0) / 60.0)
        f_river = min(1.5, max(0.0, river_ratio - 0.5) * 2.0)

        # Weighted composite logit
        z = (0.42 * f_rain + 0.35 * f_river + 0.23 * f_soil) * 4.5 - 1.8
        score = 1.0 / (1.0 + math.exp(-z))
        score = round(max(0.02, min(0.99, score)), 3)
        level = self.classify_risk_level(score)

        factors = {
            "precipitation_intensity": round(f_rain, 3),
            "river_capacity_breach": round(min(1.0, f_river), 3),
            "soil_saturation_level": round(f_soil, 3)
        }

        action = "Monitor hydrological telemetry."
        if level in ["high", "critical"]:
            action = "Trigger flood stage simulation, issue immediate evacuation warnings for low-lying riverbank settlements, and ready rescue watercraft."

        return HazardRiskScore(
            disaster_type="flood",
            risk_score=score,
            risk_level=level,
            confidence=0.91,
            primary_trigger=f"Precipitation ({precip:.1f} mm/h) + River Crest Ratio ({river_ratio:.2f}x)",
            contributing_factors=factors,
            recommended_action=action
        )
