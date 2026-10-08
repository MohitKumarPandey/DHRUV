from dataclasses import dataclass
from typing import Optional

@dataclass
class ResilienceAssessment:
    scenario_stability: str
    fallback_status: str
    data_confidence: float
    tail_risk_level: str
    recovery_status: str
    overall_resilience_score: float
    resilience_derivation: str
    policy_configuration: str

class ResilienceEvaluator:
    def evaluate(self, expected_performance: float, tail_hazard: float, scenario_regret: float,
                 recovery_cost: float, fallback_accessibility: float, data_confidence: float,
                 forecast_sensitivity: float, policy_configuration: str) -> ResilienceAssessment:
        
        # Qualitative mappings
        scenario_stability = "HIGH" if scenario_regret < 0.1 else ("MEDIUM" if scenario_regret < 0.3 else "LOW")
        fallback_status = "AVAILABLE" if fallback_accessibility > 0.8 else ("LIMITED" if fallback_accessibility > 0.3 else "NONE")
        tail_risk_level = "LOW" if tail_hazard < 0.15 else ("MEDIUM" if tail_hazard < 0.4 else "HIGH")
        recovery_status = "EASY" if recovery_cost < 20 else "DIFFICULT"

        # Explicit normalization
        # Score = (Performance * 0.3) + (1-TailHazard * 0.25) + (1-ScenarioRegret * 0.2) + (Fallback * 0.15) + (DataConf * 0.1)
        score = (expected_performance * 0.3) + ((1 - tail_hazard) * 0.25) + ((1 - scenario_regret) * 0.2) + \
                (fallback_accessibility * 0.15) + (data_confidence * 0.1)
                
        derivation = "Norm: 30% ExpectedPerf, 25% (1-TailHazard), 20% (1-ScenarioRegret), 15% Fallback, 10% DataConf"

        return ResilienceAssessment(
            scenario_stability=scenario_stability,
            fallback_status=fallback_status,
            data_confidence=data_confidence,
            tail_risk_level=tail_risk_level,
            recovery_status=recovery_status,
            overall_resilience_score=score,
            resilience_derivation=derivation,
            policy_configuration=policy_configuration
        )
