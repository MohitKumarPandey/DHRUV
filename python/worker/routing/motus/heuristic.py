"""
DHRUV-MOTUS Heuristic Functions (A* Guidance)

TASK 17: Verified heuristic implementation.

For time: h_time = remaining_distance / maximum_feasible_speed
For fuel: h_fuel = remaining_time * minimum_fuel_rate (optimistic lower bound)

A* heuristic is search GUIDANCE only.
Pareto dominance remains the multi-objective decision mechanism.
The heuristic is NOT used to collapse objectives into a single weighted score.
"""

from ..graph.builder import haversine_distance
import h3


def calculate_h_time(current_node: str, end_node: str, max_speed: float) -> float:
    """
    Admissible heuristic: minimum possible travel time from current to destination.
    
    h_time = straight-line distance / maximum feasible speed
    
    This is optimistic (admissible) because the actual path can only be longer.
    """
    if max_speed <= 0:
        return 0.0
    lat1, lon1 = h3.h3_to_geo(current_node)
    lat2, lon2 = h3.h3_to_geo(end_node)
    dist = haversine_distance(lat1, lon1, lat2, lon2)
    return dist / max_speed


def calculate_h_fuel(current_node: str, end_node: str, min_fuel_rate: float, max_speed: float) -> float:
    """
    Admissible heuristic: minimum possible fuel consumption from current to destination.
    
    h_fuel = minimum_time * minimum_fuel_rate
    
    This is a documented optimistic lower bound:
    - We assume the fastest path (minimum time)
    - At the lowest fuel consumption rate
    - Real fuel will always be >= this
    """
    time = calculate_h_time(current_node, end_node, max_speed)
    return time * min_fuel_rate


def calculate_composite_heuristic(
    current_node: str,
    end_node: str,
    vessel_profile: dict,
    weight: float = 1.0,
) -> float:
    """
    Composite A* guidance heuristic.
    
    Uses time as the primary guidance signal, weighted by config.
    Does NOT combine objectives into a weighted score for dominance —
    this is purely search ordering.
    """
    max_speed = vessel_profile.get("max_speed", 12.0)
    h_t = calculate_h_time(current_node, end_node, max_speed)
    return h_t * weight
