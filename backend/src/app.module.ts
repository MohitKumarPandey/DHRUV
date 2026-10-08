import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { BullModule } from '@nestjs/bullmq';

import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';
import { CasesModule } from './cases/cases.module';
import { DataModule } from './data/data.module';
import { SatelliteModule } from './satellite/satellite.module';
import { SeaIceModule } from './sea-ice/sea-ice.module';
import { IcebergModule } from './iceberg/iceberg.module';
import { WeatherModule } from './weather/weather.module';
import { OceanModule } from './ocean/ocean.module';
import { VesselModule } from './vessel/vessel.module';
import { RiskModule } from './risk/risk.module';
import { RoutingModule } from './routing/routing.module';
import { ScenarioModule } from './scenario/scenario.module';
import { FallbackModule } from './fallback/fallback.module';
import { ReplanningModule } from './replanning/replanning.module';
import { ReplayModule } from './replay/replay.module';
import { ReportsModule } from './reports/reports.module';
import { AgentModule } from './agent/agent.module';
import { JobsModule } from './jobs/jobs.module';
import { HealthModule } from './health/health.module';
import { AuditModule } from './audit/audit.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    TypeOrmModule.forRoot({
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
    BullModule.forRoot({
      connection: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT, 10) || 6379,
      },
    }),
    AuthModule,
    UsersModule,
    CasesModule,
    DataModule,
    SatelliteModule,
    SeaIceModule,
    IcebergModule,
    WeatherModule,
    OceanModule,
    VesselModule,
    RiskModule,
    RoutingModule,
    ScenarioModule,
    FallbackModule,
    ReplanningModule,
    ReplayModule,
    ReportsModule,
    AgentModule,
    JobsModule,
    HealthModule,
    AuditModule
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}
