"""
DHRUV-MOTUS Weather & Ocean Provider Interfaces

Time-aware environmental data queries for weather and ocean conditions.

CRITICAL: Does NOT silently use wind=0, current=0, wave=0
unless those values genuinely exist in the source data.
Returns explicit UNAVAILABLE state when no data is connected.
"""

import logging
from typing import Optional

from .environment import (
    WeatherData,
    OceanData,
    DataAvailability,
    DataProvenance,
    DataQuality,
)

logger = logging.getLogger("DHRUV-Weather-Ocean")


class WeatherProvider:
    """
    Interface for querying weather conditions at a cell/time.
    
    If unavailable, returns explicit unavailable state.
    Does NOT silently default to wind=0, wave=0.
    """

    def __init__(self, provider=None):
        self.provider = provider
        self._connected = provider is not None

    def get_weather(self, h3_cell: str, valid_time: Optional[str] = None) -> WeatherData:
        if not self._connected:
            return WeatherData(
                availability=DataAvailability.UNAVAILABLE,
                provenance=DataProvenance(
                    source="NONE",
                    quality=DataQuality.UNKNOWN,
                    dataset_id="WEATHER_DATA_UNAVAILABLE",
                ),
            )

        try:
            result = self.provider.query(h3_cell=h3_cell, valid_time=valid_time)
            if result is None:
                return WeatherData(
                    availability=DataAvailability.UNAVAILABLE,
                    provenance=DataProvenance(
                        source=getattr(self.provider, 'source_name', 'UNKNOWN'),
                        quality=DataQuality.UNKNOWN,
                    ),
                )
            return WeatherData(
                availability=DataAvailability.AVAILABLE,
                wind_speed_kts=result.get("wind_speed_kts"),
                wind_direction_deg=result.get("wind_direction_deg"),
                wave_height_m=result.get("wave_height_m"),
                wave_period_s=result.get("wave_period_s"),
                visibility_nm=result.get("visibility_nm"),
                hazard_score=result.get("hazard_score"),
                provenance=DataProvenance(
                    source=result.get("source", getattr(self.provider, 'source_name', 'UNKNOWN')),
                    dataset_id=result.get("dataset_id"),
                    observation_time=result.get("observation_time"),
                    forecast_time=result.get("forecast_time"),
                    valid_time=valid_time,
                    quality=DataQuality.GREEN,
                ),
            )
        except Exception as e:
            logger.error(f"Weather query failed for {h3_cell}: {e}")
            return WeatherData(
                availability=DataAvailability.UNAVAILABLE,
                provenance=DataProvenance(source="ERROR", quality=DataQuality.RED),
            )


class OceanProvider:
    """
    Interface for querying ocean current conditions at a cell/time.
    
    If unavailable, returns explicit unavailable state.
    Does NOT silently default to current=0.
    """

    def __init__(self, provider=None):
        self.provider = provider
        self._connected = provider is not None

    def get_ocean(self, h3_cell: str, valid_time: Optional[str] = None) -> OceanData:
        if not self._connected:
            return OceanData(
                availability=DataAvailability.UNAVAILABLE,
                provenance=DataProvenance(
                    source="NONE",
                    quality=DataQuality.UNKNOWN,
                    dataset_id="OCEAN_DATA_UNAVAILABLE",
                ),
            )

        try:
            result = self.provider.query(h3_cell=h3_cell, valid_time=valid_time)
            if result is None:
                return OceanData(
                    availability=DataAvailability.UNAVAILABLE,
                    provenance=DataProvenance(
                        source=getattr(self.provider, 'source_name', 'UNKNOWN'),
                        quality=DataQuality.UNKNOWN,
                    ),
                )
            return OceanData(
                availability=DataAvailability.AVAILABLE,
                current_speed_kts=result.get("current_speed_kts"),
                current_direction_deg=result.get("current_direction_deg"),
                sst_celsius=result.get("sst_celsius"),
                provenance=DataProvenance(
                    source=result.get("source", getattr(self.provider, 'source_name', 'UNKNOWN')),
                    dataset_id=result.get("dataset_id"),
                    observation_time=result.get("observation_time"),
                    valid_time=valid_time,
                    quality=DataQuality.GREEN,
                ),
            )
        except Exception as e:
            logger.error(f"Ocean query failed for {h3_cell}: {e}")
            return OceanData(
                availability=DataAvailability.UNAVAILABLE,
                provenance=DataProvenance(source="ERROR", quality=DataQuality.RED),
            )
