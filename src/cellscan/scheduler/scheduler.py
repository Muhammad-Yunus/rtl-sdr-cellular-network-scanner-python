"""Scheduler — generates scan jobs from bands.json."""

from __future__ import annotations

import json
from pathlib import Path

from cellscan.model.spectrum import ScanJob


class ScanScheduler:
    """Create scan jobs from the bands configuration."""

    def __init__(self, db_path: Path | None = None) -> None:
        if db_path is None:
            db_path = Path(__file__).parents[3] / "database" / "bands.json"
        self._jobs: list[ScanJob] = []
        self._load_jobs(db_path)

    def _load_jobs(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data:
            if entry.get("enabled", True):
                self._jobs.append(
                    ScanJob(
                        technology=entry["technology"],
                        band=entry["band"],
                        start_hz=entry["start"],
                        end_hz=entry["end"],
                        enabled=entry.get("enabled", True),
                    )
                )

    @property
    def jobs(self) -> list[ScanJob]:
        return list(self._jobs)

    def filter_by_technology(self, technology: str) -> list[ScanJob]:
        """Return jobs matching the given technology (e.g. 'LTE', 'GSM')."""
        return [j for j in self._jobs if j.technology.upper() == technology.upper()]
