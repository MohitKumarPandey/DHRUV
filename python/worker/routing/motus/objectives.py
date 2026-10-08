from dataclasses import dataclass

@dataclass
class MotusObjectiveVector:
    fuel: float
    time: float
    iceberg: float
    safety_uncertainty: float
    
    # Diagnostics
    sea_ice_exposure: float
    weather_exposure: float
    ocean_exposure: float
    distance: float
    recovery_cost: float
