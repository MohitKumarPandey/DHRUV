/**
 * DHRUV Routing API Client — TASK 24
 *
 * Client-side API functions to call the NestJS routing endpoints.
 * Returns typed responses matching the proto/DTO structure.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';

export interface Coordinate {
  lat: number;
  lon: number;
}

export interface VesselProfile {
  id?: string;
  draft?: number;
  max_speed?: number;
  cruise_speed?: number;
  min_speed?: number;
  ice_class?: string;
  maximum_operational_sic?: number;
}

export interface RouteRequest {
  case_id: string;
  origin: Coordinate;
  destination: Coordinate;
  departure_time?: string;
  vessel?: VesselProfile;
  policy?: 'CONSERVATIVE' | 'BALANCED' | 'EFFICIENT';
  algorithm?: 'DIJKSTRA' | 'ASTAR' | 'DHRUV_MOTUS';
}

export interface RouteSegment {
  segment_id: string;
  start: Coordinate;
  end: Coordinate;
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

export interface RouteMetrics {
  total_time_hours: number;
  total_fuel_tons: number;
  total_distance_nm: number;
  sea_ice_exposure: number;
  iceberg_exposure: number;
  safety_uncertainty: number;
}

export interface ExecutionMetrics {
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

export interface RouteResult {
  route_id: string;
  segments: RouteSegment[];
  metrics: RouteMetrics;
  fallback_status: string;
  explanation: string;
}

export interface RouteResponse {
  case_id: string;
  algorithm: string;
  status: string;
  selected_route?: RouteResult;
  pareto_routes?: RouteResult[];
  execution_metrics?: ExecutionMetrics;
  data_quality: string;
  warnings: string;
  policy_status: string;
  missing_data_sources: string;
}

export async function generateRoute(request: RouteRequest): Promise<RouteResponse> {
  const response = await fetch(`${API_BASE}/api/v1/routing/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Route generation failed (${response.status}): ${errorBody}`);
  }

  return response.json();
}
