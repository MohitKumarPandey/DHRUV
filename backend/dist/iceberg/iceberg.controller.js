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
Object.defineProperty(exports, "__esModule", { value: true });
exports.IcebergController = void 0;
const common_1 = require("@nestjs/common");
let IcebergController = class IcebergController {
    getIcebergLayer() {
        return { layer: 'icebergs', data_quality: 'GREEN' };
    }
    getIceberg(icebergId) {
        return { iceberg_id: icebergId, status: 'detected' };
    }
    generateForecast(body) {
        return { forecast: 'generated', valid_time: new Date(), ensemble: [] };
    }
};
exports.IcebergController = IcebergController;
__decorate([
    (0, common_1.Get)('layers/icebergs'),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", void 0)
], IcebergController.prototype, "getIcebergLayer", null);
__decorate([
    (0, common_1.Get)('icebergs/:iceberg_id'),
    __param(0, (0, common_1.Param)('iceberg_id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], IcebergController.prototype, "getIceberg", null);
__decorate([
    (0, common_1.Post)('forecast/iceberg'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", void 0)
], IcebergController.prototype, "generateForecast", null);
exports.IcebergController = IcebergController = __decorate([
    (0, common_1.Controller)()
], IcebergController);
//# sourceMappingURL=iceberg.controller.js.map