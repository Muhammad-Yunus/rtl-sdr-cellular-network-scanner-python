"""Parser for rtl_power CSV output.

rtl_power CSV columns:
    date, time, Hz low, Hz high, Hz step, samples, dbm_1, dbm_2, ...

Each dbm_*, dbm_2, ... corresponds to a frequency point:
    freq_i = Hz_low + i * Hz_step  for i in range(number_of_dbm_columns)
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

from cellscan.model.spectrum import SpectrumBin


class CSVParseError(Exception):
    """Raised when rtl_power CSV cannot be parsed."""


class RTLPowerCSVParser:
    """Parse structured CSV output from rtl_power."""

    def parse(self, data: bytes) -> list[SpectrumBin]:
        """Parse rtl_power CSV bytes into a list of SpectrumBin."""
        text = data.decode("utf-8", errors="replace")
        return self.parse_text(text)

    def parse_text(self, text: str) -> list[SpectrumBin]:
        """Parse rtl_power CSV text into a list of SpectrumBin."""
        reader = csv.reader(io.StringIO(text))
        bins: list[SpectrumBin] = []
        header = None

        for row in reader:
            stripped = [cell.strip() for cell in row if cell.strip()]
            if not stripped:
                continue

            if header is None:
                header = stripped
                continue

            try:
                date_str = stripped[0]
                time_str = stripped[1]
                ts = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=timezone.utc
                )
                freq_start = int(float(stripped[2]))
                step = int(float(stripped[4]))
                num_values = len(stripped) - 6  # subtract 6 fixed columns

                for i in range(num_values):
                    bins.append(
                        SpectrumBin(
                            timestamp=ts,
                            frequency_hz=freq_start + i * step,
                            power_dbm=float(stripped[6 + i]),
                        )
                    )
            except (IndexError, ValueError) as exc:
                raise CSVParseError(f"Failed to parse row: {stripped}") from exc

        return bins
