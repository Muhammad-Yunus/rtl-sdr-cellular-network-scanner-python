"""Domain models for CellScan."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from enum import Enum


class Technology(str, Enum):
    GSM900 = "GSM900"
    UMTS_B8 = "UMTS_B8"
    LTE_B5 = "LTE_B5"
    LTE_B8 = "LTE_B8"


class Band(str, Enum):
    BAND_5 = "B5"
    BAND_8 = "B8"
    GSM900 = "GSM900"


class CandidateOperator(BaseModel):
    name: str
    mnc: str = ""
    bands: list[str]


class CarrierPeak(BaseModel):
    frequency_mhz: float = Field(..., gt=0)
    power_dbm: float
    technology: Technology
    band: Band
    candidates: list[CandidateOperator] = Field(default_factory=list)


class SpectrumBin(BaseModel):
    """Represents one FFT bin produced by rtl_power."""

    timestamp: datetime
    frequency_hz: int
    power_dbm: float


class ScanJob(BaseModel):
    """A scan job definition from bands.json."""

    technology: str
    band: str
    start_hz: int = Field(..., gt=0)
    end_hz: int = Field(..., gt=0)
    enabled: bool = True


class ScanResult(BaseModel):
    """Complete result of a scan."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    carriers: list[CarrierPeak] = Field(default_factory=list)
