"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AppModule = void 0;
const common_1 = require("@nestjs/common");
const config_1 = require("@nestjs/config");
const typeorm_1 = require("@nestjs/typeorm");
const bullmq_1 = require("@nestjs/bullmq");
const auth_module_1 = require("./auth/auth.module");
const users_module_1 = require("./users/users.module");
const cases_module_1 = require("./cases/cases.module");
const data_module_1 = require("./data/data.module");
const satellite_module_1 = require("./satellite/satellite.module");
const sea_ice_module_1 = require("./sea-ice/sea-ice.module");
const iceberg_module_1 = require("./iceberg/iceberg.module");
const weather_module_1 = require("./weather/weather.module");
const ocean_module_1 = require("./ocean/ocean.module");
const vessel_module_1 = require("./vessel/vessel.module");
const risk_module_1 = require("./risk/risk.module");
const routing_module_1 = require("./routing/routing.module");
const scenario_module_1 = require("./scenario/scenario.module");
const fallback_module_1 = require("./fallback/fallback.module");
const replanning_module_1 = require("./replanning/replanning.module");
const replay_module_1 = require("./replay/replay.module");
const reports_module_1 = require("./reports/reports.module");
const agent_module_1 = require("./agent/agent.module");
const jobs_module_1 = require("./jobs/jobs.module");
const health_module_1 = require("./health/health.module");
const audit_module_1 = require("./audit/audit.module");
let AppModule = class AppModule {
};
exports.AppModule = AppModule;
exports.AppModule = AppModule = __decorate([
    (0, common_1.Module)({
        imports: [
            config_1.ConfigModule.forRoot({ isGlobal: true }),
            typeorm_1.TypeOrmModule.forRoot({
                type: 'postgres',
                host: process.env.DB_HOST || 'localhost',
                port: parseInt(process.env.DB_PORT, 10) || 5432,
                username: process.env.DB_USER || 'dhruv_user',
                password: process.env.DB_PASSWORD || 'dhruv_pass',
                database: process.env.DB_NAME || 'dhruv_db',
                autoLoadEntities: true,
                synchronize: process.env.NODE_ENV !== 'production',
                logging: false,
            }),
            bullmq_1.BullModule.forRoot({
                connection: {
                    host: process.env.REDIS_HOST || 'localhost',
                    port: parseInt(process.env.REDIS_PORT, 10) || 6379,
                },
            }),
            auth_module_1.AuthModule,
            users_module_1.UsersModule,
            cases_module_1.CasesModule,
            data_module_1.DataModule,
            satellite_module_1.SatelliteModule,
            sea_ice_module_1.SeaIceModule,
            iceberg_module_1.IcebergModule,
            weather_module_1.WeatherModule,
            ocean_module_1.OceanModule,
            vessel_module_1.VesselModule,
            risk_module_1.RiskModule,
            routing_module_1.RoutingModule,
            scenario_module_1.ScenarioModule,
            fallback_module_1.FallbackModule,
            replanning_module_1.ReplanningModule,
            replay_module_1.ReplayModule,
            reports_module_1.ReportsModule,
            agent_module_1.AgentModule,
            jobs_module_1.JobsModule,
            health_module_1.HealthModule,
            audit_module_1.AuditModule
        ],
        controllers: [],
        providers: [],
    })
], AppModule);
//# sourceMappingURL=app.module.js.map