from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum
import datetime
from ingestion.providers import DataQuality

class ScenarioType(Enum):
    EXPECTED_FORCING = "EXPECTED_FORCING"
    HIGHER_SEA_ICE_FUTURE = "HIGHER_SEA_ICE_FUTURE"
    ALTERNATIVE_ICEBERG_DRIFT = "ALTERNATIVE_ICEBERG_DRIFT"
    WIND_PERTURBATION = "WIND_PERTURBATION"
    CURRENT_PERTURBATION = "CURRENT_PERTURBATION"
    JOINT_PERTURBATION = "JOINT_PERTURBATION"

@dataclass
class HazardScenario:
    scenario_id: str
    parent_forecast_id: str
    perturbation_definition: str
    valid_time: datetime.datetime
    environment_snapshot: Dict[str, Any]
    uncertainty_metadata: Dict[str, float]
    generation_method: str
    model_version: str

class ScenarioGenerator:
    def __init__(self, model_version: str = "v1.0"):
        self.model_version = model_version

    def generate_expected_forcing(self, base_forecast: Any) -> HazardScenario:
        return HazardScenario(
            scenario_id="scen_expected",
            parent_forecast_id="fcst_1",
            perturbation_definition="none",
            valid_time=datetime.datetime.utcnow(),
            environment_snapshot={},
            uncertainty_metadata={"base_model_uncertainty": 0.1},
            generation_method="baseline",
            model_version=self.model_version
        )

    def generate_higher_sea_ice_future(self, base_forecast: Any, uncertainty_spread: float) -> HazardScenario:
        return HazardScenario(
            scenario_id="scen_high_ice",
            parent_forecast_id="fcst_1",
            perturbation_definition="sic_plus_1_std",
            valid_time=datetime.datetime.utcnow(),
            environment_snapshot={"sic_modifier": uncertainty_spread},
            uncertainty_metadata={"spread_used": uncertainty_spread},
            generation_method="statistical_upper_bound",
            model_version=self.model_version
        )

    def generate_ensemble(self, base_forecast: Any, uncertainty_spread: float) -> List[HazardScenario]:
        return [
            self.generate_expected_forcing(base_forecast),
            self.generate_higher_sea_ice_future(base_forecast, uncertainty_spread)
        ]
