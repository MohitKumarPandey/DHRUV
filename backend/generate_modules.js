const fs = require('fs');
const path = require('path');

const modules = [
  'auth', 'users', 'cases', 'data', 'satellite', 'sea-ice', 'iceberg', 
  'weather', 'ocean', 'vessel', 'risk', 'routing', 'scenario', 'fallback', 
  'replanning', 'replay', 'reports', 'agent', 'jobs', 'health', 'audit'
];

const srcDir = path.join(__dirname, 'src');

if (!fs.existsSync(srcDir)) {
  fs.mkdirSync(srcDir, { recursive: true });
}

let appModuleImports = [];
let appModuleNames = [];

modules.forEach(mod => {
  const modDir = path.join(srcDir, mod);
  if (!fs.existsSync(modDir)) {
    fs.mkdirSync(modDir, { recursive: true });
  }

  // Convert kebab-case to PascalCase
  const pascalName = mod.split('-').map(part => part.charAt(0).toUpperCase() + part.slice(1)).join('');
  const className = `${pascalName}Module`;

  const moduleContent = `import { Module } from '@nestjs/common';

@Module({
  imports: [],
  controllers: [],
  providers: [],
  exports: [],
})
export class ${className} {}
`;

  fs.writeFileSync(path.join(modDir, `${mod}.module.ts`), moduleContent);
  
  appModuleImports.push(`import { ${className} } from './${mod}/${mod}.module';`);
  appModuleNames.push(className);
});

const appModuleContent = `import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { BullModule } from '@nestjs/bullmq';

${appModuleImports.join('\n')}

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
    ${appModuleNames.join(',\n    ')}
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}
`;

fs.writeFileSync(path.join(srcDir, 'app.module.ts'), appModuleContent);

console.log('Successfully generated NestJS modules and updated AppModule!');
