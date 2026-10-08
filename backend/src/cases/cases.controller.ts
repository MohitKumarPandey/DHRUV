import { Controller, Get, Param, HttpException, HttpStatus } from '@nestjs/common';

@Controller('cases')
export class CasesController {
  @Get(':case_id')
  getCase(@Param('case_id') caseId: string) {
    throw new HttpException('Database connection unavailable (Docker down)', HttpStatus.SERVICE_UNAVAILABLE);
  }
}
