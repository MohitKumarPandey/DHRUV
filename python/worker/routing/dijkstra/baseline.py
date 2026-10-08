import heapq
import h3
import logging
from typing import List, Dict, Optional, Tuple
from ..graph.builder import H3GraphBuilder, haversine_distance

logger = logging.getLogger("DHRUV-Dijkstra")

class DijkstraBaseline:
    def __init__(self, graph: H3GraphBuilder):
        self.graph = graph

    def find_route(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float, speed_knots: float) -> Optional[Dict]:
        start_cell = h3.geo_to_h3(start_lat, start_lon, self.graph.base_resolution)
        end_cell = h3.geo_to_h3(end_lat, end_lon, self.graph.base_resolution)

        if start_cell not in self.graph.cells:
            self.graph.cells.add(start_cell)
        if end_cell not in self.graph.cells:
            self.graph.cells.add(end_cell)

        # Priority queue: (cost, current_node)
        pq = [(0.0, start_cell)]
        
        # Costs and paths
        distances = {start_cell: 0.0}
        came_from = {start_cell: None}

        logger.info(f"Starting Dijkstra search from {start_cell} to {end_cell}")
        nodes_explored = 0

        while pq:
            current_cost, current_node = heapq.heappop(pq)
            nodes_explored += 1

            if current_node == end_cell:
                logger.info(f"Route found. Nodes explored: {nodes_explored}")
                return self._reconstruct_path(came_from, current_node, current_cost, speed_knots)

            if current_cost > distances.get(current_node, float('inf')):
                continue

            for neighbor in self.graph.get_neighbors(current_node):
                # Calculate distance in NM
                lat1, lon1 = h3.h3_to_geo(current_node)
                lat2, lon2 = h3.h3_to_geo(neighbor)
                edge_cost = haversine_distance(lat1, lon1, lat2, lon2)
                
                new_cost = current_cost + edge_cost

                if new_cost < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_cost
                    came_from[neighbor] = current_node
                    heapq.heappush(pq, (new_cost, neighbor))

        logger.warning("No valid route found.")
        return None

    def _reconstruct_path(self, came_from: Dict[str, Optional[str]], current: str, total_dist: float, speed_knots: float) -> Dict:
        path = []
        while current is not None:
            path.append(current)
            current = came_from[current]
        
        path.reverse()
        
        segments = []
        for i in range(len(path) - 1):
            lat1, lon1 = h3.h3_to_geo(path[i])
            lat2, lon2 = h3.h3_to_geo(path[i+1])
            dist = haversine_distance(lat1, lon1, lat2, lon2)
            time = dist / speed_knots if speed_knots > 0 else float('inf')
            
            segments.append({
                "start": {"lat": lat1, "lon": lon1},
                "end": {"lat": lat2, "lon": lon2},
                "distance_nm": dist,
                "time_hours": time,
                "speed_knots": speed_knots,
                "hazard_score": 0.0  # Placeholder, would fetch from environment
            })

        return {
            "route_id": "dijkstra-baseline-01",
            "primary_route": segments,
            "total_time_hours": total_dist / speed_knots if speed_knots > 0 else float('inf'),
            "total_fuel_tons": (total_dist / speed_knots) * 2.5, # Dummy fuel calc
            "risk_exposure": 0.0,
            "status": "SUCCESS",
            "message": "Generated using Dijkstra Baseline"
        }
