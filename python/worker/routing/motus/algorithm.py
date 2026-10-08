"""
DHRUV-MOTUS: Multi-Objective Time-Uncertain Search Algorithm

Complete implementation with all 11 architecture stages instrumented:
  1. Node + Time + Current State
  2. Speed / Power / Wait actions
  3. Arrival Time Update
  4. Future Environment Query
  5. 4-objective Evaluation (fuel, time, iceberg, safety_uncertainty)
  6. Hard Safety Gates
  7. Pareto Dominance
  8. ε-Dominance
  9. Label Cap
  10. A*-Guided Search
  11. Non-Dominated Route Extraction

CRITICAL:
- Uses real EnvironmentProvider (defaults to UnavailableEnvironmentProvider)
- Uses externalized MotusConfig (no hardcoded epsilon/caps)
- Reconstructs actual routes from label chains
- Reports honest execution metrics
"""

import logging
import time
import heapq
import uuid
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import h3

from .state import RoutingState
from .actions import get_legal_actions
from .objectives import MotusObjectiveVector
from .safety_gates import evaluate_hard_safety_gates
from .pareto import ParetoLabel, ParetoMetrics, filter_non_dominated, apply_label_cap
from .heuristic import calculate_h_time, calculate_h_fuel, calculate_composite_heuristic
from .config import MotusConfig
from .environment import (
    EnvironmentProvider,
    UnavailableEnvironmentProvider,
    EnvironmentSnapshot,
    DataAvailability,
    DataQuality,
)
from ..graph.builder import H3GraphBuilder, haversine_distance

logger = logging.getLogger("DHRUV-MOTUS")


@dataclass
class SearchMetrics:
    """Execution metrics for a single MOTUS search run."""
    runtime_ms: float = 0.0
    nodes_expanded: int = 0
    labels_created: int = 0
    labels_pruned: int = 0
    epsilon_pruned: int = 0
    cap_pruned: int = 0
    hard_gate_rejections: int = 0
    destination_labels_found: int = 0
    pareto_routes_returned: int = 0
    search_terminated_reason: str = ""
    data_quality: str = "UNKNOWN"
    warnings: List[str] = field(default_factory=list)
    missing_data_sources: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "runtime_ms": self.runtime_ms,
            "nodes_expanded": self.nodes_expanded,
            "labels_created": self.labels_created,
            "labels_pruned": self.labels_pruned,
            "epsilon_pruned": self.epsilon_pruned,
            "cap_pruned": self.cap_pruned,
            "hard_gate_rejections": self.hard_gate_rejections,
            "destination_labels_found": self.destination_labels_found,
            "pareto_routes_returned": self.pareto_routes_returned,
            "search_terminated_reason": self.search_terminated_reason,
            "data_quality": self.data_quality,
            "warnings": self.warnings,
            "missing_data_sources": self.missing_data_sources,
        }


@dataclass
class RouteSegmentData:
    """A single segment in a reconstructed route."""
    segment_id: str
    from_cell: str
    to_cell: str
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    departure_time: float
    arrival_time: float
    duration_hours: float
    speed_knots: float
    speed_mode: str
    distance_nm: float
    fuel_tons: float
    sea_ice_exposure: float
    iceberg_exposure: float
    safety_uncertainty: float
    data_quality: str


@dataclass
class ReconstructedRoute:
    """A complete route from origin to destination, reconstructed from labels."""
    route_id: str
    segments: List[RouteSegmentData]
    total_distance_nm: float
    total_time_hours: float
    total_fuel_tons: float
    sea_ice_exposure: float
    iceberg_exposure: float
    safety_uncertainty: float
    objective_vector: MotusObjectiveVector
    data_quality: str
    explanation: str
    fallback_status: str = "NONE"


