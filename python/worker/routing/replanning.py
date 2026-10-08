from dataclasses import dataclass
from typing import Any, Optional, Dict

@dataclass
class ReplanningTriggersConfig:
    hazard_envelope_intersection_threshold: float
    sea_ice_exceedance_threshold: float
    uncertainty_expansion_threshold: float
    forecast_change_threshold: float
    stale_data_timeout_hours: float
    weather_exceedance_threshold: float

@dataclass
class ReplanComparison:
    old_eta: str
    new_eta: str
    old_fuel: float
    new_fuel: float
    old_hazard: float
    new_hazard: float
    route_change_distance: float
    replan_reason: str
    trigger: str
    environment_change: str
    forecast_change: str
    hazard_change: str
    route_cost_difference: float

class DynamicReplanningEngine:
    def __init__(self, config: ReplanningTriggersConfig):
        self.config = config

    def check_route_health(self, current_vessel_state: Any, latest_environment: Any, 
                           latest_forecast: Any, latest_iceberg_observations: Any, 
                           current_route: Any, fallback_corridor: Any) -> Optional[str]:
        # Evaluate triggers based on configurable thresholds
        # DO NOT hardcode arbitrary scientific percentages.
        
        # Mock logic
        trigger = "uncertainty materially expands"
        # Return trigger reason if replan is needed, else None
        return trigger

    def replan(self, current_vessel_state: Any, trigger: str, previous_route: Any) -> ReplanComparison:
        # Replan from the CURRENT vessel state.
        # Completed route prefix must remain immutable.
        
        return ReplanComparison(
            old_eta="2026-10-06T12:00:00Z",
            new_eta="2026-10-06T14:30:00Z",
            old_fuel=100.0,
            new_fuel=115.0,
            old_hazard=0.1,
            new_hazard=0.05,
            route_change_distance=25.5,
            replan_reason="Ensuring safety margin",
            trigger=trigger,
            environment_change="Iceberg entered hazard envelope",
            forecast_change="None",
            hazard_change="-0.05",
            route_cost_difference=15.0
        )
