from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

class DataProvider(ABC):
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
        
    @abstractmethod
    def fetch_data(self, bbox: Dict[str, float], time_range: tuple[datetime, datetime]) -> Optional[Any]:
        """
        Fetches the dataset from the external source, validates it, and returns a normalized model.
        Must return None if data is unavailable.
        """
        pass
