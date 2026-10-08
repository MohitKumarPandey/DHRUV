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
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
var RoutingController_1;
Object.defineProperty(exports, "__esModule", { value: true });
exports.RoutingController = void 0;
const common_1 = require("@nestjs/common");
const routing_service_1 = require("./routing.service");
const routing_dto_1 = require("./routing.dto");
let RoutingController = RoutingController_1 = class RoutingController {
    constructor(routingService) {
        this.routingService = routingService;
        this.logger = new common_1.Logger(RoutingController_1.name);
    }
    async generateRoute(dto) {
        this.logger.log(`Route request: case=${dto.case_id}, algo=${dto.algorithm ?? 'DHRUV_MOTUS'}, policy=${dto.policy ?? 'NONE'}`);
        try {
            const payload = {
                case_id: dto.case_id,
                origin: dto.origin,
                destination: dto.destination,
                departure_time: dto.departure_time ?? '',
                vessel: dto.vessel ?? {},
                policy: dto.policy ?? '',
                arrival_window: dto.arrival_window ?? '',
                algorithm: dto.algorithm ?? 'DHRUV_MOTUS',
            };
            const response = await this.routingService.generateRoute(payload);
            return response;
        }
        catch (error) {
            this.logger.error(`Route generation failed: ${error.message}`, error.stack);
            throw new common_1.HttpException({
                status: 'FAILED',
                message: `Route generation error: ${error.message}`,
                data_quality: 'UNKNOWN',
            }, common_1.HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    async getRoute(routeId) {
        return { route_id: routeId, status: 'retrieved' };
    }
    async stressTestRoute(routeId, body) {
        return { route_id: routeId, status: 'stress_tested', resilience_score: 0.85 };
    }
    async replanRoute(routeId, body) {
        return { route_id: routeId, status: 'replanned', new_route: [] };
    }
};
exports.RoutingController = RoutingController;
__decorate([
    (0, common_1.Post)('generate'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [routing_dto_1.GenerateRouteDto]),
    __metadata("design:returntype", Promise)
], RoutingController.prototype, "generateRoute", null);
__decorate([
    (0, common_1.Get)(':route_id'),
    __param(0, (0, common_1.Param)('route_id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], RoutingController.prototype, "getRoute", null);
__decorate([
    (0, common_1.Post)(':route_id/stress-test'),
    __param(0, (0, common_1.Param)('route_id')),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, Object]),
    __metadata("design:returntype", Promise)
], RoutingController.prototype, "stressTestRoute", null);
__decorate([
    (0, common_1.Post)(':route_id/replan'),
    __param(0, (0, common_1.Param)('route_id')),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, Object]),
    __metadata("design:returntype", Promise)
], RoutingController.prototype, "replanRoute", null);
exports.RoutingController = RoutingController = RoutingController_1 = __decorate([
    (0, common_1.Controller)('routing'),
    __metadata("design:paramtypes", [routing_service_1.RoutingService])
], RoutingController);
//# sourceMappingURL=routing.controller.js.map