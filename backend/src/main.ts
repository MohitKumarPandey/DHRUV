import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Set global API prefix
  app.setGlobalPrefix('api/v1');
  // Enable CORS for client access
  app.enableCors();
  // Use validation pipe with transformation
  app.useGlobalPipes(new ValidationPipe({ transform: true }));

  const port = parseInt(process.env.PORT ?? "3000", 10);
  await app.listen(port);
  console.log(`🚀 DHRUV API is running on: http://localhost:${port}`);
}

bootstrap().catch((err) => {
  console.error('Error during NestJS bootstrap:', err);
  process.exit(1);
});
