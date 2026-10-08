import h3
import logging
from typing import Set, List, Dict
from math import radians, cos, sin, asin, sqrt

logger = logging.getLogger("DHRUV-H3-Graph")

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in nautical miles between two coordinates."""
    R = 3440.065 # Radius of earth in nautical miles
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = sin(dLat/2) * sin(dLat/2) + cos(radians(lat1)) \
        * cos(radians(lat2)) * sin(dLon/2) * sin(dLon/2)
    c = 2 * asin(sqrt(a))
    return R * c

class H3GraphBuilder:
    def __init__(self, base_resolution: int = 4):
        self.base_resolution = base_resolution
        self.cells: Set[str] = set()

    def build_region(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float):
        """Builds a base graph of H3 cells covering the bounding box."""
        logger.info(f"Building H3 graph for region [{min_lat}, {min_lon}] to [{max_lat}, {max_lon}] at res {self.base_resolution}")
        
        # In a real implementation, we would use h3.polyfill on a GeoJSON polygon representing the bbox
        # For simplicity in this scaffold, we just create a grid
        # h3_polyfill requires a polygon dict
        geo_json = {
            "type": "Polygon",
            "coordinates": [[[min_lon, min_lat], [min_lon, max_lat], [max_lon, max_lat], [max_lon, min_lat], [min_lon, min_lat]]]
        }
        
        # h3 3.7.6 uses geo_json=True to accept (lng, lat) coordinates
        try:
            cells = h3.polyfill(geo_json, self.base_resolution, geo_json_conformant=True)
        except TypeError:
            cells = h3.polyfill(geo_json, self.base_resolution)
            
        self.cells = set(cells)
        logger.info(f"Graph initialized with {len(self.cells)} cells.")

    def get_neighbors(self, cell_id: str) -> List[str]:
        """Returns adjacent navigable cells."""
        try:
            neighbors = h3.k_ring(cell_id, 1)
            # Remove the cell itself
            neighbors.remove(cell_id)
            return [n for n in neighbors if n in self.cells]
        except Exception as e:
            logger.error(f"Failed to get neighbors for {cell_id}: {e}")
            return []
