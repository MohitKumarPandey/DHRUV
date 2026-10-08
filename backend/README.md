# DHRUV Backend (NestJS)

This directory contains the NestJS API server for the DHRUV platform.

## Project Structure
```
src/
  ├─ auth/
  ├─ users/
  ├─ cases/
  ├─ data/
  ├─ satellite/
  ├─ sea-ice/
  ├─ iceberg/
  ├─ weather/
  ├─ ocean/
  ├─ vessel/
  ├─ risk/
  ├─ routing/
  ├─ scenario/
  ├─ fallback/
  ├─ replanning/
  ├─ replay/
  ├─ reports/
  ├─ agent/
  ├─ jobs/
  └─ health/

modules/
  (each feature module)

main.ts – bootstrap NestJS
app.module.ts – root module
```

## Setup
```bash
# Install dependencies
npm install

# Run migrations (to be added)
# npm run migration:run

# Start development server
npm run start:dev
```

## Docker
A Dockerfile is provided in the root of this directory.

---
*This is a placeholder scaffold; further implementation will fill in controllers, services, DTOs, entities, and OpenAPI docs.*
