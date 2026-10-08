from dataclasses import dataclass
from typing import List, Dict

@dataclass
class DecisionCard:
    recommendation: str
    policy_used: str
    expected_fuel: float
    expected_travel_time: float
    sea_ice_exposure: float
    iceberg_encounter_exposure: float
    tail_risk: str
    fallback_availability: str
    data_confidence: str
    trade_off_explanation: str
    robustness_scenario_stability: str
    fallback_status: str
    data_provenance: List[Dict[str, str]]

    def explain(self) -> str:
        # Every statement must map to actual backend data.
        return f"""
RECOMMENDATION
Recommended under {self.policy_used} policy

WHY THIS ROUTE
- Expected fuel: {self.expected_fuel}
- Expected travel time: {self.expected_travel_time}
- Sea-ice exposure: {self.sea_ice_exposure}
- Iceberg encounter exposure: {self.iceberg_encounter_exposure}
- Tail-risk: {self.tail_risk}
- Fallback availability: {self.fallback_availability}
- Data confidence: {self.data_confidence}

TRADE-OFF
{self.trade_off_explanation}

ROBUSTNESS
Scenario stability: {self.robustness_scenario_stability}

FALLBACK
{self.fallback_status}

DATA
{self.data_provenance}
"""
