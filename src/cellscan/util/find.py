"""Utility functions for finding external tools."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def _search_extra_paths() -> list[Path]:
    """Return extra candidate directories to search for rtl_power.

    Covers common conda/mamba environments where rtl-sdr is installed to
    ``$CONDA_PREFIX/Library/bin`` rather than the main ``Scripts`` directory.
    """
    candidates: list[Path] = []
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        candidates.append(Path(conda_prefix) / "Library" / "bin")
        candidates.append(Path(conda_prefix) / "bin")
    candidates.append(Path("C:/Users/Asus/miniconda3/envs/cellscan/Library/bin"))
    candidates.append(Path("/c/Users/Asus/miniconda3/envs/cellscan/Library/bin"))
    return candidates


def find_rtl_power() -> Path | None:
    """Locate the rtl_power executable on PATH or in conda Library/bin."""
    which = shutil.which("rtl_power")
    if which:
        return Path(which)

    suffix = ".exe" if os.name == "nt" else ""
    for directory in _search_extra_paths():
        candidate = directory / f"rtl_power{suffix}"
        if candidate.is_file():
            return candidate
    return None