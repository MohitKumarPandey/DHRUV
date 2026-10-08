export declare enum RoutingAlgorithm {
    DIJKSTRA = "DIJKSTRA",
    ASTAR = "ASTAR",
    PARETO = "PARETO",
    DHRUV_MOTUS = "DHRUV_MOTUS"
}
export declare enum RoutingPolicy {
    CONSERVATIVE = "CONSERVATIVE",
    BALANCED = "BALANCED",
    EFFICIENT = "EFFICIENT"
}
export declare class CoordinateDto {
    lat: number;
    lon: number;
}
export declare class VesselProfileDto {
    id?: string;
    draft?: number;
    max_speed?: number;
    cruise_speed?: number;
    min_speed?: number;
    ice_class?: string;
    maximum_operational_sic?: number;
    max_operational_wind_kts?: number;
    max_operational_wave_m?: number;
}
export declare class GenerateRouteDto {
    case_id: string;
    origin: CoordinateDto;
    destination: CoordinateDto;
    departure_time?: string;
    vessel?: VesselProfileDto;
    policy?: RoutingPolicy;
    arrival_window?: string;
    algorithm?: RoutingAlgorithm;
}
export declare class RouteSegmentDto {
    segment_id: string;
    start: CoordinateDto;
    end: CoordinateDto;
    distance_nm: number;
    time_hours: number;
    speed_knots: number;
    fuel_tons: number;
    sea_ice_exposure: number;
    iceberg_exposure: number;
    safety_uncertainty: number;
    from_cell: string;
    to_cell: string;
    speed_mode: string;
    data_quality: string;
}
export declare class RouteMetricsDto {
    total_time_hours: number;
    total_fuel_tons: number;
    total_distance_nm: number;
    sea_ice_exposure: number;
    iceberg_exposure: number;
    safety_uncertainty: number;
}
export declare class RouteResultDto {
    route_id: string;
    segments: RouteSegmentDto[];
    metrics: RouteMetricsDto;
    fallback_status: string;
    explanation: string;
}
export declare class ExecutionMetricsDto {
    runtime_ms: number;
    nodes_expanded: number;
    labels_created: number;
    labels_pruned: number;
    hard_gate_rejections: number;
    epsilon_pruned: number;
    cap_pruned: number;
    pareto_routes_found: number;
    search_terminated_reason: string;
}
export declare class RouteResponseDto {
    case_id: string;
    algorithm: string;
    status: string;
    selected_route?: RouteResultDto;
    pareto_routes?: RouteResultDto[];
    execution_metrics?: ExecutionMetricsDto;
    data_quality: string;
    warnings: string;
    policy_status: string;
    missing_data_sources: string;
}
