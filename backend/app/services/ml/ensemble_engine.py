"""Master Multi-Hazard Risk Prediction Coordinator."""

from datetime import datetime, timezone
from typing import Dict, Any, List
from backend.app.services.ml.flood_predictor import FloodPredictor
from backend.app.services.ml.cyclone_predictor import CyclonePredictor
from backend.app.services.ml.wildfire_predictor import WildfirePredictor
from backend.app.services.ml.landslide_predictor import LandslidePredictor
from backend.app.services.ml.heatwave_predictor import HeatwavePredictor
from backend.app.services.ml.drought_predictor import DroughtPredictor
from backend.app.schemas.prediction import HazardRiskScore, MultiHazardPredictionResponse


class MultiHazardEnsembleEngine:
    """Orchestrates predictions across all 6 disaster modalities and produces unified threat intelligence."""

    def __init__(self):
        self.predictors = {
            "flood": FloodPredictor(),
            "cyclone": CyclonePredictor(),
            "wildfire": WildfirePredictor(),
            "landslide": LandslidePredictor(),
            "heatwave": HeatwavePredictor(),
            "drought": DroughtPredictor(),
        }

    def evaluate_all_hazards(
        self,
        region_name: str,
        lat: float,
        lon: float,
        telemetry: Dict[str, Any],
        horizon_hours: int = 24
    ) -> MultiHazardPredictionResponse:
        """Runs ensemble inference across all 6 hazards and ranks critical alerts."""
        hazard_scores: List[HazardRiskScore] = []

        for name, predictor in self.predictors.items():
            score_obj = predictor.predict_risk(telemetry)
            hazard_scores.append(score_obj)

        # Sort hazards by risk score descending
        hazard_scores.sort(key=lambda x: x.risk_score, reverse=True)
        primary = hazard_scores[0]

        # Determine overall threat level
        max_score = primary.risk_score
        if max_score >= 0.80:
            overall_threat = "CRITICAL"
        elif max_score >= 0.60:
            overall_threat = "HIGH"
        elif max_score >= 0.35:
            overall_threat = "MODERATE"
        else:
            overall_threat = "LOW"

        summary = (
            f"Evaluated 6 disaster types for {region_name}. Dominant threat: {primary.disaster_type.upper()} "
            f"(Score: {primary.risk_score:.2f}, Tier: {primary.risk_level.upper()}). "
            f"Trigger: {primary.primary_trigger}. Recommended: {primary.recommended_action}"
        )

        return MultiHazardPredictionResponse(
            region_name=region_name,
            latitude=lat,
            longitude=lon,
            evaluation_time=datetime.now(timezone.utc),
            horizon_hours=horizon_hours,
            overall_threat_level=overall_threat,
            primary_hazard=primary.disaster_type,
            hazards=hazard_scores,
            summary=summary
        )
