"""CLI entry point for CellScan."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import click

# Force UTF-8 stdout so Unicode em-dashes render properly in Windows
if os.name == "nt":
    for stream in ("stdout", "stderr"):
        enc = getattr(__import__("sys"), stream).encoding
        if enc and "utf" not in enc.lower():
            os.environ["PYTHONUTF8"] = "1"

from cellscan.analysis.classifier import TechnologyClassifier, OperatorEstimator, build_carrier
from cellscan.analysis.peak_detector import CarrierPeakDetector
from cellscan.backend.rtl_power import RTLPowerBackend, ScanConfig
from cellscan.backend.validator import RTLPowerInfo, check_backend
from cellscan.model.spectrum import ScanResult
from cellscan.parser.csv import CSVParseError, RTLPowerCSVParser
from cellscan.output.terminal import format_terminal
from cellscan.scheduler.scheduler import ScanScheduler


@click.group()
@click.version_option(version="0.1.0", prog_name="cellscan")
def main() -> None:
    """CellScan - RF Carrier Scanner for Indonesian Cellular Spectrum."""


# ── backend check ──────────────────────────────────────────────


@main.group()
def backend() -> None:
    """Backend management commands."""


@backend.command("check")
def backend_check() -> None:
    """Check backend availability (rtl_power and RTL-SDR device)."""
    info = check_backend()
    click.echo("CellScan Backend Check")
    click.echo(f"  rtl_power   : {'[OK] ' + str(info.path) if info.available else '[FAIL] ' + str(info.error)}")
    click.echo(f"  rtl_sdr     : {'[OK]' if info.rtl_sdr_available else '[WARN] not found'}")
    click.echo(f"  rtl_eeprom  : {'[OK]' if info.rtl_eeprom_available else '[WARN] not found'}")
    if info.available and info.device_connected:
        click.echo("  device      : [OK] RTL-SDR Blog V3 connected")
    elif info.available:
        click.echo("  device      : [WARN] no RTL-SDR detected (plug in V3 and retry)")


# ── scan ───────────────────────────────────────────────────────


@main.command()
@click.option("--technology", "-t", help="Filter by technology (GSM, UMTS, LTE)")
@click.option("--profile", "profile_", default="full", type=click.Choice(["quick", "full"]),
              help="Scan profile (sweep time)")
@click.option("--json", "export_json_", is_flag=True, help="Export results to JSON file")
def scan(technology: str, profile_: str, export_json_: bool) -> None:
    """Run a full spectrum scan across all supported bands."""
    scheduler = ScanScheduler()
    if technology:
        jobs = scheduler.filter_by_technology(technology)
        if not jobs:
            click.echo(f"No jobs for technology '{technology}'")
            return
    else:
        jobs = scheduler.jobs

    backend = RTLPowerBackend()
    detector = CarrierPeakDetector()
    classifier = TechnologyClassifier()
    estimator = OperatorEstimator()
    parser = RTLPowerCSVParser()

    all_peaks: list[any] = []

    for job in jobs:
        sweep_time = 30.0 if profile_ == "quick" else 60.0
        config = ScanConfig(
            start_hz=job.start_hz,
            end_hz=job.end_hz,
            sweep_time=sweep_time,
        )
        click.echo(f"Scanning {job.technology} {job.band} ({job.start_hz/1e6:.0f}-{job.end_hz/1e6:.0f} MHz)...")
        try:
            stdout, _ = asyncio.run(backend.run(config))
        except FileNotFoundError as exc:
            click.echo(f"  [SKIP] {exc}")
            continue
        except RuntimeError as exc:
            click.echo(f"  [ERROR] {exc}")
            continue

        try:
            bins = parser.parse(stdout)
        except CSVParseError as exc:
            click.echo(f"  [PARSE ERROR] {exc}")
            continue

        raw_peaks = detector.detect(bins)
        for rp in raw_peaks:
            cls = classifier.classify(rp)
            if cls:
                tech, band = cls
                peak = build_carrier(rp, tech, band, estimator)
                all_peaks.append(peak)
                click.echo(f"  Found: {peak.frequency_mhz:.3f} MHz | {tech.value} | {band.value} | {peak.power_dbm:.1f} dBm")

    # Terminal output
    click.echo()
    click.echo(format_terminal(all_peaks))

    # JSON export
    if export_json_:
        result = ScanResult(timestamp=datetime.now(timezone.utc), carriers=all_peaks)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = Path("captures") / f"results_{ts}.json"
        from cellscan.output.json_export import export_json as export_json_fn
        export_json_fn(result, json_path)
        click.echo(f"\nResults exported to {json_path}")


# ── monitor ─────────────────────────────��──────────────────────


@main.command()
@click.option("--interval", "-i", default=60, help="Monitoring interval in seconds")
def monitor(interval: int) -> None:
    """Continuously monitor spectrum at regular intervals."""
    click.echo(f"Monitoring every {interval}s. Press Ctrl+C to stop.")
    try:
        while True:
            asyncio.run(scan.callback(technology=None, profile_="quick", export_json_=False))  # type: ignore[union-attr]
    except KeyboardInterrupt:
        click.echo("\nStopped.")


# ── replay ─────────────────────────────────────────────────────


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--json", "export_json_", is_flag=False, default=None,
              flag_value="capture.json", help="Export results to JSON file")
def replay(path: Path, export_json_: str | None) -> None:
    """Analyse a previously recorded rtl_power CSV file."""
    csv_path = Path(path)
    data = csv_path.read_bytes()

    parser = RTLPowerCSVParser()
    detector = CarrierPeakDetector()
    classifier = TechnologyClassifier()
    estimator = OperatorEstimator()

    try:
        bins = parser.parse(data)
    except CSVParseError as exc:
        click.echo(f"[PARSE ERROR] {exc}")
        return

    raw_peaks = detector.detect(bins)
    peaks: list[any] = []
    for rp in raw_peaks:
        cls = classifier.classify(rp)
        if cls:
            tech, band = cls
            peaks.append(build_carrier(rp, tech, band, estimator))

    click.echo(format_terminal(peaks))

    if export_json_:
        from cellscan.model.spectrum import ScanResult
        from cellscan.output.json_export import export_json as export_json_fn
        result = ScanResult(carriers=peaks)  # type: ignore[arg-type]
        export_json_fn(result, Path(export_json_))
        click.echo(f"\nResults exported to {export_json_}")
