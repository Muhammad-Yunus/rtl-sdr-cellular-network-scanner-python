"""Generate sample rtl_power CSV for replay testing."""

from __future__ import annotations

import csv
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def generate_sample(output: Path, start_freq: int = 869_000_000,
                    end_freq: int = 894_000_000, steps: int = 25,
                    duration_minutes: int = 10, step_hz: int = 1_000) -> None:
    """Write a realistic-looking rtl_power CSV file."""
    output.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc)

    freqs = list(range(start_freq, end_freq, (end_freq - start_freq) // steps))

    with open(output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "time", "start_freq", "end_freq", "step_width",
                         "n_int", "mode", "detail", "dbm_mean"])

        current = ts
        for minute in range(duration_minutes):
            date_str = current.strftime("%Y-%m-%d")
            time_str = current.strftime("%H:%M:%S")
            row_freqs = freqs[:steps]  # sample subset for speed
            for freq in row_freqs:
                base_noise = -95.0
                # Add a fake LTE B5 carrier at 875 MHz
                if abs(freq - 875_000_000) < step_hz * 5:
                    base_noise += 30 + random.uniform(-2, 2)
                # Add a fake LTE B8 carrier at 940 MHz (if in range)
                if start_freq <= 940_000_000 <= end_freq and abs(freq - 940_000_000) < step_hz * 5:
                    base_noise += 25 + random.uniform(-2, 2)
                writer.writerow([date_str, time_str, freq, freq + step_hz, step_hz, 1,
                                 "mean", "fine", f"{base_noise:.1f}"])
            current += timedelta(minutes=1)


if __name__ == "__main__":
    out = Path("captures") / "sample.csv"
    generate_sample(out)
    print(f"Generated {out}")
