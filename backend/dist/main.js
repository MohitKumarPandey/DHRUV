"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const core_1 = require("@nestjs/core");
const app_module_1 = require("./app.module");
const common_1 = require("@nestjs/common");
async function bootstrap() {
    const app = await core_1.NestFactory.create(app_module_1.AppModule);
    app.setGlobalPrefix('api/v1');
    app.enableCors();
    app.useGlobalPipes(new common_1.ValidationPipe({ transform: true }));
    const port = parseInt(process.env.PORT ?? "3000", 10);
    await app.listen(port);
    console.log(`🚀 DHRUV API is running on: http://localhost:${port}`);
}
bootstrap().catch((err) => {
    console.error('Error during NestJS bootstrap:', err);
    process.exit(1);
});
//# sourceMappingURL=main.js.map