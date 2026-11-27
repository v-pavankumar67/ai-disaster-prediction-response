"""Machine Learning and multi-hazard prediction models package."""

from backend.app.services.ml.base_model import BaseHazardPredictor
from backend.app.services.ml.flood_predictor import FloodPredictor
from backend.app.services.ml.cyclone_predictor import CyclonePredictor
from backend.app.services.ml.wildfire_predictor import WildfirePredictor
from backend.app.services.ml.landslide_predictor import LandslidePredictor
from backend.app.services.ml.heatwave_predictor import HeatwavePredictor
from backend.app.services.ml.drought_predictor import DroughtPredictor
from backend.app.services.ml.ensemble_engine import MultiHazardEnsembleEngine

__all__ = [
    "BaseHazardPredictor",
    "FloodPredictor",
    "CyclonePredictor",
    "WildfirePredictor",
    "LandslidePredictor",
    "HeatwavePredictor",
    "DroughtPredictor",
    "MultiHazardEnsembleEngine",
]
