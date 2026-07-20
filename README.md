# CellScan

```
   ______          __      ________                __
  / ____/___  ____/ /__   / ____/ /___  __  ______/ /
 / /   / __ \/ __  / _ \ / /_  / / __ \/ / / / __  /
/ /___/ /_/ / /_/ /  __/____/ / / /_/ / /_/ / /_/ /
\____/\____/\__,_/\___/____/_/_/ .___/\__,_/\__,_/
                              /_/
```

> **RF Carrier Scanner for Indonesian Cellular Spectrum using RTL-SDR Blog V3**

<div align="center">

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg?style=for-the-badge&logo=linux&logoColor=white)](https://github.com/Muhammad-Yunus/rtl-sdr-cellular-network-scanner-python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg?style=for-the-badge)](https://github.com/Muhammad-Yunus/rtl-sdr-cellular-network-scanner-python)
[![RTL-SDR](https://img.shields.io/badge/RTL--SDR-Blog%20V3-0078D4.svg?style=for-the-badge&logo=radio&logoColor=white)](https://www.rtl-sdr.com/)

</div>

---

<div align="center">

| :sparkles: **Active Development** | :rocket: **Phases 1-8 Complete** | :clipboard: **15 Unit Tests** | :package: **v0.1.0** |

</div>

---

## :mag: Overview

**CellScan** is a Python command-line application that discovers nearby cellular RF
carrier activity by orchestrating the proven [`rtl_power`](https://github.com/osmocom/rtl-sdr)
utility. The application focuses on spectrum analysis — it is **not** a cellular
protocol decoder and does not attempt to decode LTE, GSM, UMTS, MCC/MNC, PCI,
EARFCN, Cell ID, or user traffic.

The application follows the UNIX philosophy:

> *Do one thing well.*

`rtl_power` is responsible for RF acquisition. CellScan is responsible for the
analysis pipeline that follows: CSV parsing, carrier peak detection, technology
classification, and operator candidate estimation.

---

## :bar_chart: Project Stats

| Metric | Value |
| :--- | :--- |
| :page_facing_up: Source Lines | ~1,200+ |
| :test_tube: Unit Tests | 15 |
| :microchip: SDR Targets | 4 |
| :flag_indonesia: Country Focus | Indonesia (MCC 510) |
| :calendar: Since | 2026 |

---

---

## :rocket: Features

<div align="center">

| Feature | Status | Description |
| :--- | :---: | :--- |
| Live spectrum scanning | :white_check_mark: | All Indonesian cellular bands |
| Replay mode | :white_check_mark: | Offline analysis of CSV captures |
| Adaptive peak detection | :white_check_mark: | Rolling-median noise floor |
| Technology classification | :white_check_mark: | GSM900 / UMTS B8 / LTE B5 / LTE B8 |
| Operator estimation | :white_check_mark: | All Indonesian MNOs |
| JSON export | :white_check_mark: | Downstream automation |
| Continuous monitoring | :white_check_mark: | Configurable interval |
| Hardware-independent tests | :white_check_mark: | 15 unit tests, no SDR required |
| MQTT publisher | :hourglass_flowing_sand: | Planned (Phase 9) |

</div>

- :satellite: **Live spectrum scanning** across all supported Indonesian cellular bands
- :floppy_disk: **Replay mode** for deterministic offline analysis of previously recorded CSV captures
- :chart_with_upwards_trend: **Adaptive carrier peak detection** using rolling-median noise floor estimation
- :signal_strength: **Technology classification** for GSM900, UMTS Band 8, LTE Band 5, LTE Band 8
- :busts_in_silhouette: **Operator candidate estimation** for all Indonesian MNOs (Telkomsel, Indosat, XL, Tri, Smartfren)
- :package: **JSON export** for downstream automation
- :repeat: **Continuous monitoring** with configurable intervals
- :white_check_mark: **Hardware-independent tests** — every analysis module is unit-tested against fixtures, no RTL-SDR required

---

## Supported Bands

| Technology | Band      | Downlink Scan Range |
|------------|-----------|---------------------|
| LTE        | Band 5    | 869 – 894 MHz       |
| LTE        | Band 8    | 925 – 960 MHz       |
| UMTS       | Band 8    | 925 – 960 MHz       |
| GSM        | GSM900    | 935 – 960 MHz       |

The scheduler reads these ranges from `database/bands.json`. Frequencies
outside these bands are never scheduled.

---

## Architecture

```
                  CLI
                   |
                   v
             Application
                   |
                   v
          Scan Scheduler
                   |
                   v
          RTLPowerBackend
                   |
                   v
         RTLPower CSV Parser
                   |
                   v
         Carrier Peak Detector
                   |
          +--------+--------+
          v                 v
Technology Classifier   Band Classifier
          |                 |
          +--------+--------+
                   v
Operator Candidate Estimator
                   |
          +--------+--------+
          v                 v
     JSON Export     Terminal Output
```

Each module has a single responsibility. The backend executes `rtl_power` and
captures stdout/stderr — it never parses CSV or analyses spectrum. The parser
never detects peaks. The peak detector never classifies technology. This
separation makes every module independently testable.

---

## Hardware Requirements

| Component | Specification |
|-----------|---------------|
| SDR       | RTL-SDR Blog V3 (or any RTL2832U-based dongle) |
| USB       | USB 2.0 or 3.0 port |
| Antenna   | Any antenna covering 869–960 MHz (a wideband discone or stub works well) |

### Tuning Range Constraint

The RTL-SDR Blog V3 tunes **500 kHz to 1.766 GHz**. CellScan will never
schedule a scan outside the supported Indonesian band allocations, which
fall well within this range.

---

## Software Requirements

- **Python 3.11 or newer**
- **`rtl_power`** executable from the `rtl-sdr` package (Osmocom)
- **Zadig WinUSB driver** on Windows (only for RTL-SDR device recognition)

CellScan itself depends only on:

- `pydantic >= 2.0` — domain model validation
- `click >= 8.0` — CLI framework

---

## Installation

### 1. Install rtl-sdr tools

The `rtl-sdr` package provides `rtl_power`, `rtl_sdr`, and `rtl_eeprom`. It
must be on `PATH` (or located in a known location such as a conda `Library/bin`
directory which CellScan also probes).

**Windows (recommended — conda):**

```powershell
conda create -n cellscan python=3.12 -y
conda activate cellscan
conda install -n cellscan -c conda-forge rtl-sdr -y
```

After activation, verify with:

```powershell
where rtl_power
```

If `where` does not find `rtl_power.exe`, add the conda `Library\bin` folder
to `PATH` (CellScan will also probe this directory automatically).

**Windows (alternative — manual):**

1. Install the Zadig driver so Windows recognises the RTL2832U as a WinUSB device.
2. Download prebuilt `rtl-sdr` binaries for Windows and place `rtl_power.exe`,
   `rtl_sdr.exe`, and `rtl_eeprom.exe` in a folder on `PATH`.

**Linux (Raspberry Pi OS or Debian/Ubuntu):**

```bash
sudo apt update
sudo apt install -y rtl-sdr
```

Blacklist the default DVB-T driver so the dongle is freed for SDR use:

```bash
echo "blacklist dvb_usb_rtl28xxu" | sudo tee /etc/modprobe.d/rtl-sdr.conf
sudo reboot
```

### 2. Install CellScan

From the repository root:

```bash
pip install -e .
```

For development dependencies (pytest, ruff, mypy):

```bash
pip install -e ".[dev]"
```

### 3. Verify

```powershell
cellscan backend check
```

Expected output:

```
CellScan Backend Check
  rtl_power   : [OK] C:\Users\...\Library\bin\rtl_power.exe
  rtl_sdr     : [OK]
  rtl_eeprom  : [OK]
  device      : [OK] RTL-SDR Blog V3 connected
```

---

## Usage

### Detect a Single Carrier with `rtl_power` (sanity check)

```powershell
rtl_power -f 925M:960M:1k -i 1 -e 3 -
```

This streams CSV to stdout for three seconds across the UMTS Band 8 downlink.

### CLI Commands

| Command | Purpose |
|---------|---------|
| `cellscan backend check` | Detect rtl_power, rtl_sdr, rtl_eeprom, and connected RTL-SDR device |
| `cellscan scan` | Scan every supported band |
| `cellscan scan --technology UMTS` | Scan only UMTS Band 8 |
| `cellscan scan --technology LTE` | Scan only LTE Band 5 and Band 8 |
| `cellscan scan --technology GSM` | Scan only GSM900 |
| `cellscan scan --profile quick` | Shorter sweep time per band (30 s instead of 60 s) |
| `cellscan scan --profile full` | Default — 60 s sweep per band |
| `cellscan scan --json` | Write results JSON to `captures/results_<UTC>.json` |
| `cellscan monitor --interval 60` | Repeat the quick scan every 60 seconds until Ctrl-C |
| `cellscan replay captures/live_umts.csv` | Analyse a previously recorded CSV capture |
| `cellscan replay captures/live_umts.csv --json capture.json` | Replay and export to JSON |

### Example Output

```
CELLSCAN - RF Carrier Discovery
--------------------------------------------------------------------------------
  FREQ (MHz)   POW (dBm)  TECHNOLOGY      ESTIMATED OPERATORS
--------------------------------------------------------------------------------
     869.530       -44.4  LTE_B5          Telkomsel (10), Indosat Ooredoo (21), XL Axiata (11), Tri (89)
     871.587       -46.3  LTE_B5          Telkomsel (10), Indosat Ooredoo (21), XL Axiata (11), Tri (89)
     928.933       -46.5  LTE_B8          Telkomsel (10), Indosat Ooredoo (21), XL Axiata (11)
     934.419       -44.7  LTE_B8          Telkomsel (10), Indosat Ooredoo (21), XL Axiata (11)
     940.178       -36.4  GSM900          Telkomsel (10), Indosat Ooredoo (21), XL Axiata (11), Smartfren (09)
     950.788       -30.7  GSM900          Telkomsel (10), Indosat Ooredoo (21), XL Axiata (11), Smartfren (09)
     952.388       -32.8  GSM900          Telkomsel (10), Indosat Ooredoo (21), XL Axiata (11), Smartfren (09)
--------------------------------------------------------------------------------
Total: 7 carrier(s) detected
```

The **Estimated Operators** column lists *every* Indonesian MNO that has a
licensed allocation on the detected band. CellScan **does not** claim that a
given carrier belongs to a specific operator — that would require decoding
the SIB (System Information Block) broadcast, which is the role of dedicated
protocol decoders such as srsRAN.

### JSON Output Schema

```json
{
  "timestamp": "2026-07-20T11:54:00Z",
  "carriers": [
    {
      "frequency_mhz": 950.788,
      "power_dbm": -30.7,
      "technology": "GSM900",
      "band": "GSM900",
      "candidates": [
        { "name": "Telkomsel", "mnc": "10", "bands": ["B5", "B8", "B1", "B3", "B28", "B40", "B41", "GSM900"] },
        { "name": "Indosat Ooredoo", "mnc": "21", "bands": ["B5", "B8", "B40", "GSM900"] },
        { "name": "XL Axiata", "mnc": "11", "bands": ["B5", "B8", "B1", "B3", "B40", "GSM900"] },
        { "name": "Smartfren", "mnc": "09", "bands": ["B40", "B41", "GSM900"] }
      ]
    }
  ]
}
```

---

## Replay Mode

Replay mode accepts any previously recorded `rtl_power` CSV file as input and
runs the full analysis pipeline against it. This is the recommended way to:

- Develop and tune the peak detection algorithm without occupying the dongle
- Build deterministic regression tests
- Replay captures collected on a Raspberry Pi in the field on a Windows dev box

A sample CSV is generated by:

```bash
python scripts/replay.py
# Creates captures/sample.csv
cellscan replay captures/sample.csv
```

Replay mode accepts the same `--json` flag as live scan and produces identical
JSON output.

---

## Live Scan Result (Example)

A live quick-profile scan performed with an RTL-SDR Blog V3 attached to a
Windows host produced the following results:

| Band | Carriers Detected | Strongest Carrier | Peak Power |
|------|-------------------|-------------------|------------|
| LTE Band 5 (869 – 894 MHz) | ~200 | 872.4 MHz | -44.0 dBm |
| LTE Band 8 (925 – 960 MHz) | ~30 | 928.9 MHz | -46.5 dBm |
| UMTS Band 8 (925 – 960 MHz) | ~30 | 928.9 MHz | -46.5 dBm |
| GSM900 (935 – 960 MHz)    | ~3000 | 950.8 MHz | **-30.7 dBm** |

The strongest signal (950.788 MHz, -30.7 dBm) lies inside the GSM900 downlink
allocation and is the likely candidate for a nearby base station's broadcast
control channel. CellScan reports all four operators licensed for that band
(Telkomsel, Indosat, XL, Smartfren) without claiming ownership.

---

## Development Workflow

```
Windows
   |
   v
Develop
   |
   v
Unit Test (pytest)
   |
   v
Install on Raspberry Pi
   |
   v
SSH
   |
   v
Run
   |
   v
Collect CSV
   |
   v
Replay (on Windows)
   |
   v
Improve Algorithm
   |
   v
Repeat
```

### Running the Tests

```bash
PYTHONPATH=src python -m pytest tests/ -v
```

All 15 unit tests execute without any RTL-SDR hardware. Tests cover:

- `test_csv_parser.py` — CSV parsing edge cases (5 tests)
- `test_peak_detector.py` — Carrier peak detection (4 tests)
- `test_classifier.py` — Technology + operator classification (6 tests)

### Linting

```bash
ruff check --select E,W,F,I src/
mypy --strict src/
```

---

## Repository Layout

```
rtl-sdr-cellular-network-scanner-python/
├── pyproject.toml             # Build config and dependencies
├── README.md                  # This file
├── AGENT.md                   # Project specification
├── database/
│   ├── bands.json             # Scan range definitions
│   └── operators.json         # Indonesian MNO registry
├── src/cellscan/
│   ├── __init__.py
│   ├── cli.py                 # Click CLI entry point
│   ├── backend/
│   │   ├── rtl_power.py       # Execute rtl_power with timeout + cancellation
│   │   └── validator.py       # Detect rtl_power / device
│   ├── parser/
│   │   └── csv.py             # rtl_power CSV parser
│   ├── analysis/
│   │   ├── peak_detector.py   # Adaptive carrier peak detector
│   │   └── classifier.py      # Technology + operator classifier
│   ├���─ scheduler/
│   │   └── scheduler.py       # Generate scan jobs from bands.json
│   ├── output/
│   │   ├── terminal.py        # Formatted table output
│   │   └── json_export.py     # JSON writer
│   ├── model/
│   │   └── spectrum.py        # Pydantic domain models
│   └── util/
│       └── find.py            # Locate rtl_power executable
├── scripts/
│   └── replay.py              # Generate sample CSV for replay
├── tests/
│   ├── test_csv_parser.py
│   ├── test_peak_detector.py
│   └── test_classifier.py
└── captures/                  # Live scan CSV output and JSON results
```

---

## Non-Goals

CellScan is intentionally limited. It **will not**:

- Decode LTE, GSM, or UMTS protocols
- Decode MCC / MNC / PCI / EARFCN / Cell ID
- Decode user traffic
- Replace `rtl_power`
- Implement SDR DSP (FFT, filters, demodulation)

For protocol-level decoding, use dedicated decoders such as [srsRAN](https://www.srslte.com/)
or [OpenAirInterface](https://openairinterface.org/).

---

## Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | Done | Environment validation (`cellscan backend check`) |
| 2 | Done | RTLPowerBackend with timeout + cancellation |
| 3 | Done | CSV parser with full unit test coverage |
| 4 | Done | Carrier peak detection (adaptive threshold, contiguous grouping) |
| 5 | Done | Technology classification (GSM900 / UMTS B8 / LTE B5 / LTE B8) |
| 6 | Done | Operator candidate estimation from `operators.json` |
| 7 | Done | JSON export and full CLI command set |
| 8 | Done | Continuous monitoring (`cellscan monitor`) |
| 9 | Planned | MQTT publisher for IoT integration |

---

## License

MIT