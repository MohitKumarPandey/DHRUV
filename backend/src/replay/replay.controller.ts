import { Controller, Get, Param, HttpException, HttpStatus } from '@nestjs/common';

@Controller('replay')
export class ReplayController {
  @Get(':case_id')
  getReplay(@Param('case_id') caseId: string) {
    throw new HttpException('Historical replay unavailable (Database blocked)', HttpStatus.SERVICE_UNAVAILABLE);
  }
}
