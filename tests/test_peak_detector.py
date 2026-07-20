"""Unit tests for carrier peak detector."""

from __future__ import annotations

from datetime import datetime, timezone

from cellscan.analysis.peak_detector import CarrierPeakDetector
from cellscan.model.spectrum import SpectrumBin


def _bin(freq_hz: int, power: float, ts: datetime | None = None) -> SpectrumBin:
    return SpectrumBin(timestamp=ts or datetime(2026, 7, 20, 10, 0, 0, tzinfo=timezone.utc),
                       frequency_hz=freq_hz, power_dbm=power)


def test_no_bins_returns_empty():
    detector = CarrierPeakDetector()
    assert detector.detect([]) == []


def test_noise_below_threshold_returns_empty():
    detector = CarrierPeakDetector(noise_margin_db=10.0)
    bins = [_bin(f, -100.0) for f in range(869_000_000, 870_001_000, 1_000)]
    peaks = detector.detect(bins)
    assert peaks == []


def test_detects_single_carrier():
    detector = CarrierPeakDetector(noise_margin_db=10.0, min_bandwidth_hz=5_000)
    # Background noise at -100 dBm, single carrier at a single freq
    bins = []
    for f in range(869_000_000, 870_000_000, 1_000):
        bins.append(_bin(f, -100.0))
    # Insert a short-carrier peak (at least 2 bins per min_bandwidth grouping)
    bins.append(_bin(869_500_000, -65.0))
    bins.append(_bin(869_501_000, -65.0))
    peaks = detector.detect(bins)
    assert len(peaks) == 1
    assert peaks[0].frequency_hz in (869_500_000, 869_501_000)
    assert peaks[0].power_dbm == -65.0


def test_detects_multiple_carriers():
    detector = CarrierPeakDetector(noise_margin_db=10.0, min_bandwidth_hz=5_000)
    bins = [_bin(f, -100.0) for f in range(869_000_000, 872_000_000, 1_000)]
    # Two distinct carrier groups far apart
    for f in (869_500_000, 869_501_000):
        bins.append(_bin(f, -65.0))
    for f in (871_500_000, 871_501_000):
        bins.append(_bin(f, -60.0))
    peaks = detector.detect(bins)
    assert len(peaks) == 2
