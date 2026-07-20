"""Detection of RF carrier peaks from spectrum bins."""

from __future__ import annotations

from pydantic import BaseModel

from cellscan.model.spectrum import SpectrumBin


class RawPeak(BaseModel):
    """Intermediate peak result before classification."""

    frequency_hz: int
    power_dbm: float


class CarrierPeakDetector:
    """Detect carriers from rtl_power spectrum bins.

    Strategy:
    1. Compute noise floor as rolling median
    2. Identify bins above adaptive threshold (noise_floor + margin)
    3. Group contiguous qualifying bins
    4. Select highest-power bin from each group
    """

    def __init__(self, noise_margin_db: float = 10.0, min_bandwidth_hz: int = 10_000) -> None:
        self.noise_margin_db = noise_margin_db
        self.min_bandwidth_hz = min_bandwidth_hz

    def detect(self, bins: list[SpectrumBin], window_size: int = 50) -> list[RawPeak]:
        """Scan bins and return detected carrier peaks.

        Args:
            bins: sorted spectrum bins from rtl_power CSV parser.
            window_size: number of bins for rolling noise floor estimation.

        Returns:
            List of RawPeak (frequency + power only).
        """
        if not bins:
            return []

        noise_floor = self._estimate_noise_floor(bins, window_size)
        above_threshold = [b for b in bins if b.power_dbm > noise_floor + self.noise_margin_db]

        if not above_threshold:
            return []

        groups = self._group_contiguous(above_threshold)
        peaks: list[RawPeak] = []
        for group in groups:
            if len(group) < 2:
                continue
            center = max(group, key=lambda b: b.power_dbm)
            peaks.append(RawPeak(frequency_hz=center.frequency_hz, power_dbm=center.power_dbm))

        return peaks

    def _estimate_noise_floor(self, bins: list[SpectrumBin], window: int) -> float:
        """Estimate noise floor using rolling median of power values."""
        powers = [b.power_dbm for b in bins]
        half = window // 2
        medians: list[float] = []
        for i in range(len(powers)):
            start = max(0, i - half)
            end = min(len(powers), i + half)
            w = sorted(powers[start:end])
            mid = len(w) // 2
            medians.append(w[mid] if len(w) % 2 else (w[mid - 1] + w[mid]) / 2)
        if not medians:
            return min(powers) if powers else -100.0
        sorted_medians = sorted(medians)
        mid = len(sorted_medians) // 2
        return sorted_medians[mid]

    def _group_contiguous(self, bins: list[SpectrumBin]) -> list[list[SpectrumBin]]:
        """Group bins by contiguous frequency range."""
        groups: list[list[SpectrumBin]] = [[bins[0]]]
        for b in bins[1:]:
            prev = groups[-1][-1]
            span = abs(b.frequency_hz - prev.frequency_hz)
            if span <= self.min_bandwidth_hz:
                groups[-1].append(b)
            else:
                groups.append([b])
        return groups
