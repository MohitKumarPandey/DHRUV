import { Controller, Get, Param, HttpException, HttpStatus } from '@nestjs/common';

@Controller('report')
export class ReportsController {
  @Get(':route_id')
  getReport(@Param('route_id') routeId: string) {
    throw new HttpException('Database connection blocked', HttpStatus.SERVICE_UNAVAILABLE);
  }

  @Get('dashboard/metrics')
  getScientificMetrics() {
    throw new HttpException('Database connection blocked', HttpStatus.SERVICE_UNAVAILABLE);
  }
}
