from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class RoutingState:
    """
    Immutable representation of the node + time + current operating state.
    """
    node_id: str
    latitude: float
    longitude: float
    arrival_time: float # Abstracted as hours from departure for simplicity, or timestamp
    speed_mode: str
    current_speed: float
    accumulated_distance: float
    accumulated_time: float
    accumulated_fuel: float
    accumulated_sea_ice_exposure: float
    accumulated_iceberg_exposure: float
    accumulated_safety_uncertainty: float
    accumulated_recovery_cost: float
    parent_label_id: Optional[str]
    
    def __eq__(self, dict_or_obj):
        if not isinstance(dict_or_obj, RoutingState):
            return False
        return self.node_id == dict_or_obj.node_id and self.arrival_time == dict_or_obj.arrival_time
    
    def __hash__(self):
        return hash((self.node_id, self.arrival_time, self.speed_mode))
