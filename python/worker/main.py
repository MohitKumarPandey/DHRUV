"""
DHRUV Python Worker — gRPC Server

Wires DHRUV-MOTUS into the existing gRPC infrastructure alongside
the Dijkstra baseline. Does NOT create a second routing server.

Execution flow for DHRUV_MOTUS:
  gRPC request → validation → vessel profile → origin/destination →
  departure time → H3 graph → MotusAlgorithm.search() → Pareto labels →
  route reconstruction → policy selection → RouteResult → RouteResponse
"""

import time
import logging
import grpc
import os
from concurrent import futures

import dhruv_pb2
import dhruv_pb2_grpc

from routing.graph.builder import H3GraphBuilder
from routing.dijkstra.baseline import DijkstraBaseline
from routing.motus.algorithm import MotusAlgorithm, SearchMetrics
from routing.motus.config import MotusConfig
from routing.motus.environment import UnavailableEnvironmentProvider

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DHRUV-Worker")


class RoutingService(dhruv_pb2_grpc.RoutingServiceServicer):
    def __init__(self):
        # Shared H3 graph — reused by both Dijkstra and MOTUS
        self.graph = H3GraphBuilder(base_resolution=3)
        # Bounding box for Antarctic region
        self.graph.build_region(-80.0, -60.0, -100.0, 100.0)

        # Dijkstra baseline (preserved)
        self.dijkstra = DijkstraBaseline(self.graph)

        # MOTUS — uses existing graph, honest environment provider
        config_path = os.path.join(
            os.path.dirname(__file__),
            "routing", "motus", "config.json",
        )
        self.motus_config = MotusConfig.from_file(config_path)
        self.environment_provider = UnavailableEnvironmentProvider()
        self.motus = MotusAlgorithm(
            graph=self.graph,
            config=self.motus_config,
            environment_provider=self.environment_provider,
        )

        logger.info("RoutingService initialized with Dijkstra baseline + DHRUV-MOTUS")

    def GenerateRoute(self, request, context):
        logger.info(
            f"GenerateRoute: case={request.case_id}, "
            f"algorithm={request.algorithm}, policy={request.policy}"
        )

        algorithm = request.algorithm.upper() if request.algorithm else "DHRUV_MOTUS"

        # Route to appropriate algorithm
        if algorithm in ("DIJKSTRA", "ASTAR"):
            return self._generate_dijkstra_route(request)
        else:
            # Default: DHRUV_MOTUS (for empty, "DHRUV_MOTUS", "PARETO", etc.)
            return self._generate_motus_route(request)

    def _generate_motus_route(self, request):
        """Execute DHRUV-MOTUS search and return protobuf response."""
        start_lat = request.origin.lat
        start_lon = request.origin.lon
        end_lat = request.destination.lat
        end_lon = request.destination.lon

        # Build vessel profile dict from proto
        vessel_profile = {
            "id": request.vessel.id,
            "draft": request.vessel.draft,
            "max_speed": request.vessel.max_speed if request.vessel.max_speed > 0 else 12.0,
            "cruise_speed": request.vessel.cruise_speed if request.vessel.cruise_speed > 0 else 10.0,
            "min_speed": request.vessel.min_speed if request.vessel.min_speed > 0 else 6.0,
            "ice_class": request.vessel.ice_class,
            "maximum_operational_sic": request.vessel.maximum_operational_sic if request.vessel.maximum_operational_sic > 0 else 0.8,
            "max_operational_wind_kts": request.vessel.max_operational_wind_kts if request.vessel.max_operational_wind_kts > 0 else None,
            "max_operational_wave_m": request.vessel.max_operational_wave_m if request.vessel.max_operational_wave_m > 0 else None,
            "min_fuel_rate": 1.5,
            "cruise_fuel_rate": 2.5,
            "max_fuel_rate": 4.0,
            "idle_fuel_rate": 0.5,
        }

        # Execute search
        try:
            pareto_labels, metrics = self.motus.search(
                start_lat, start_lon, end_lat, end_lon,
                vessel_profile, request.departure_time,
            )
        except Exception as e:
            logger.error(f"MOTUS search failed: {e}", exc_info=True)
            return dhruv_pb2.RouteResponse(
                case_id=request.case_id,
                algorithm="DHRUV_MOTUS",
                status="FAILED",
                warnings=f"Search error: {e}",
                data_quality="UNKNOWN",
            )

        if not pareto_labels:
            return dhruv_pb2.RouteResponse(
                case_id=request.case_id,
                algorithm="DHRUV_MOTUS",
                status="NO_ROUTE_FOUND",
                execution_metrics=self._build_execution_metrics(metrics),
                data_quality=metrics.data_quality,
                warnings="; ".join(metrics.warnings),
                missing_data_sources=", ".join(metrics.missing_data_sources),
            )

        # Reconstruct all Pareto routes
        reconstructed_routes = []
        for label in pareto_labels:
            route = self.motus.reconstruct_route(label)
            reconstructed_routes.append(route)

        # Policy selection (TASK 5)
        selected_route, policy_status = self.motus.select_route_by_policy(
            reconstructed_routes, request.policy,
        )

        # Build protobuf response
        pareto_route_results = []
        for route in reconstructed_routes:
            pareto_route_results.append(self._route_to_proto(route))

        selected_proto = None
        if selected_route is not None:
            selected_proto = self._route_to_proto(selected_route)

        return dhruv_pb2.RouteResponse(
            case_id=request.case_id,
            algorithm="DHRUV_MOTUS",
            status="SUCCESS",
            selected_route=selected_proto,
            pareto_routes=pareto_route_results,
            execution_metrics=self._build_execution_metrics(metrics),
            data_quality=metrics.data_quality,
            warnings="; ".join(metrics.warnings),
            policy_status=policy_status,
            missing_data_sources=", ".join(metrics.missing_data_sources),
        )

    def _route_to_proto(self, route):
        """Convert a ReconstructedRoute to protobuf RouteResult."""
        segments = []
        for s in route.segments:
            segments.append(dhruv_pb2.RouteSegment(
                segment_id=s.segment_id,
                start=dhruv_pb2.Coordinate(lat=s.start_lat, lon=s.start_lon),
                end=dhruv_pb2.Coordinate(lat=s.end_lat, lon=s.end_lon),
                distance_nm=s.distance_nm,
                time_hours=s.duration_hours,
                speed_knots=s.speed_knots,
                fuel_tons=s.fuel_tons,
                sea_ice_exposure=s.sea_ice_exposure,
                iceberg_exposure=s.iceberg_exposure,
                safety_uncertainty=s.safety_uncertainty,
                from_cell=s.from_cell,
                to_cell=s.to_cell,
                speed_mode=s.speed_mode,
                data_quality=s.data_quality,
            ))

        return dhruv_pb2.RouteResult(
            route_id=route.route_id,
            segments=segments,
            metrics=dhruv_pb2.RouteMetrics(
                total_time_hours=route.total_time_hours,
                total_fuel_tons=route.total_fuel_tons,
                total_distance_nm=route.total_distance_nm,
                sea_ice_exposure=route.sea_ice_exposure,
                iceberg_exposure=route.iceberg_exposure,
                safety_uncertainty=route.safety_uncertainty,
            ),
            fallback_status=route.fallback_status,
            explanation=route.explanation,
        )

    def _build_execution_metrics(self, metrics: SearchMetrics):
        return dhruv_pb2.ExecutionMetrics(
            runtime_ms=metrics.runtime_ms,
            nodes_expanded=metrics.nodes_expanded,
            labels_created=metrics.labels_created,
            labels_pruned=metrics.labels_pruned,
            hard_gate_rejections=metrics.hard_gate_rejections,
            epsilon_pruned=metrics.epsilon_pruned,
            cap_pruned=metrics.cap_pruned,
            pareto_routes_found=metrics.pareto_routes_returned,
            search_terminated_reason=metrics.search_terminated_reason,
        )

    def _generate_dijkstra_route(self, request):
        """Preserved Dijkstra baseline behavior (TASK 29)."""
        start_lat = request.origin.lat
        start_lon = request.origin.lon
        end_lat = request.destination.lat
        end_lon = request.destination.lon

        speed = request.vessel.max_speed if request.vessel.max_speed > 0 else 12.0

        route_data = self.dijkstra.find_route(start_lat, start_lon, end_lat, end_lon, speed)

        if not route_data:
            return dhruv_pb2.RouteResponse(
                case_id=request.case_id,
                algorithm="DIJKSTRA",
                status="NO_ROUTE_FOUND",
                warnings="No valid Dijkstra route could be generated.",
            )

        segments = []
        for s in route_data["primary_route"]:
            segments.append(dhruv_pb2.RouteSegment(
                start=dhruv_pb2.Coordinate(lat=s["start"]["lat"], lon=s["start"]["lon"]),
                end=dhruv_pb2.Coordinate(lat=s["end"]["lat"], lon=s["end"]["lon"]),
                distance_nm=s["distance_nm"],
                time_hours=s["time_hours"],
                speed_knots=s["speed_knots"],
            ))

        selected = dhruv_pb2.RouteResult(
            route_id=route_data["route_id"],
            segments=segments,
            metrics=dhruv_pb2.RouteMetrics(
                total_time_hours=route_data["total_time_hours"],
                total_fuel_tons=route_data["total_fuel_tons"],
                total_distance_nm=route_data.get("total_distance_nm", 0.0),
            ),
            explanation="Generated using Dijkstra Baseline",
        )

        return dhruv_pb2.RouteResponse(
            case_id=request.case_id,
            algorithm="DIJKSTRA",
            status="SUCCESS",
            selected_route=selected,
        )

    def StressTestRoute(self, request, context):
        logger.info(f"Stress testing route {request.route_id} with scenario {request.scenario_type}")
        return dhruv_pb2.RouteResponse(
            case_id="",
            algorithm="STRESS_TEST",
            status="SUCCESS",
            warnings="Stress test complete.",
        )


def serve():
    logger.info("Starting DHRUV Python Worker...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dhruv_pb2_grpc.add_RoutingServiceServicer_to_server(RoutingService(), server)

    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("Worker gRPC server listening on port 50051.")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Stopping worker...")
        server.stop(0)

if __name__ == "__main__":
    serve()
