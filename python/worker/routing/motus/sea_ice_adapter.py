"""
DHRUV-MOTUS Sea-Ice Environment Adapter

Converts real sea-ice provider output into the MOTUS environment contract.

CRITICAL: Does NOT fabricate data. If the underlying provider has not
loaded a real dataset, returns UNAVAILABLE with proper metadata.
"""

import logging
from typing import Optional

from .environment import (
    SeaIceData,
    DataAvailability,
    DataProvenance,
    DataQuality,
)

logger = logging.getLogger("DHRUV-SeaIce-Adapter")


class SeaIceEnvironmentAdapter:
    """
    Adapter that converts real NSIDC/other sea-ice provider output
    into the MOTUS EnvironmentSnapshot.sea_ice contract.
    
    Required metadata when data IS available:
      source, observation_time, valid_time, resolution, coverage,
      quality, dataset/product identifier
    
    If data is unavailable: returns SeaIceData with UNAVAILABLE status.
    Does NOT substitute SIC = 0.
    """

    def __init__(self, provider=None):
        """
        Args:
            provider: Real sea-ice data provider instance (e.g., NSIDCSeaIceProvider).
                      If None, all queries return UNAVAILABLE.
        """
        self.provider = provider
        self._connected = provider is not None

    def get_sea_ice(self, h3_cell: str, valid_time: Optional[str] = None) -> SeaIceData:
        """
        Query sea-ice conditions for a given H3 cell and time.
        
        Returns SeaIceData with explicit availability status.
        """
        if not self._connected:
            return SeaIceData(
                availability=DataAvailability.UNAVAILABLE,
                provenance=DataProvenance(
                    source="NONE",
                    quality=DataQuality.UNKNOWN,
                    dataset_id="NOT_CONNECTED",
                ),
            )

        try:
            # Query the real provider
            # The actual API depends on the provider implementation
            result = self.provider.query(h3_cell=h3_cell, valid_time=valid_time)
            
            if result is None:
                return SeaIceData(
                    availability=DataAvailability.UNAVAILABLE,
                    provenance=DataProvenance(
                        source=getattr(self.provider, 'source_name', 'UNKNOWN'),
                        quality=DataQuality.UNKNOWN,
                    ),
                )

            return SeaIceData(
                availability=DataAvailability.AVAILABLE,
                sic=result.get("sic"),
                thickness=result.get("thickness"),
                ice_type=result.get("ice_type"),
                provenance=DataProvenance(
                    source=result.get("source", getattr(self.provider, 'source_name', 'UNKNOWN')),
                    dataset_id=result.get("dataset_id"),
                    observation_time=result.get("observation_time"),
                    forecast_time=result.get("forecast_time"),
                    valid_time=valid_time,
                    resolution=result.get("resolution"),
                    coverage=result.get("coverage"),
                    quality=DataQuality.GREEN if result.get("sic") is not None else DataQuality.YELLOW,
                ),
            )
        except Exception as e:
            logger.error(f"Sea-ice query failed for {h3_cell} at {valid_time}: {e}")
            return SeaIceData(
                availability=DataAvailability.UNAVAILABLE,
                provenance=DataProvenance(
                    source=getattr(self.provider, 'source_name', 'UNKNOWN'),
                    quality=DataQuality.RED,
                ),
            )
