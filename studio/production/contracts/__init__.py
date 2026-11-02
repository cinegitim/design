"""Brandstudio v1 portable contracts; no runtime actions."""
from pathlib import Path
SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"
SCHEMA_PATHS = {kind: SCHEMA_DIR / (kind.replace("_", "-") + ".schema.json") for kind in ("task", "capability-report", "task-receipt", "output-manifest")}
