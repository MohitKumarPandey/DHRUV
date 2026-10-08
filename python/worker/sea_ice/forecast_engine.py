from dataclasses import dataclass
from typing import Optional, List, Dict
import datetime
from ingestion.providers import DataQuality

@dataclass
class SeaIceForecastOutput:
    valid_time: datetime.datetime
    sic_prediction: float
    uncertainty_spread: float
    source_snapshot_id: str
    model_version: str
    data_quality: DataQuality

class SeaIceForecastEngine:
    def __init__(self):
        self.model_version = "v1.0-baseline"

    def generate_persistence_baseline(self, current_sic: float, valid_time: datetime.datetime) -> SeaIceForecastOutput:
        return SeaIceForecastOutput(
            valid_time=valid_time,
            sic_prediction=current_sic,
            uncertainty_spread=0.1,  # increases with time in real implementation
            source_snapshot_id="snapshot_current",
            model_version=self.model_version + "-persistence",
            data_quality=DataQuality.YELLOW
        )

    def generate_climatological_baseline(self, climatology_sic: float, valid_time: datetime.datetime) -> SeaIceForecastOutput:
        return SeaIceForecastOutput(
            valid_time=valid_time,
            sic_prediction=climatology_sic,
            uncertainty_spread=0.2,
            source_snapshot_id="snapshot_climatology",
            model_version=self.model_version + "-climatology",
            data_quality=DataQuality.YELLOW
        )

    def generate_ml_candidate(self, features: dict, valid_time: datetime.datetime) -> SeaIceForecastOutput:
        # Do not claim ML superiority before validation
        raise NotImplementedError("ML candidate architecture is blocked waiting for valid training snapshot")

class ForecastEvaluator:
    @staticmethod
    def calculate_mae(predictions: List[float], truths: List[float]) -> float:
        return sum(abs(p - t) for p, t in zip(predictions, truths)) / len(predictions) if predictions else 0.0

    @staticmethod
    def calculate_rmse(predictions: List[float], truths: List[float]) -> float:
        import math
        return math.sqrt(sum((p - t)**2 for p, t in zip(predictions, truths)) / len(predictions)) if predictions else 0.0
