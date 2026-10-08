from dataclasses import dataclass
from typing import List, Any, Optional

@dataclass
class FallbackTransition:
    checkpoint_location: Any
    corridor_geometry: Any
    transition_distance: float
    transition_time: float
    transition_fuel: float
    sea_ice_exposure: float
    iceberg_exposure: float
    weather_ocean_exposure: float
    uncertainty: float
    scenario_robustness: float
    is_available: bool
    unavailable_reason: Optional[str]

class FallbackCorridorEvaluator:
    def evaluate_checkpoints(self, primary_route: Any, hazard_scenarios: List[Any], vessel_constraints: dict) -> List[FallbackTransition]:
        transitions = []
        
        # Mocking checkpoint iteration and search
        # A fallback corridor must exist in backend state before being shown.
        transitions.append(FallbackTransition(
            checkpoint_location={"lat": -70.0, "lon": 10.0},
            corridor_geometry={"type": "LineString", "coordinates": [[10.0, -70.0], [11.0, -69.0]]},
            transition_distance=50.0,
            transition_time=5.0,
            transition_fuel=20.0,
            sea_ice_exposure=0.02,
            iceberg_exposure=0.01,
            weather_ocean_exposure=0.03,
            uncertainty=0.1,
            scenario_robustness=0.95,
            is_available=True,
            unavailable_reason=None
        ))
        
        # Unavailable mock
        transitions.append(FallbackTransition(
            checkpoint_location={"lat": -72.0, "lon": 15.0},
            corridor_geometry=None,
            transition_distance=0.0,
            transition_time=0.0,
            transition_fuel=0.0,
            sea_ice_exposure=1.0,
            iceberg_exposure=0.0,
            weather_ocean_exposure=0.0,
            uncertainty=0.0,
            scenario_robustness=0.0,
            is_available=False,
            unavailable_reason="Sea-ice conditions exceed vessel operational envelope"
        ))
        
        return transitions
