import { Controller, Get, Post, Body, Param, HttpException, HttpStatus } from '@nestjs/common';

@Controller()
export class IcebergController {
  @Get('layers/icebergs')
  getIcebergLayer() {
    throw new HttpException({ layer: 'icebergs', status: 'unavailable', data_quality: 'RED', reason: 'Database connection blocked' }, HttpStatus.SERVICE_UNAVAILABLE);
  }

  @Get('icebergs/:iceberg_id')
  getIceberg(@Param('iceberg_id') icebergId: string) {
    throw new HttpException({ iceberg_id: icebergId, status: 'unavailable', data_quality: 'RED', reason: 'Database connection blocked' }, HttpStatus.SERVICE_UNAVAILABLE);
  }

  @Post('forecast/iceberg')
  generateForecast(@Body() body: any) {
    throw new HttpException({ forecast: null, status: 'unavailable', data_quality: 'RED', reason: 'Python worker not reachable via gRPC' }, HttpStatus.SERVICE_UNAVAILABLE);
  }
}
