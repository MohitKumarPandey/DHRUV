from dataclasses import dataclass
from typing import Any, List
import datetime

@dataclass
class HistoricalCase:
    case_id: str
    target_date: datetime.datetime
    description: str

class HistoricalReplayEngine:
    def __init__(self):
        pass

    def load_case(self, case_id: str) -> HistoricalCase:
        pass

    def generate_forecasts(self, case: HistoricalCase, max_data_time: datetime.datetime):
        # Only data available at max_data_time can be used for prediction.
        pass

    def predict_icebergs(self, case: HistoricalCase, max_data_time: datetime.datetime):
        pass

    def generate_routes(self, start_state: Any, end_state: Any):
        pass

    def reveal_future_observations(self, case: HistoricalCase, reveal_time: datetime.datetime) -> Any:
        # Later observations are evaluation targets only.
        pass

    def evaluate_performance(self):
        pass
