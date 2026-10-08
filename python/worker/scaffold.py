import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

dirs = [
    "grpc", "data", "ingestion", "ingestion/providers", "preprocessing",
    "sea_ice", "iceberg", "weather", "ocean", "risk", "routing",
    "routing/graph", "routing/dijkstra", "routing/astar", "routing/pareto",
    "routing/hf_psta", "scenarios", "fallback", "models", "evaluation",
    "provenance", "tests"
]

for d in dirs:
    dir_path = BASE_DIR / d
    dir_path.mkdir(parents=True, exist_ok=True)
    init_file = dir_path / "__init__.py"
    if not init_file.exists():
        init_file.touch()

print("Python worker directory structure created successfully.")
