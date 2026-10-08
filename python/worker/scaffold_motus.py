import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

motus_dir = BASE_DIR / "routing" / "motus"
motus_dir.mkdir(parents=True, exist_ok=True)
(motus_dir / "__init__.py").touch(exist_ok=True)

print("DHRUV-MOTUS directory structure created.")
