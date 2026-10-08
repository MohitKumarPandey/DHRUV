"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.RouteResponseDto = exports.ExecutionMetricsDto = exports.RouteResultDto = exports.RouteMetricsDto = exports.RouteSegmentDto = exports.GenerateRouteDto = exports.VesselProfileDto = exports.CoordinateDto = exports.RoutingPolicy = exports.RoutingAlgorithm = void 0;
const class_validator_1 = require("class-validator");
const class_transformer_1 = require("class-transformer");
var RoutingAlgorithm;
(function (RoutingAlgorithm) {
    RoutingAlgorithm["DIJKSTRA"] = "DIJKSTRA";
    RoutingAlgorithm["ASTAR"] = "ASTAR";
    RoutingAlgorithm["PARETO"] = "PARETO";
    RoutingAlgorithm["DHRUV_MOTUS"] = "DHRUV_MOTUS";
})(RoutingAlgorithm || (exports.RoutingAlgorithm = RoutingAlgorithm = {}));
var RoutingPolicy;
(function (RoutingPolicy) {
    RoutingPolicy["CONSERVATIVE"] = "CONSERVATIVE";
    RoutingPolicy["BALANCED"] = "BALANCED";
    RoutingPolicy["EFFICIENT"] = "EFFICIENT";
})(RoutingPolicy || (exports.RoutingPolicy = RoutingPolicy = {}));
class CoordinateDto {
}
exports.CoordinateDto = CoordinateDto;
__decorate([
    (0, class_validator_1.IsNumber)(),
    __metadata("design:type", Number)
], CoordinateDto.prototype, "lat", void 0);
__decorate([
    (0, class_validator_1.IsNumber)(),
    __metadata("design:type", Number)
], CoordinateDto.prototype, "lon", void 0);
class VesselProfileDto {
}
exports.VesselProfileDto = VesselProfileDto;
__decorate([
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", String)
], VesselProfileDto.prototype, "id", void 0);
__decorate([
    (0, class_validator_1.IsNumber)(),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", Number)
], VesselProfileDto.prototype, "draft", void 0);
__decorate([
    (0, class_validator_1.IsNumber)(),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", Number)
], VesselProfileDto.prototype, "max_speed", void 0);
__decorate([
    (0, class_validator_1.IsNumber)(),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", Number)
], VesselProfileDto.prototype, "cruise_speed", void 0);
__decorate([
    (0, class_validator_1.IsNumber)(),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", Number)
], VesselProfileDto.prototype, "min_speed", void 0);
__decorate([
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", String)
], VesselProfileDto.prototype, "ice_class", void 0);
__decorate([
    (0, class_validator_1.IsNumber)(),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", Number)
], VesselProfileDto.prototype, "maximum_operational_sic", void 0);
__decorate([
    (0, class_validator_1.IsNumber)(),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", Number)
], VesselProfileDto.prototype, "max_operational_wind_kts", void 0);
__decorate([
    (0, class_validator_1.IsNumber)(),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", Number)
], VesselProfileDto.prototype, "max_operational_wave_m", void 0);
class GenerateRouteDto {
}
exports.GenerateRouteDto = GenerateRouteDto;
__decorate([
    (0, class_validator_1.IsString)(),
    __metadata("design:type", String)
], GenerateRouteDto.prototype, "case_id", void 0);
__decorate([
    (0, class_validator_1.ValidateNested)(),
    (0, class_transformer_1.Type)(() => CoordinateDto),
    __metadata("design:type", CoordinateDto)
], GenerateRouteDto.prototype, "origin", void 0);
__decorate([
    (0, class_validator_1.ValidateNested)(),
    (0, class_transformer_1.Type)(() => CoordinateDto),
    __metadata("design:type", CoordinateDto)
], GenerateRouteDto.prototype, "destination", void 0);
__decorate([
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", String)
], GenerateRouteDto.prototype, "departure_time", void 0);
__decorate([
    (0, class_validator_1.ValidateNested)(),
    (0, class_transformer_1.Type)(() => VesselProfileDto),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", VesselProfileDto)
], GenerateRouteDto.prototype, "vessel", void 0);
__decorate([
    (0, class_validator_1.IsEnum)(RoutingPolicy),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", String)
], GenerateRouteDto.prototype, "policy", void 0);
__decorate([
    (0, class_validator_1.IsString)(),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", String)
], GenerateRouteDto.prototype, "arrival_window", void 0);
__decorate([
    (0, class_validator_1.IsEnum)(RoutingAlgorithm),
    (0, class_validator_1.IsOptional)(),
    __metadata("design:type", String)
], GenerateRouteDto.prototype, "algorithm", void 0);
class RouteSegmentDto {
}
exports.RouteSegmentDto = RouteSegmentDto;
class RouteMetricsDto {
}
exports.RouteMetricsDto = RouteMetricsDto;
class RouteResultDto {
}
exports.RouteResultDto = RouteResultDto;
class ExecutionMetricsDto {
}
exports.ExecutionMetricsDto = ExecutionMetricsDto;
class RouteResponseDto {
}
exports.RouteResponseDto = RouteResponseDto;
//# sourceMappingURL=routing.dto.js.map