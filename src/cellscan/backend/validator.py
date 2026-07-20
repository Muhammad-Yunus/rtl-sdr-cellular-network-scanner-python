"""Backend validation module."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from cellscan.util.find import _search_extra_paths


def _find_executable(name: str) -> Path | None:
    """Find any executable on PATH or in conda Library/bin."""
    import shutil
    which = shutil.which(name)
    if which:
        return Path(which)
    suffix = ".exe" if os.name == "nt" else ""
    for directory in _search_extra_paths():
        candidate = directory / f"{name}{suffix}"
        if candidate.is_file():
            return candidate
    return None


def find_rtl_power_exe() -> str:
    """Return path to rtl_power executable, raising FileNotFoundError if missing."""
    info = check_backend()
    if info.path is None:
        raise FileNotFoundError("rtl_power not found on PATH")
    return str(info.path)


class RTLPowerInfo:
    """Information about rtl_power availability and state."""

    def __init__(
        self,
        available: bool,
        path: Path | None = None,
        error: str | None = None,
        rtl_sdr_available: bool = False,
        rtl_eeprom_available: bool = False,
    ) -> None:
        self.available = available
        self.path = path
        self.error = error
        self.rtl_sdr_available = rtl_sdr_available
        self.rtl_eeprom_available = rtl_eeprom_available

    @property
    def device_connected(self) -> bool:
        """Return True if an RTL-SDR device is physically connected."""
        eeprom = _find_executable("rtl_eeprom")
        if eeprom is None:
            return False
        try:
            result = subprocess.run(
                [str(eeprom)],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return False


def check_backend() -> RTLPowerInfo:
    """Validate that rtl_power is installed and RTL-SDR tools are available."""
    path = _find_executable("rtl_power") or _find_executable("rtl_power.exe")
    if path is None:
        return RTLPowerInfo(available=False, error="rtl_power not found on PATH")

    return RTLPowerInfo(
        available=True,
        path=path,
        rtl_sdr_available=_find_executable("rtl_sdr") is not None,
        rtl_eeprom_available=_find_executable("rtl_eeprom") is not None,
    )