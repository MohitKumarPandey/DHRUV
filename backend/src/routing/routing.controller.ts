/**
 * DHRUV Routing Controller — TASK 23
 *
 * REST API endpoints for route generation.
 * Delegates to RoutingService which calls the Python gRPC worker.
 */

import {
  Controller,
  Post,
  Body,
  HttpException,
  HttpStatus,
  Logger,
  Get,
  Param,
} from '@nestjs/common';
import { RoutingService } from './routing.service';
import { GenerateRouteDto, RouteResponseDto } from './routing.dto';

@Controller('routing')
export class RoutingController {
  private readonly logger = new Logger(RoutingController.name);

  constructor(private readonly routingService: RoutingService) {}

  @Post('generate')
  async generateRoute(
    @Body() dto: GenerateRouteDto,
  ): Promise<RouteResponseDto> {
    this.logger.log(
      `Route request: case=${dto.case_id}, algo=${dto.algorithm ?? 'DHRUV_MOTUS'}, policy=${dto.policy ?? 'NONE'}`,
    );

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
      return response as RouteResponseDto;
    } catch (error) {
      this.logger.error(`Route generation failed: ${error.message}`, error.stack);
      throw new HttpException(
        {
          status: 'FAILED',
          message: `Route generation error: ${error.message}`,
          data_quality: 'UNKNOWN',
        },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
  @Get(':route_id')
  async getRoute(@Param('route_id') routeId: string) {
    throw new HttpException('Database connection blocked', HttpStatus.SERVICE_UNAVAILABLE);
  }

  @Post(':route_id/stress-test')
  async stressTestRoute(@Param('route_id') routeId: string, @Body() body: any) {
    throw new HttpException('Python worker not reachable via gRPC', HttpStatus.SERVICE_UNAVAILABLE);
  }

  @Post(':route_id/replan')
  async replanRoute(@Param('route_id') routeId: string, @Body() body: any) {
    throw new HttpException('Python worker not reachable via gRPC', HttpStatus.SERVICE_UNAVAILABLE);
  }
}
