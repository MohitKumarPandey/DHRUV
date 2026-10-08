import os
import requests
import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
import hashlib

class DataQuality(Enum):
    GREEN = "GREEN"      # High confidence, recent, validated
    YELLOW = "YELLOW"    # Moderate confidence, slightly stale or interpolated
    ORANGE = "ORANGE"    # Low confidence, degraded or highly extrapolated
    RED = "RED"          # Invalid, missing, or extremely stale

class ProviderEnum(Enum):
    NSIDC = "NSIDC"
    COPERNICUS = "COPERNICUS"
    ECMWF = "ECMWF"
    NCEP = "NCEP"
    HYCOM = "HYCOM"
    NIC = "NIC"

@dataclass
class ScientificRecord:
    provider: ProviderEnum
    product_name: str
    observation_time: datetime.datetime
    processing_time: datetime.datetime
    spatial_resolution: str
    geographic_coverage: str
    quality_state: DataQuality
    product_version: str
    retrieval_timestamp: datetime.datetime
    file_path: Optional[str] = None
    forecast_initialization_time: Optional[datetime.datetime] = None
    forecast_valid_time: Optional[datetime.datetime] = None

class DataProviderInterface:
    def fetch_data(self, start_time: datetime.datetime, end_time: datetime.datetime, bbox: Dict[str, float]) -> List[ScientificRecord]:
        raise NotImplementedError

class CacheManager:
    def __init__(self, cache_dir="/tmp/dhruv_cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def get_cache_path(self, url: str) -> str:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, url_hash)

class NSIDCProvider(DataProviderInterface):
    """NSIDC Sea-Ice Concentration."""
    def __init__(self):
        self.cache = CacheManager()
        self.base_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
        self.dataset_id = "NSIDC-0051"

    def fetch_data(self, start_time, end_time, bbox) -> List[ScientificRecord]:
        records = []
        try:
            # Query actual CMR API for NSIDC-0051
            search_url = f"{self.base_url}?short_name={self.dataset_id}&temporal={start_time.isoformat()}Z,{end_time.isoformat()}Z"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                granules = data.get('feed', {}).get('entry', [])
                
                # Check for authentication requirement (Earthdata login)
                earthdata_user = os.environ.get("EARTHDATA_USERNAME")
                earthdata_pass = os.environ.get("EARTHDATA_PASSWORD")
                
                for granule in granules[:5]:
                    title = granule.get('title', 'Unknown NSIDC Product')
                    download_url = None
                    for link in granule.get('links', []):
                        if link.get('href', '').endswith('.nc'):
                            download_url = link.get('href')
                            break
                            
                    record = ScientificRecord(
                        provider=ProviderEnum.NSIDC,
                        product_name=title,
                        observation_time=start_time, # Should ideally be parsed from granule metadata
                        processing_time=datetime.datetime.now(datetime.timezone.utc),
                        spatial_resolution="25km",
                        geographic_coverage="Polar",
                        quality_state=DataQuality.YELLOW,
                        product_version="2.0",
                        retrieval_timestamp=datetime.datetime.now(datetime.timezone.utc),
                        file_path=download_url # Store URL here until downloaded
                    )
                    records.append(record)
                    
                if not earthdata_user:
                    print("NSIDC_REAL_DATA = BLOCKED (Missing EARTHDATA_USERNAME)")
            else:
                raise Exception(f"NSIDC API Error: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"NSIDC Data retrieval failed: {e}")
            raise Exception("External data failure: NSIDC unreachable")
            
        return records

class CopernicusProvider(DataProviderInterface):
    """Copernicus Sentinel-1 SAR (Copernicus Data Space Ecosystem)."""
    def __init__(self):
        self.cache = CacheManager()
        self.auth_token = os.environ.get("COPERNICUS_TOKEN")
        self.base_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

    def fetch_data(self, start_time, end_time, bbox) -> List[ScientificRecord]:
        records = []
        try:
            # Copernicus Data Space OData API for Sentinel-1
            search_url = f"{self.base_url}?$filter=Collection/Name eq 'SENTINEL-1' and ContentDate/Start ge {start_time.isoformat()}Z and ContentDate/Start le {end_time.isoformat()}Z&$top=5"
            response = requests.get(search_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                for product in data.get('value', []):
                    product_id = product.get('Id')
                    download_url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
                    
                    record = ScientificRecord(
                        provider=ProviderEnum.COPERNICUS,
                        product_name=product.get('Name', 'Sentinel-1'),
                        observation_time=datetime.datetime.fromisoformat(product.get('ContentDate', {}).get('Start', start_time.isoformat()).rstrip('Z')),
                        processing_time=datetime.datetime.now(datetime.timezone.utc),
                        spatial_resolution="10m",
                        geographic_coverage="Antarctic filter required",
                        quality_state=DataQuality.YELLOW,
                        product_version="Level-1",
                        retrieval_timestamp=datetime.datetime.now(datetime.timezone.utc),
                        file_path=download_url
                    )
                    records.append(record)
                    
                if not self.auth_token:
                    print("COPERNICUS_RUNTIME = BLOCKED (Missing COPERNICUS_TOKEN in environment)")
            else:
                raise Exception(f"Copernicus API Error: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"Copernicus Data retrieval failed: {e}")
            raise Exception("External data failure: Copernicus unreachable")
            
        return records

class MeteorologicalProvider(DataProviderInterface):
    """Validated meteorological data (e.g., ECMWF/NCEP)."""
    def fetch_data(self, start_time, end_time, bbox):
        return []

class OceanProvider(DataProviderInterface):
    """Validated ocean/current data."""
    def fetch_data(self, start_time, end_time, bbox):
        return []

class IcebergObservationProvider(DataProviderInterface):
    """Iceberg observations/detections."""
    def fetch_data(self, start_time, end_time, bbox):
        return []
