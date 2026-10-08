from dataclasses import dataclass
from typing import Optional

@dataclass
class RoutingExperimentResult:
    algorithm_name: str
    dataset_case: str
    runtime_ms: float
    route_length: float
    travel_time: float
    fuel: float
    ice_exposure: float
    iceberg_exposure: float
    tail_hazard: float
    scenario_regret: float
    fallback_availability: bool

class AblationFramework:
    def run_experiment_A(self, case) -> RoutingExperimentResult:
        # A = shortest feasible route
        pass

    def run_experiment_B(self, case) -> RoutingExperimentResult:
        # B = static ice-aware route
        pass

    def run_experiment_C(self, case) -> RoutingExperimentResult:
        # C = time-dependent hazard route
        pass

    def run_experiment_D(self, case) -> RoutingExperimentResult:
        # D = multi-objective Pareto route
        pass

    def run_experiment_E(self, case) -> RoutingExperimentResult:
        # E = uncertainty + hazard futures
        pass

    def run_experiment_F(self, case) -> RoutingExperimentResult:
        # F = uncertainty + hazard futures + fallback/resilience
        pass
