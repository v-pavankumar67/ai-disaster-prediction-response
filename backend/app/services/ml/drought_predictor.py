"""Agricultural and hydrological drought prediction model."""

import math
from typing import Dict, Any
from backend.app.services.ml.base_model import BaseHazardPredictor
from backend.app.schemas.prediction import HazardRiskScore


class DroughtPredictor(BaseHazardPredictor):
    """Predicts hydrological & agricultural drought vulnerability (SPI/SPEI proxy)."""

    def __init__(self):
        super().__init__("drought")

    def predict_risk(self, telemetry: Dict[str, Any]) -> HazardRiskScore:
        precip_deficit_pct = telemetry.get("precipitation_deficit_90d_pct", 35.0)
        reservoir_storage_pct = telemetry.get("reservoir_storage_pct", 48.0)
        soil_sat = telemetry.get("soil_saturation_pct", 40.0)

        # Drought triggers: 90-day rainfall deficit > 50%, reservoirs < 30%, soil moisture < 20%
        f_precip_def = min(1.0, precip_deficit_pct / 80.0)
        f_reservoir_def = max(0.0, min(1.0, (60.0 - reservoir_storage_pct) / 50.0))
        f_soil_dry = max(0.0, min(1.0, (50.0 - soil_sat) / 40.0))

        z = (0.45 * f_precip_def + 0.35 * f_reservoir_def + 0.20 * f_soil_dry) * 4.5 - 2.2
        score = 1.0 / (1.0 + math.exp(-z))
        score = round(max(0.01, min(0.99, score)), 3)
        level = self.classify_risk_level(score)

        factors = {
            "90d_rainfall_deficit": round(f_precip_def, 3),
            "reservoir_depletion": round(f_reservoir_def, 3),
            "rootzone_soil_dryness": round(f_soil_dry, 3)
        }

        action = "Water reserves sufficient."
        if level in ["high", "critical"]:
            action = "Impose municipal water rationing, deploy emergency water tanker caravans, and release agricultural drought subsidies."

        return HazardRiskScore(
            disaster_type="drought",
            risk_score=score,
            risk_level=level,
            confidence=0.87,
            primary_trigger=f"90-day rainfall deficit at {precip_deficit_pct:.1f}% with reservoirs at {reservoir_storage_pct:.1f}%",
            contributing_factors=factors,
            recommended_action=action
        )
