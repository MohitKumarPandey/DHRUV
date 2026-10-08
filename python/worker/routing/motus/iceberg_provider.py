"""
DHRUV-MOTUS Iceberg Trajectory Provider Interface

Provides iceberg hazard data to the MOTUS environment system.

CRITICAL: Does NOT create fake iceberg trajectories.
If no real dataset is connected, returns ICEBERG_DATA_UNAVAILABLE.
"""

import logging
from typing import Optional, List, Dict, Any

from .environment import (
    IcebergData,
    DataAvailability,
    DataProvenance,
    DataQuality,
)

logger = logging.getLogger("DHRUV-Iceberg-Provider")


class IcebergTrajectoryProvider:
    """
    Interface for querying iceberg trajectory and hazard data.
    
    Supports:
        get_trajectories(spatial_area, time_window) -> trajectory list
        get_hazard(h3_cell, valid_time) -> IcebergData
    
    Output supports:
        iceberg_id, timestamp, lat, lon, trajectory ensemble,
        uncertainty, source, confidence
    
    Until a real dataset is connected, returns ICEBERG_DATA_UNAVAILABLE.
    """

    def __init__(self, provider=None):
        """
        Args:
            provider: Real iceberg data provider instance.
                      If None, all queries return UNAVAILABLE.
        """
        self.provider = provider
        self._connected = provider is not None

    def get_trajectories(
        self,
        spatial_area: Dict[str, float],
        time_window: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Query iceberg trajectories within a spatial area and time window.
        
        Args:
            spatial_area: {"min_lat": ..., "max_lat": ..., "min_lon": ..., "max_lon": ...}
            time_window: {"start": "ISO8601", "end": "ISO8601"}
        
        Returns dict with:
            status: "AVAILABLE" | "UNAVAILABLE"
            trajectories: list of trajectory dicts (if available)
        """
        if not self._connected:
            return {
                "status": "ICEBERG_DATA_UNAVAILABLE",
                "trajectories": [],
                "message": "No real iceberg data source connected.",
            }

        try:
            result = self.provider.query_trajectories(
                spatial_area=spatial_area,
                time_window=time_window,
            )
            return {
                "status": "AVAILABLE",
                "trajectories": result if result else [],
            }
        except Exception as e:
            logger.error(f"Iceberg trajectory query failed: {e}")
            return {
                "status": "ICEBERG_DATA_UNAVAILABLE",
                "trajectories": [],
                "message": f"Query error: {e}",
            }

    def get_hazard(self, h3_cell: str, valid_time: Optional[str] = None) -> IcebergData:
        """
        Query iceberg hazard for a single H3 cell and time.
        
        Returns IcebergData with explicit availability.
        """
        if not self._connected:
            return IcebergData(
                availability=DataAvailability.UNAVAILABLE,
                provenance=DataProvenance(
                    source="NONE",
                    quality=DataQuality.UNKNOWN,
                    dataset_id="ICEBERG_DATA_UNAVAILABLE",
                ),
            )

        try:
            result = self.provider.query_cell(h3_cell=h3_cell, valid_time=valid_time)
            if result is None:
                return IcebergData(
                    availability=DataAvailability.UNAVAILABLE,
                    provenance=DataProvenance(
                        source=getattr(self.provider, 'source_name', 'UNKNOWN'),
                        quality=DataQuality.UNKNOWN,
                    ),
                )
            
            return IcebergData(
                availability=DataAvailability.AVAILABLE,
                probability=result.get("probability"),
                density=result.get("density"),
                provenance=DataProvenance(
                    source=result.get("source", getattr(self.provider, 'source_name', 'UNKNOWN')),
                    dataset_id=result.get("dataset_id"),
                    observation_time=result.get("observation_time"),
                    valid_time=valid_time,
                    quality=DataQuality.GREEN if result.get("probability") is not None else DataQuality.YELLOW,
                ),
            )
        except Exception as e:
            logger.error(f"Iceberg hazard query failed for {h3_cell}: {e}")
            return IcebergData(
                availability=DataAvailability.UNAVAILABLE,
                provenance=DataProvenance(
                    source=getattr(self.provider, 'source_name', 'UNKNOWN'),
                    quality=DataQuality.RED,
                ),
            )
