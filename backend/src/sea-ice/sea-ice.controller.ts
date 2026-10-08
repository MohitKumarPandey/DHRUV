import { Controller, Get, Post, Body, HttpException, HttpStatus } from '@nestjs/common';

@Controller()
export class SeaIceController {
  @Get('layers/sea-ice')
  getSeaIceLayer() {
    throw new HttpException({ layer: 'sea-ice', status: 'unavailable', data_quality: 'RED', reason: 'Database connection blocked' }, HttpStatus.SERVICE_UNAVAILABLE);
  }

  @Post('forecast/sea-ice')
  generateForecast(@Body() body: any) {
    throw new HttpException({ forecast: null, status: 'unavailable', data_quality: 'RED', reason: 'Python worker not reachable via gRPC' }, HttpStatus.SERVICE_UNAVAILABLE);
  }
}
