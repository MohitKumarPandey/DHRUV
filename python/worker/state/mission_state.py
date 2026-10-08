from dataclasses import dataclass
from typing import Any, List, Optional
import datetime

@dataclass
class MissionState:
    mission_id: str
    case_id: str
    vessel: Any
    origin: Any
    destination: Any
    departure_time: datetime.datetime
    current_position: Any
    current_time: datetime.datetime
    current_route: Any
    alternative_routes: List[Any]
    forecast_version: str
    hazard_future_version: str
    fallback_status: str
    data_quality: str
    route_status: str
    replanning_status: str
    last_replan: Optional[datetime.datetime]
    decision_policy: str
