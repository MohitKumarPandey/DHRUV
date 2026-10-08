/**
 * DHRUV Routing DTOs — TASK 23
 *
 * Typed request/response DTOs matching the extended dhruv.proto.
 * These are used by the NestJS routing controller and service.
 */

import { IsString, IsNumber, IsOptional, ValidateNested, IsEnum } from 'class-validator';
import { Type } from 'class-transformer';

// --- Enums ---

export enum RoutingAlgorithm {
  DIJKSTRA = 'DIJKSTRA',
  ASTAR = 'ASTAR',
  PARETO = 'PARETO',
  DHRUV_MOTUS = 'DHRUV_MOTUS',
}

export enum RoutingPolicy {
  CONSERVATIVE = 'CONSERVATIVE',
  BALANCED = 'BALANCED',
  EFFICIENT = 'EFFICIENT',
}

// --- Request DTOs ---

export class CoordinateDto {
  @IsNumber()
  lat: number;

  @IsNumber()
  lon: number;
}

export class VesselProfileDto {
  @IsString()
  @IsOptional()
  id?: string;

  @IsNumber()
  @IsOptional()
  draft?: number;

  @IsNumber()
  @IsOptional()
  max_speed?: number;

  @IsNumber()
  @IsOptional()
  cruise_speed?: number;

  @IsNumber()
  @IsOptional()
  min_speed?: number;

  @IsString()
  @IsOptional()
  ice_class?: string;

  @IsNumber()
  @IsOptional()
  maximum_operational_sic?: number;

  @IsNumber()
  @IsOptional()
  max_operational_wind_kts?: number;

  @IsNumber()
  @IsOptional()
  max_operational_wave_m?: number;
}

export class GenerateRouteDto {
  @IsString()
  case_id: string;

  @ValidateNested()
  @Type(() => CoordinateDto)
  origin: CoordinateDto;

  @ValidateNested()
  @Type(() => CoordinateDto)
  destination: CoordinateDto;

  @IsString()
  @IsOptional()
  departure_time?: string;

  @ValidateNested()
  @Type(() => VesselProfileDto)
  @IsOptional()
  vessel?: VesselProfileDto;

  @IsEnum(RoutingPolicy)
  @IsOptional()
  policy?: RoutingPolicy;

  @IsString()
  @IsOptional()
  arrival_window?: string;

  @IsEnum(RoutingAlgorithm)
  @IsOptional()
  algorithm?: RoutingAlgorithm;
}

// --- Response DTOs ---

export class RouteSegmentDto {
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

export class RouteMetricsDto {
  total_time_hours: number;
  total_fuel_tons: number;
  total_distance_nm: number;
  sea_ice_exposure: number;
  iceberg_exposure: number;
  safety_uncertainty: number;
}

export class RouteResultDto {
  route_id: string;
  segments: RouteSegmentDto[];
  metrics: RouteMetricsDto;
  fallback_status: string;
  explanation: string;
}

export class ExecutionMetricsDto {
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

export class RouteResponseDto {
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
