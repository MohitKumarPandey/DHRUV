from dataclasses import dataclass
from typing import Optional, List

from .config import WaitingConfig


@dataclass(frozen=True)
class RoutingAction:
    """
    Represents a speed/power/wait action the vessel can take.
    
    action_type: "SLOW", "CRUISE", "FAST", "WAIT"
    speed: effective speed in knots (0 for WAIT)
    duration: hours (used for WAIT actions)
    fuel_cost_per_hour: fuel consumption rate at this speed
    """
    action_type: str
    speed: float
    duration: float
    fuel_cost_per_hour: float


def get_legal_actions(
    state,
    vessel_profile: dict,
    waiting_config: WaitingConfig = None,
) -> List[RoutingAction]:
    """
    Returns legal actions for the current state based on vessel capabilities.
    
    Speed actions are always available if the vessel profile defines them.
    WAIT action is conditionally available based on config and accumulated wait time.
    """
    actions = []

    min_speed = vessel_profile.get("min_speed", 0)
    cruise_speed = vessel_profile.get("cruise_speed", 0)
    max_speed = vessel_profile.get("max_speed", 0)

    # Fuel rates: lower speeds are more efficient
    min_fuel = vessel_profile.get("min_fuel_rate", 1.5)
    cruise_fuel = vessel_profile.get("cruise_fuel_rate", 2.5)
    max_fuel = vessel_profile.get("max_fuel_rate", 4.0)

    if min_speed > 0:
        actions.append(RoutingAction("SLOW", min_speed, 0, min_fuel))
    if cruise_speed > 0:
        actions.append(RoutingAction("CRUISE", cruise_speed, 0, cruise_fuel))
    if max_speed > 0:
        actions.append(RoutingAction("FAST", max_speed, 0, max_fuel))

    # WAIT action: stay at current node, consume idle fuel, let conditions change
    if waiting_config and waiting_config.enabled:
        idle_fuel = vessel_profile.get("idle_fuel_rate", 0.5)
        actions.append(RoutingAction(
            "WAIT",
            0.0,
            waiting_config.wait_interval_hours,
            idle_fuel,
        ))

    return actions
