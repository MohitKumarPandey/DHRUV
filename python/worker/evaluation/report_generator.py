from dataclasses import dataclass
from typing import List, Any
import datetime
from agent.decision_card import DecisionCard
from state.mission_state import MissionState

@dataclass
class MissionReport:
    mission_info: MissionState
    data_sources: List[Any]
    sea_ice_forecast: Any
    iceberg_forecast: Any
    candidate_routes: List[Any]
    selected_route: Any
    stress_test_results: Any
    decision_explanation: DecisionCard
    audit_trail: List[Any]

class ReportGenerator:
    def generate_report(self, state: MissionState, decision: DecisionCard) -> MissionReport:
        # The report must clearly distinguish observed, forecast, predicted, scenario-generated, derived metric
        pass
