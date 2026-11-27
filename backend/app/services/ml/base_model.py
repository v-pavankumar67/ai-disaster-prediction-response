"""Abstract Base Class for Hazard Predictors."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from backend.app.schemas.prediction import HazardRiskScore


class BaseHazardPredictor(ABC):
    """Base interface for all 6 specialized disaster ML predictors."""

    def __init__(self, disaster_name: str):
        self.disaster_name = disaster_name

    @abstractmethod
    def predict_risk(self, telemetry: Dict[str, Any]) -> HazardRiskScore:
        """Calculate calibrated hazard risk score and contributing factors."""
        pass

    @staticmethod
    def classify_risk_level(score: float) -> str:
        """Map score [0.0 - 1.0] to discrete emergency tier."""
        if score >= 0.80:
            return "critical"
        elif score >= 0.60:
            return "high"
        elif score >= 0.35:
            return "moderate"
        return "low"
