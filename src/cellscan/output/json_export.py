"""JSON export for scan results."""

from __future__ import annotations

import json
from pathlib import Path

from cellscan.model.spectrum import ScanResult


def export_json(result: ScanResult, path: Path) -> Path:
    """Serialize scan result to JSON and write to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.model_dump(), indent=2, default=str), encoding="utf-8")
    return path
