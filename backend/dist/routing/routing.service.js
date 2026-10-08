"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var RoutingService_1;
Object.defineProperty(exports, "__esModule", { value: true });
exports.RoutingService = void 0;
const common_1 = require("@nestjs/common");
const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");
const path = require("path");
const PROTO_PATH = path.join(__dirname, '../../../../python/worker/dhruv.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true,
});
const dhruvProto = grpc.loadPackageDefinition(packageDefinition).dhruv;
let RoutingService = RoutingService_1 = class RoutingService {
    constructor() {
        this.logger = new common_1.Logger(RoutingService_1.name);
    }
    onModuleInit() {
        const grpcHost = process.env.GRPC_WORKER_HOST || 'localhost:50051';
        this.logger.log(`Connecting to Python gRPC worker at ${grpcHost}`);
        this.routingClient = new dhruvProto.RoutingService(grpcHost, grpc.credentials.createInsecure());
    }
    async generateRoute(payload) {
        return new Promise((resolve, reject) => {
            this.routingClient.GenerateRoute(payload, (error, response) => {
                if (error) {
                    this.logger.error(`gRPC error: ${error.message}`);
                    reject(error);
                }
                else {
                    this.logger.log(`Route response: status=${response.status}, algo=${response.algorithm}, ` +
                        `data_quality=${response.data_quality}, policy=${response.policy_status}`);
                    resolve(response);
                }
            });
        });
    }
};
exports.RoutingService = RoutingService;
exports.RoutingService = RoutingService = RoutingService_1 = __decorate([
    (0, common_1.Injectable)()
], RoutingService);
//# sourceMappingURL=routing.service.js.map