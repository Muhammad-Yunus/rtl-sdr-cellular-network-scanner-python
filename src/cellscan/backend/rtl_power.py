"""Backend for executing rtl_power."""

from __future__ import annotations

import asyncio
import pathlib
from datetime import datetime, timezone

from pydantic import BaseModel

from cellscan.backend.validator import check_backend, find_rtl_power_exe


class ScanConfig(BaseModel):
    """Configuration for a rtl_power scan."""

    start_hz: int
    end_hz: int
    step_hz: int = 1_000
    dwell: float = 1.0
    sweep_time: float = 60.0
    directory: pathlib.Path = pathlib.Path("captures")


class RTLPowerBackend:
    """Execute rtl_power and capture CSV output to stdout.

    Responsibilities:
    - detect rtl_power executable
    - build command with provided config
    - execute with timeout and cancellation support
    - capture stdout (CSV data) and stderr (progress log)

    This backend SHALL NOT parse or analyse CSV content.
    """

    def __init__(self, rtl_power_path: str | None = None) -> None:
        self._rtl_power_path = rtl_power_path or str(find_rtl_power_exe())
        self._proc: asyncio.subprocess.Process[bytes] | None = None

    def build_command(self, config: ScanConfig) -> list[str]:
        """Build the rtl_power command."""
        return [
            self._rtl_power_path,
            "-f", f"{config.start_hz}:{config.end_hz}:{config.step_hz}",
            "-i", str(int(config.dwell)),
            "-e", str(int(config.sweep_time)),
            "-c", "20%",
        ]

    async def run(self, config: ScanConfig) -> tuple[bytes, bytes]:
        """Execute rtl_power and return (stdout, stderr)."""
        cmd = self.build_command(config)
        self._proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                self._proc.communicate(),
                timeout=config.sweep_time + 10,
            )
            return stdout, stderr
        except asyncio.TimeoutError:
            await self.cancel()
            raise RuntimeError("rtl_power timed out")

    async def cancel(self) -> None:
        """Terminate the running rtl_power process."""
        if self._proc and self._proc.returncode is None:
            self._proc.kill()
