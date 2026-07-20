"""Technology and band classification for detected peaks."""

from __future__ import annotations

import json
from pathlib import Path

from cellscan.analysis.peak_detector import RawPeak
from cellscan.model.spectrum import Band, CarrierPeak, CandidateOperator, Technology


class TechnologyClassifier:
    """Classify a RawPeak into a Technology + Band."""

    # Frequency ranges in Hz
    FREQUENCY_RANGES: dict[Technology, tuple[int, int]] = {
        Technology.LTE_B5: (869_000_000, 894_000_000),
        Technology.LTE_B8: (925_000_000, 960_000_000),
        Technology.UMTS_B8: (925_000_000, 960_000_000),
        Technology.GSM900: (935_000_000, 960_000_000),
    }

    BAND_MAP: dict[Technology, Band] = {
        Technology.LTE_B5: Band.BAND_5,
        Technology.LTE_B8: Band.BAND_8,
        Technology.UMTS_B8: Band.BAND_8,
        Technology.GSM900: Band.GSM900,
    }

    def classify(self, peak: RawPeak) -> tuple[Technology, Band] | None:
        """Match peak frequency to a supported technology.

        Priority: more specific matches first.
        GSM900 is a subset of LTE_B8/UMTS_B8 band but starts at 935 MHz.
        """
        freq = peak.frequency_hz
        for tech in (Technology.LTE_B5, Technology.LTE_B8, Technology.UMTS_B8, Technology.GSM900):
            lo, hi = self.FREQUENCY_RANGES[tech]
            if lo <= freq <= hi:
                # GSM900 range overlaps with LTE/UMTS B8; prefer GSM900 when >= 935 MHz
                if tech != Technology.GSM900 and 935_000_000 <= freq <= 960_000_000:
                    # Both GSM900 and LTE/UMTS_B8 match — GSM900 wins in overlap zone
                    # because GSM carriers are narrower and more likely to show as peaks
                    continue
                return tech, self.BAND_MAP[tech]
        return None


class OperatorEstimator:
    """Given a technology/band, return candidate operators for Indonesia."""

    def __init__(self, db_path: Path | None = None) -> None:
        self._operators: list[CandidateOperator] = []
        if db_path is None:
            db_path = Path(__file__).parents[3] / "database" / "operators.json"
        self._load_operators(db_path)

    def _load_operators(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        indonesia = data.get("Indonesia", {})
        for op in indonesia.get("operators", []):
            self._operators.append(
                CandidateOperator(name=op["name"], mnc=op.get("mnc", ""), bands=op["bands"])
            )

    def estimate(self, technology: Technology, band: Band) -> list[CandidateOperator]:
        """Return all operators that support this band."""
        band_str = band.value
        result: list[CandidateOperator] = []
        for op in self._operators:
            if band_str in op.bands:
                result.append(op)
        return result


def build_carrier(peak: RawPeak, tech: Technology, band: Band, estim: OperatorEstimator) -> CarrierPeak:
    """Construct a full CarrierPeak from raw data."""
    return CarrierPeak(
        frequency_mhz=round(peak.frequency_hz / 1_000_000, 3),
        power_dbm=round(peak.power_dbm, 2),
        technology=tech,
        band=band,
        candidates=estim.estimate(tech, band),
    )
