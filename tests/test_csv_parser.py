"""Unit tests for rtl_power CSV parser."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cellscan.parser.csv import CSVParseError, RTLPowerCSVParser


def _row(date: str, time: str, freq: int, dbm: float) -> str:
    return f"{date},{time},{freq},{freq + 1000},1000,1,mean,fine,{dbm}"


HEADER = "date,time,start_freq,end_freq,step_width,n_int,mode,detail,dbm_mean"


def test_parse_minimal_csv():
    parser = RTLPowerCSVParser()
    text = "\n".join([HEADER, _row("2026-07-20", "10:00:00", 869_000_000, -95.0)])
    bins = parser.parse_text(text)
    assert len(bins) == 1
    assert bins[0].frequency_hz == 869_000_000
    assert bins[0].power_dbm == -95.0
    assert bins[0].timestamp == datetime(2026, 7, 20, 10, 0, 0, tzinfo=timezone.utc)


def test_parse_multiple_rows():
    parser = RTLPowerCSVParser()
    rows = [HEADER] + [_row("2026-07-20", "10:00:00", f, -90.0 + i)
                       for i, f in enumerate([869_000_000, 870_000_000, 871_000_000])]
    bins = parser.parse_text("\n".join(rows))
    assert len(bins) == 3
    assert [b.frequency_hz for b in bins] == [869_000_000, 870_000_000, 871_000_000]
    assert [b.power_dbm for b in bins] == [-90.0, -89.0, -88.0]


def test_parse_skips_blank_lines():
    parser = RTLPowerCSVParser()
    text = "\n".join([HEADER, "", _row("2026-07-20", "10:00:00", 869_000_000, -95.0), "  "])
    bins = parser.parse_text(text)
    assert len(bins) == 1


def test_parse_raises_on_invalid_format():
    parser = RTLPowerCSVParser()
    text = "\n".join([HEADER, "this,is,garbage,data,row,no,valid,fields,here"])
    with pytest.raises(CSVParseError):
        parser.parse_text(text)


def test_parse_bytes_input():
    parser = RTLPowerCSVParser()
    text = "\n".join([HEADER, _row("2026-07-20", "10:00:00", 869_000_000, -95.0)])
    bins = parser.parse(text.encode("utf-8"))
    assert len(bins) == 1
    assert bins[0].power_dbm == -95.0