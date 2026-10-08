# DHRUV – Dynamic Hazard Route Optimization Underway Vessel

## Overview
This repository implements the full DHRUV decision‑support system as specified:
- **NestJS (TypeScript) backend** with all required modules, PostgreSQL/PostGIS, Redis/BullMQ, and gRPC integration.
- **Next.js (TypeScript) frontend** using Tailwind, Shadcn UI, and MapLibre GL for the Antarctic map.
- **Python scientific workers** exposing gRPC services for sea‑ice forecasting, iceberg detection, trajectory prediction, risk fields, and routing.
- **Docker Compose** wiring all components together (API, frontend, DB, Redis, MinIO, Python worker).

## Repository Structure
```
/                   # repository root
├─ backend/         # NestJS API
│   ├─ src/        # source code, modules, controllers, services
│   ├─ Dockerfile
│   └─ package.json
├─ frontend/       # Next.js UI
│   ├─ src/        # pages, components, styles
│   ├─ Dockerfile
│   └─ package.json
├─ python/          # Python workers
│   ├─ worker/     # gRPC service implementations
│   ├─ requirements.txt
│   └─ Dockerfile
├─ docker-compose.yml
└─ README.md       # (this file)
``` 

## Quick Start (development)
1. **Prerequisites** – Docker Desktop (or Docker Engine) and Node 18+ installed.
2. **Clone the repo** and navigate to the root directory.
3. **Start the stack**:
   ```bash
   docker compose up --build
   ```
   This will build and run:
   - `api` (NestJS) on `http://localhost:3000`
   - `frontend` on `http://localhost:3001`
   - `postgres` with PostGIS, `redis`, `minio`, and `python-worker`.
4. **Access the UI** – open `http://localhost:3001` in a browser.
5. **API documentation** – Swagger UI is available at `http://localhost:3000/api`
