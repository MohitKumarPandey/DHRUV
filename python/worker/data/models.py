from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class DataProvenance(BaseModel):
    provider: str
    dataset_name: str
    source_url: str
    acquisition_timestamp: datetime
    quality_state: str = Field(default="UNKNOWN")
    checksum: Optional[str] = None

class SeaIceField(BaseModel):
    timestamp: datetime
    valid_time: datetime
    bbox: Dict[str, float]
    crs: str
    resolution: float
    # In a real scenario, this would be a reference to an Xarray Dataset or a numpy array
    # stored locally or on object storage. We store the path here.
    data_uri: str 
    source: str
    provenance: DataProvenance
