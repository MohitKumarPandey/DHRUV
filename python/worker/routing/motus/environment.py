"""
DHRUV-MOTUS Environment Provider Interface

This module defines the contract for all environmental data providers
used by the MOTUS search algorithm.

CRITICAL DESIGN PRINCIPLE:
- If real data is unavailable, return DataAvailability.UNAVAILABLE
- NEVER substitute 0, "low risk", or fabricated values for missing data
- Missing data ≠ safe conditions
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
import logging

logger = logging.getLogger("DHRUV-Environment")


class DataAvailability(Enum):
    """Indicates whether environmental data is genuinely available."""
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"


class DataQuality(Enum):
    """Quality classification for environmental data."""
    GREEN = "GREEN"      # Full confidence, recent observation
    YELLOW = "YELLOW"    # Moderate confidence or aging data
    ORANGE = "ORANGE"    # Low confidence, significant uncertainty
    RED = "RED"          # Very low confidence or near-missing
    UNKNOWN = "UNKNOWN"  # Cannot assess quality


@dataclass
class DataProvenance:
    """Tracks the origin and freshness of environmental data."""
    source: Optional[str] = None
    dataset_id: Optional[str] = None
    observation_time: Optional[str] = None
    forecast_time: Optional[str] = None
    valid_time: Optional[str] = None
    resolution: Optional[str] = None
    coverage: Optional[str] = None
    quality: DataQuality = DataQuality.UNKNOWN


@dataclass
class SeaIceData:
    """Sea-ice concentration and related fields."""
    availability: DataAvailability = DataAvailability.UNAVAILABLE
    sic: Optional[float] = None           # Sea-ice concentration (0.0 - 1.0)
    thickness: Optional[float] = None     # Ice thickness in meters
    ice_type: Optional[str] = None        # e.g., "first-year", "multi-year"
    provenance: DataProvenance = field(default_factory=DataProvenance)


@dataclass
class IcebergData:
    """Iceberg hazard assessment for a cell/time."""
    availability: DataAvailability = DataAvailability.UNAVAILABLE
    probability: Optional[float] = None   # Probability of iceberg encounter (0.0 - 1.0)
    density: Optional[float] = None       # Icebergs per unit area
    provenance: DataProvenance = field(default_factory=DataProvenance)


@dataclass
class WeatherData:
    """Weather conditions for a cell/time."""
    availability: DataAvailability = DataAvailability.UNAVAILABLE
    wind_speed_kts: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    wave_height_m: Optional[float] = None
    wave_period_s: Optional[float] = None
    visibility_nm: Optional[float] = None
    hazard_score: Optional[float] = None  # Composite weather hazard (0.0 - 1.0)
    provenance: DataProvenance = field(default_factory=DataProvenance)


@dataclass
class OceanData:
    """Ocean current conditions for a cell/time."""
    availability: DataAvailability = DataAvailability.UNAVAILABLE
    current_speed_kts: Optional[float] = None
    current_direction_deg: Optional[float] = None
    sst_celsius: Optional[float] = None
    provenance: DataProvenance = field(default_factory=DataProvenance)


@dataclass
class EnvironmentSnapshot:
    """
    Complete environmental state for a single H3 cell at a specific time.
    
    The algorithm queries this for every candidate transition.
    Fields that are UNAVAILABLE are explicitly marked — never silently zeroed.
    """
    h3_cell: str
    valid_time: Optional[str] = None
    
    sea_ice: SeaIceData = field(default_factory=SeaIceData)
    iceberg: IcebergData = field(default_factory=IcebergData)
    weather: WeatherData = field(default_factory=WeatherData)
    ocean: OceanData = field(default_factory=OceanData)
    
    overall_quality: DataQuality = DataQuality.UNKNOWN
    warnings: List[str] = field(default_factory=list)
    missing_sources: List[str] = field(default_factory=list)

    def compute_overall_quality(self):
        """Derive overall quality from component qualities."""
        qualities = [
            self.sea_ice.provenance.quality,
            self.iceberg.provenance.quality,
            self.weather.provenance.quality,
            self.ocean.provenance.quality,
        ]
        # Worst quality wins
        priority = {
            DataQuality.RED: 0,
            DataQuality.UNKNOWN: 1,
            DataQuality.ORANGE: 2,
            DataQuality.YELLOW: 3,
            DataQuality.GREEN: 4,
        }
        self.overall_quality = min(qualities, key=lambda q: priority.get(q, -1))
        
        # Track missing sources
        self.missing_sources = []
        if self.sea_ice.availability == DataAvailability.UNAVAILABLE:
            self.missing_sources.append("SEA_ICE")
        if self.iceberg.availability == DataAvailability.UNAVAILABLE:
            self.missing_sources.append("ICEBERG")
        if self.weather.availability == DataAvailability.UNAVAILABLE:
            self.missing_sources.append("WEATHER")
        if self.ocean.availability == DataAvailability.UNAVAILABLE:
            self.missing_sources.append("OCEAN")


class EnvironmentProvider:
    """
    Abstract interface for querying environmental conditions.
    
    Implementations must:
    - Return DataAvailability.UNAVAILABLE for missing data
    - NEVER substitute fabricated values
    - Include provenance metadata for every field
    """

    def get_environment(self, h3_cell: str, valid_time: Optional[str] = None) -> EnvironmentSnapshot:
        """
        Query all environmental data for a given H3 cell and time.
        
        Returns an EnvironmentSnapshot with explicit availability status
        for each data source.
        """
        raise NotImplementedError("Subclasses must implement get_environment")


class UnavailableEnvironmentProvider(EnvironmentProvider):
    """
    Default provider that honestly reports all data as UNAVAILABLE.
    
    Used when no real data sources are connected.
    This is the honest starting point — not a fake provider.
    """

    def get_environment(self, h3_cell: str, valid_time: Optional[str] = None) -> EnvironmentSnapshot:
        snapshot = EnvironmentSnapshot(h3_cell=h3_cell, valid_time=valid_time)
        
        snapshot.sea_ice = SeaIceData(
            availability=DataAvailability.UNAVAILABLE,
            provenance=DataProvenance(source="NONE", quality=DataQuality.UNKNOWN)
        )
        snapshot.iceberg = IcebergData(
            availability=DataAvailability.UNAVAILABLE,
            provenance=DataProvenance(source="NONE", quality=DataQuality.UNKNOWN)
        )
        snapshot.weather = WeatherData(
            availability=DataAvailability.UNAVAILABLE,
            provenance=DataProvenance(source="NONE", quality=DataQuality.UNKNOWN)
        )
        snapshot.ocean = OceanData(
            availability=DataAvailability.UNAVAILABLE,
            provenance=DataProvenance(source="NONE", quality=DataQuality.UNKNOWN)
        )
        
        snapshot.warnings = [
            "ALL_DATA_UNAVAILABLE: No real environmental data sources connected.",
            "Route computed without environmental hazard assessment.",
        ]
        snapshot.missing_sources = ["SEA_ICE", "ICEBERG", "WEATHER", "OCEAN"]
        snapshot.overall_quality = DataQuality.UNKNOWN
        
        return snapshot