class MotusAlgorithm:
    """
    DHRUV-MOTUS: Multi-Objective Time-Uncertain Search
    
    Uses the existing H3GraphBuilder infrastructure.
    Does NOT create a second graph implementation.
    """

    def __init__(
        self,
        graph: H3GraphBuilder,
        config: MotusConfig = None,
        environment_provider: EnvironmentProvider = None,
    ):
        self.graph = graph
        self.config = config or MotusConfig()
        self.environment = environment_provider or UnavailableEnvironmentProvider()

        # Validate config
        warnings = self.config.validate()
        for w in warnings:
            logger.warning(f"Config validation: {w}")

    def search(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        vessel_profile: Dict,
        departure_time: str = None,
    ) -> tuple:
        """
        Execute MOTUS multi-objective A* search.
        
        Returns:
            (pareto_labels: List[ParetoLabel], metrics: SearchMetrics)
        """
        start_time = time.time()
        metrics = SearchMetrics()
        pareto_metrics = ParetoMetrics()

        # --- STAGE 1: Node + Time + Current State ---
        logger.info("STAGE 1: Initializing search state")
        start_cell = h3.geo_to_h3(start_lat, start_lon, self.graph.base_resolution)
        end_cell = h3.geo_to_h3(end_lat, end_lon, self.graph.base_resolution)

        # Ensure start/end are in the graph
        if start_cell not in self.graph.cells:
            self.graph.cells.add(start_cell)
        if end_cell not in self.graph.cells:
            self.graph.cells.add(end_cell)

        initial_state = RoutingState(
            node_id=start_cell,
            latitude=start_lat,
            longitude=start_lon,
            arrival_time=0.0,
            speed_mode="IDLE",
            current_speed=0.0,
            accumulated_distance=0.0,
            accumulated_time=0.0,
            accumulated_fuel=0.0,
            accumulated_sea_ice_exposure=0.0,
            accumulated_iceberg_exposure=0.0,
            accumulated_safety_uncertainty=0.0,
            accumulated_recovery_cost=0.0,
            parent_label_id=None,
        )

        initial_obj = MotusObjectiveVector(
            fuel=0.0, time=0.0, iceberg=0.0, safety_uncertainty=0.0,
            sea_ice_exposure=0.0, weather_exposure=0.0, ocean_exposure=0.0,
            distance=0.0, recovery_cost=0.0,
        )

        initial_label = ParetoLabel(
            state=initial_state,
            objective_vector=initial_obj,
            heuristic_value=0.0,
            parent_label=None,
        )
        metrics.labels_created += 1
        pareto_metrics.labels_created += 1

        # --- STAGE 10: A*-Guided Search initialization ---
        logger.info("STAGE 10: Initializing A* priority queue")
        open_set = []
        heapq.heappush(open_set, (0.0, initial_label.label_id, initial_label))

        # State-level label storage for dominance
        state_labels: Dict[str, List[ParetoLabel]] = {start_cell: [initial_label]}

        destination_labels: List[ParetoLabel] = []
        environment_quality_seen = set()
        all_warnings = set()
        all_missing_sources = set()

        epsilon = self.config.epsilon.to_dict()
        max_labels = self.config.max_labels_per_state
        max_nodes = self.config.max_search_nodes

        while open_set:
            # Check search limit
            if metrics.nodes_expanded >= max_nodes:
                metrics.search_terminated_reason = f"MAX_SEARCH_NODES_REACHED ({max_nodes})"
                logger.warning(metrics.search_terminated_reason)
                break

            current_priority, _, current_label = heapq.heappop(open_set)

            metrics.nodes_expanded += 1
            if metrics.nodes_expanded % 200 == 0:
                logger.info(
                    f"MOTUS: expanded {metrics.nodes_expanded} nodes, "
                    f"queue={len(open_set)}, destinations={len(destination_labels)}"
                )

            # --- STAGE 11: Destination check ---
            if current_label.state.node_id == end_cell:
                destination_labels.append(current_label)
                metrics.destination_labels_found += 1
                logger.info(f"STAGE 11: Destination label found (#{len(destination_labels)})")
                # Continue searching for other Pareto-optimal paths
                if len(destination_labels) >= self.config.max_route_candidates:
                    metrics.search_terminated_reason = "MAX_ROUTE_CANDIDATES_REACHED"
                    break
                continue

            # --- STAGE 2: Speed / Power / Wait actions ---
            neighbors = self.graph.get_neighbors(current_label.state.node_id)
            actions = get_legal_actions(
                current_label.state,
                vessel_profile,
                self.config.waiting,
            )

            for neighbor in neighbors:
                for action in actions:
                    # --- STAGE 3: Arrival Time Update ---
                    lat1, lon1 = h3.h3_to_geo(current_label.state.node_id)
                    lat2, lon2 = h3.h3_to_geo(neighbor)

                    if action.action_type == "WAIT":
                        # WAIT: stay at current node for action.duration hours
                        dist = 0.0
                        travel_time = action.duration
                        # For WAIT, the "neighbor" should be self
                        if neighbor != current_label.state.node_id:
                            continue  # WAIT only applies to current cell
                    else:
                        dist = haversine_distance(lat1, lon1, lat2, lon2)
                        travel_time = dist / action.speed if action.speed > 0 else float('inf')

                    if travel_time == float('inf'):
                        continue

                    arrival_time = current_label.state.arrival_time + travel_time

                    # --- STAGE 4: Future Environment Query ---
                    env_snapshot = self.environment.get_environment(neighbor, str(arrival_time))

                    # Track data quality
                    env_snapshot.compute_overall_quality()
                    environment_quality_seen.add(env_snapshot.overall_quality.value)
                    for w in env_snapshot.warnings:
                        all_warnings.add(w)
                    for ms in env_snapshot.missing_sources:
                        all_missing_sources.add(ms)

                    # Extract values — using None-safe access
                    sic_value = env_snapshot.sea_ice.sic if env_snapshot.sea_ice.sic is not None else 0.0
                    iceberg_value = env_snapshot.iceberg.probability if env_snapshot.iceberg.probability is not None else 0.0
                    weather_hazard = env_snapshot.weather.hazard_score if env_snapshot.weather.hazard_score is not None else 0.0

                    # --- STAGE 6: Hard Safety Gates (BEFORE Pareto insertion) ---
                    transition = {"is_land": False}
                    safety_report = evaluate_hard_safety_gates(
                        transition, env_snapshot, vessel_profile, self.config.data_policy,
                    )

                    if not safety_report.feasible:
                        metrics.hard_gate_rejections += safety_report.hard_gate_rejections
                        continue

                    for dw in safety_report.data_warnings:
                        all_warnings.add(dw)

                    # --- STAGE 5: 4-objective Evaluation ---
                    # Safety uncertainty increases when data is unavailable
                    env_uncertainty = 0.0
                    if env_snapshot.sea_ice.availability == DataAvailability.UNAVAILABLE:
                        env_uncertainty += 0.25  # Penalty for unknown sea-ice
                    if env_snapshot.iceberg.availability == DataAvailability.UNAVAILABLE:
                        env_uncertainty += 0.25
                    if env_snapshot.weather.availability == DataAvailability.UNAVAILABLE:
                        env_uncertainty += 0.25
                    if env_snapshot.ocean.availability == DataAvailability.UNAVAILABLE:
                        env_uncertainty += 0.25

                    # --- STAGE 1 (continued): New State ---
                    new_state = RoutingState(
                        node_id=neighbor,
                        latitude=lat2,
                        longitude=lon2,
                        arrival_time=arrival_time,
                        speed_mode=action.action_type,
                        current_speed=action.speed,
                        accumulated_distance=current_label.state.accumulated_distance + dist,
                        accumulated_time=arrival_time,
                        accumulated_fuel=current_label.state.accumulated_fuel + (action.fuel_cost_per_hour * travel_time),
                        accumulated_sea_ice_exposure=current_label.state.accumulated_sea_ice_exposure + sic_value,
                        accumulated_iceberg_exposure=current_label.state.accumulated_iceberg_exposure + iceberg_value,
                        accumulated_safety_uncertainty=current_label.state.accumulated_safety_uncertainty + env_uncertainty,
                        accumulated_recovery_cost=0.0,
                        parent_label_id=current_label.label_id,
                    )

                    new_obj = MotusObjectiveVector(
                        fuel=new_state.accumulated_fuel,
                        time=new_state.accumulated_time,
                        iceberg=new_state.accumulated_iceberg_exposure,
                        safety_uncertainty=new_state.accumulated_safety_uncertainty,
                        sea_ice_exposure=new_state.accumulated_sea_ice_exposure,
                        weather_exposure=weather_hazard,
                        ocean_exposure=0.0,
                        distance=new_state.accumulated_distance,
                        recovery_cost=0.0,
                    )

                    new_label = ParetoLabel(
                        state=new_state,
                        objective_vector=new_obj,
                        parent_label=current_label,
                    )
                    metrics.labels_created += 1
                    pareto_metrics.labels_created += 1

                    # --- STAGE 7 + 8: Pareto Dominance + ε-Dominance ---
                    node_key = neighbor
                    existing_labels = state_labels.get(node_key, [])
                    existing_labels.append(new_label)

                    pruned_labels = filter_non_dominated(
                        existing_labels, epsilon=epsilon, metrics=pareto_metrics,
                    )

                    # --- STAGE 9: Label Cap ---
                    capped_labels = apply_label_cap(
                        pruned_labels, max_labels, metrics=pareto_metrics,
                    )

                    state_labels[node_key] = capped_labels

                    # --- STAGE 10: A*-Guided Search (push to OPEN if survived) ---
                    if new_label in capped_labels:
                        if self.config.heuristic.enabled:
                            h_val = calculate_composite_heuristic(
                                neighbor, end_cell, vessel_profile,
                                weight=self.config.heuristic.weight,
                            )
                            new_label.heuristic_value = new_obj.time + h_val
                        else:
                            new_label.heuristic_value = new_obj.time

                        heapq.heappush(open_set, (
                            new_label.heuristic_value,
                            new_label.label_id,
                            new_label,
                        ))

        # --- STAGE 11: Non-Dominated Route Extraction ---
        if not metrics.search_terminated_reason:
            metrics.search_terminated_reason = "SEARCH_EXHAUSTED"

        logger.info(
            f"STAGE 11: Search complete. Expanded {metrics.nodes_expanded} nodes. "
            f"Found {len(destination_labels)} destination labels."
        )

        # Final global Pareto filter on destination labels
        final_pareto_front = filter_non_dominated(destination_labels, metrics=pareto_metrics)
        metrics.pareto_routes_returned = len(final_pareto_front)
        metrics.labels_pruned = pareto_metrics.total_pruned
        metrics.epsilon_pruned = pareto_metrics.epsilon_pruned
        metrics.cap_pruned = pareto_metrics.cap_pruned

        # Aggregate data quality
        if "GREEN" in environment_quality_seen and len(environment_quality_seen) == 1:
            metrics.data_quality = "GREEN"
        elif "RED" in environment_quality_seen or "UNKNOWN" in environment_quality_seen:
            metrics.data_quality = "RED"
        elif "ORANGE" in environment_quality_seen:
            metrics.data_quality = "ORANGE"
        elif "YELLOW" in environment_quality_seen:
            metrics.data_quality = "YELLOW"
        else:
            metrics.data_quality = "UNKNOWN"

        metrics.warnings = list(all_warnings)
        metrics.missing_data_sources = list(all_missing_sources)
        metrics.runtime_ms = (time.time() - start_time) * 1000.0

        logger.info(
            f"Filtered to {len(final_pareto_front)} global Pareto optimal routes. "
            f"Runtime: {metrics.runtime_ms:.1f}ms"
        )

        return final_pareto_front, metrics

    def reconstruct_route(self, label: ParetoLabel) -> ReconstructedRoute:
        """
        TASK 3: Proper route reconstruction from label chain.
        
        Walks the parent_label chain back to origin, then reverses
        to produce: origin → H3 cell sequence → timestamps → speed/action → destination
        
        Generates actual segment geometries from H3 cell centers.
        Does NOT draw a straight line between origin and destination.
        """
        # Walk backwards through the label chain
        labels_chain = []
        current = label
        while current is not None:
            labels_chain.append(current)
            current = current.parent_label

        labels_chain.reverse()  # Now origin-first

        segments = []
        for i in range(len(labels_chain) - 1):
            from_label = labels_chain[i]
            to_label = labels_chain[i + 1]

            from_state = from_label.state
            to_state = to_label.state

            dist = haversine_distance(
                from_state.latitude, from_state.longitude,
                to_state.latitude, to_state.longitude,
            )
            duration = to_state.arrival_time - from_state.arrival_time

            fuel_delta = to_state.accumulated_fuel - from_state.accumulated_fuel
            sic_delta = to_state.accumulated_sea_ice_exposure - from_state.accumulated_sea_ice_exposure
            iceberg_delta = to_state.accumulated_iceberg_exposure - from_state.accumulated_iceberg_exposure
            safety_delta = to_state.accumulated_safety_uncertainty - from_state.accumulated_safety_uncertainty

            segments.append(RouteSegmentData(
                segment_id=str(uuid.uuid4()),
                from_cell=from_state.node_id,
                to_cell=to_state.node_id,
                start_lat=from_state.latitude,
                start_lon=from_state.longitude,
                end_lat=to_state.latitude,
                end_lon=to_state.longitude,
                departure_time=from_state.arrival_time,
                arrival_time=to_state.arrival_time,
                duration_hours=duration,
                speed_knots=to_state.current_speed,
                speed_mode=to_state.speed_mode,
                distance_nm=dist,
                fuel_tons=fuel_delta,
                sea_ice_exposure=sic_delta,
                iceberg_exposure=iceberg_delta,
                safety_uncertainty=safety_delta,
                data_quality="UNKNOWN",
            ))

        obj = label.objective_vector
        route = ReconstructedRoute(
            route_id=f"motus-{label.label_id[:8]}",
            segments=segments,
            total_distance_nm=obj.distance,
            total_time_hours=obj.time,
            total_fuel_tons=obj.fuel,
            sea_ice_exposure=obj.sea_ice_exposure,
            iceberg_exposure=obj.iceberg,
            safety_uncertainty=obj.safety_uncertainty,
            objective_vector=obj,
            data_quality="UNKNOWN",
            explanation="Computed by DHRUV-MOTUS multi-objective search",
        )

        return route

    def select_route_by_policy(
        self,
        routes: List[ReconstructedRoute],
        policy: str = None,
    ) -> tuple:
        """
        TASK 5: Policy-based route selection from Pareto front.
        
        Policies:
          CONSERVATIVE: Minimize safety_uncertainty + iceberg exposure
          BALANCED: Weighted compromise across all objectives
          EFFICIENT: Minimize fuel + time
        
        Returns (selected_route, policy_status)
        
        Does NOT claim "best" or "guaranteed optimal" — uses
        "Recommended under selected policy".
        """
        if not routes:
            return None, "NO_ROUTES_AVAILABLE"

        if policy is None or policy == "":
            return None, "POLICY_SELECTION_PENDING"

        policy = policy.upper()

        if policy == "CONSERVATIVE":
            # Minimize risk: sort by safety_uncertainty + iceberg
            selected = min(
                routes,
                key=lambda r: r.safety_uncertainty + r.iceberg_exposure,
            )
            return selected, "RECOMMENDED_UNDER_CONSERVATIVE_POLICY"

        elif policy == "BALANCED":
            # Normalized compromise across objectives
            if len(routes) == 1:
                return routes[0], "RECOMMENDED_UNDER_BALANCED_POLICY"

            # Normalize each objective to [0, 1] within the Pareto set
            fuels = [r.total_fuel_tons for r in routes]
            times = [r.total_time_hours for r in routes]
            icebergs = [r.iceberg_exposure for r in routes]
            safeties = [r.safety_uncertainty for r in routes]

            def normalize(val, values):
                min_v, max_v = min(values), max(values)
                if max_v == min_v:
                    return 0.0
                return (val - min_v) / (max_v - min_v)

            best_score = float('inf')
            selected = routes[0]
            for r in routes:
                score = (
                    normalize(r.total_fuel_tons, fuels) * 0.25 +
                    normalize(r.total_time_hours, times) * 0.25 +
                    normalize(r.iceberg_exposure, icebergs) * 0.25 +
                    normalize(r.safety_uncertainty, safeties) * 0.25
                )
                if score < best_score:
                    best_score = score
                    selected = r

            return selected, "RECOMMENDED_UNDER_BALANCED_POLICY"

        elif policy == "EFFICIENT":
            # Minimize fuel + time
            selected = min(
                routes,
                key=lambda r: r.total_fuel_tons + r.total_time_hours,
            )
            return selected, "RECOMMENDED_UNDER_EFFICIENT_POLICY"

        else:
            return None, "POLICY_SELECTION_PENDING"
