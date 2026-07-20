# AGENT.md

# CellScan

**RF Carrier Scanner for Indonesian Cellular Spectrum using RTL-SDR Blog V3**

---

# Mission

Build a production-quality command-line application that discovers nearby cellular RF carrier activity using **RTL-SDR Blog V3** by orchestrating the proven `rtl_power` utility.

This project intentionally avoids implementing SDR DSP algorithms.

Instead, the application focuses on:

- orchestrating rtl_power
- parsing spectrum data
- detecting RF carrier peaks
- classifying supported cellular technologies
- estimating possible operators
- exporting structured results
- providing continuous monitoring

The application is an RF spectrum analysis tool.

It is **NOT** a cellular protocol decoder.

---

# Development Philosophy

This project intentionally avoids reinventing mature SDR software.

`rtl_power` is responsible for RF acquisition.

CellScan is responsible for analysis.

Follow the UNIX philosophy:

> Do one thing well.

Responsibilities of CellScan

- execute rtl_power
- parse CSV output
- analyze RF spectrum
- detect carrier peaks
- classify technologies
- estimate candidate operators
- export structured data

Never implement

- SDR drivers
- FFT
- DSP
- protocol decoding

Prefer composing mature software instead of replacing it.

---

# Target Platform

## Development Host

- Windows 11
- Visual Studio Code
- Python 3.11+
- venv / uv

Python 3.11+

## Runtime Target

- Raspberry Pi 3B
- Raspberry Pi OS (64-bit)
- RTL-SDR Blog V3

---

# Build Strategy

The project is a Python application.

No compilation is required.

Dependencies are managed via
- `pyproject.toml`
- `uv` (recommended) or `pip`

Supported platforms

- Windows 11 x64
- Linux x64
- Raspberry Pi ARMv7 (32-bit)
- Raspberry Pi ARM64 (64-bit)

Package distribution

- `pyproject.toml`
- `uv` or `pip install .`

---

# Hardware Constraints

Receiver

RTL-SDR Blog V3

Practical tuning range

```
500 kHz – 1.766 GHz
```

The application SHALL NEVER schedule scans outside this range.

---

# Geographic Scope

Target country

Indonesia

Frequency allocations shall follow Indonesian spectrum allocation.

Support for other countries must be implemented through configuration files only.

---

# Supported Technologies

Supported

- GSM900
- UMTS Band 8
- LTE Band 5
- LTE Band 8

Unsupported

- GSM1800
- UMTS Band 1
- LTE Band 1
- LTE Band 3
- LTE Band 28
- LTE Band 40
- LTE Band 41
- 5G NR
- WiMAX
- CDMA2000

The scheduler SHALL NEVER generate scan jobs for unsupported technologies.

---

# Supported Scan Bands

| Technology | Band | Downlink Scan Range |
|------------|------|---------------------|
| LTE | Band 5 | 869–894 MHz |
| LTE | Band 8 | 925–960 MHz |
| UMTS | Band 8 | 925–960 MHz |
| GSM | GSM900 | 935–960 MHz |

These are the only supported scan ranges.

---

# Non Goals

This project SHALL NOT

- decode LTE
- decode GSM
- decode UMTS
- decode MCC
- decode MNC
- decode PCI
- decode EARFCN
- decode Cell ID
- decode user traffic
- replace rtl_power
- implement SDR DSP

Those features belong to dedicated protocol decoders such as srsRAN.

---

# Overall Architecture

```
                  CLI
                   │
                   ▼
             Application
                   │
                   ▼
          Scan Scheduler
                   │
                   ▼
          RTLPowerBackend
                   │
                   ▼
         RTLPower CSV Parser
                   │
                   ▼
         Carrier Peak Detector
                   │
          ┌────────┴────────┐
          ▼                 ▼
Technology Classifier   Band Classifier
          │                 │
          └────────┬────────┘
                   ▼
Operator Candidate Estimator
                   │
          ┌────────┴────────┐
          ▼                 ▼
     JSON Export     Terminal Output
```

---

# Repository Layout

```
cellscan/
├── pyproject.toml
├── README.md
├── AGENT.md
├── database/
│   ├── bands.json
│   └── operators.json
├── config/
├── captures/
├── scripts/
│   └── replay.py
├── src/
│   └── cellscan/
│       ├── __init__.py
│       ├── cli.py
│       ├── app.py
│       ├── backend/
│       ├── scheduler/
│       ├── parser/
│       ├── analysis/
│       ├── output/
│       ├── config/
│       ├── model/
│       └── util/
└── tests/
    ├── test_csv_parser.py
    ├── test_peak_detector.py
    └── test_classifier.py
```

---

# Backend

Current backend

```
RTLPowerBackend
```

Responsibilities

- detect rtl_power
- verify rtl_power version
- build command
- execute rtl_power
- timeout handling
- cancellation
- capture stdout
- capture stderr

Backend SHALL NOT

- parse CSV
- classify technologies
- estimate operators
- analyze RF spectrum

Future backends may be added later.

Do not design abstractions until a second backend exists.

---

# Scan Scheduler

The scheduler SHALL create jobs from `bands.json`.

Never hardcode frequency ranges.

Example

```
Job 1

LTE Band 5
↓
rtl_power
↓
CSV

--------------------------

Job 2

LTE Band 8
↓
rtl_power
↓
CSV

--------------------------

Job 3

UMTS Band 8
↓
rtl_power
↓
CSV

--------------------------

Job 4

GSM900
↓
rtl_power
↓
CSV
```

---

# Analysis Pipeline

```
rtl_power
↓
CSV
↓
CSV Parser
↓
Spectrum Bins
↓
Carrier Peak Detection
↓
Technology Classification
↓
Band Classification
↓
Operator Candidate Estimation
↓
JSON / Terminal
```

---

# Domain Model

## SpectrumBin

Represents one FFT bin produced by rtl_power.

Contains

- frequency
- power

---

## CarrierPeak

Represents one RF carrier.

Contains

- frequency
- power
- technology
- band
- candidate operators

Example

```python
class CarrierPeak(BaseModel):
    frequency_mhz: float
    power_dbm: float
    technology: Technology
    band: Band
    candidates: list[CandidateOperator]
```

---

## CandidateOperator

Represents one operator that may use the detected band.

Contains

- operator name
- supported bands

No confidence score shall be generated.

---

# Operator Candidate Estimation

CellScan SHALL NEVER claim that a carrier belongs to a specific operator.

Instead it SHALL return all operators known to use that band.

Example

```
947.5 MHz
↓
LTE Band 8
↓
Possible Operators

- Telkomsel
- Indosat
- XL
```

---

# Configuration

## bands.json

```json
[
    {
        "technology": "LTE",
        "band": "B5",
        "start": 869000000,
        "end": 894000000,
        "enabled": true
    },
    {
        "technology": "LTE",
        "band": "B8",
        "start": 925000000,
        "end": 960000000,
        "enabled": true
    },
    {
        "technology": "UMTS",
        "band": "B8",
        "start": 925000000,
        "end": 960000000,
        "enabled": true
    },
    {
        "technology": "GSM",
        "band": "GSM900",
        "start": 935000000,
        "end": 960000000,
        "enabled": true
    }
]
```

---

# Replay Mode

Replay mode SHALL be a first-class feature.

Every analysis module must accept

- live rtl_power output

or

- previously recorded CSV captures

This enables

- deterministic testing
- offline development
- regression testing
- CI execution
- algorithm benchmarking

without RTL-SDR hardware.

Example

```
cellscan replay captures/sample.csv
```

---

# CLI

```
cellscan scan
```

```
cellscan monitor
```

```
cellscan replay captures/sample.csv
```

```
cellscan scan --technology gsm
```

```
cellscan scan --technology umts
```

```
cellscan scan --technology lte
```

```
cellscan scan --profile quick
```

```
cellscan scan --profile full
```

```
cellscan scan --json
```

```
cellscan backend check
```

---

# Development Workflow

```
Windows

↓

Develop

↓

Unit Test (pytest)

↓

Install on Raspberry Pi

↓

SSH

↓

Run

↓

Collect CSV

↓

Replay

↓

Improve Algorithm

↓

Repeat
```

---

# Testing Strategy

Unit Tests (pytest)

- CSV Parser
- Peak Detector
- Technology Classifier
- Band Classifier
- Operator Candidate Estimator

All unit tests SHALL execute without RTL-SDR hardware.

Replay Mode SHALL be used whenever possible.

Hardware tests are reserved for

- RTLPowerBackend
- Scheduler
- Continuous monitoring

---

# Coding Guidelines

Follow

- PEP 8
- Type hints everywhere
- `pydantic` models for domain objects
- Functional core, imperative edges
- Composition over inheritance

Prefer

- `pathlib` for file paths
- `datetime` / `zoneinfo` for time
- `dataclasses` / `BaseModel` for value objects
- `logging` instead of print

Avoid

- global mutable state
- bare `except:` clauses
- `eval` / `exec`
- regex for structured CSV parsing
- hardcoded frequency allocations
- business logic inside CLI entry point

Always parse structured CSV.

Never parse terminal output.

---

# Development Roadmap

## Phase 1

Environment Validation

- detect rtl_power
- detect RTL-SDR
- verify runtime environment

---

## Phase 2

RTLPowerBackend

- execute rtl_power
- timeout
- cancellation
- stdout capture

---

## Phase 3

CSV Parser

- parse rtl_power CSV
- unit tests

---

## Phase 4

Carrier Peak Detection

- adaptive threshold
- local maxima
- duplicate suppression

---

## Phase 5

Technology Classification

- GSM900
- UMTS Band 8
- LTE Band 5
- LTE Band 8

---

## Phase 6

Operator Candidate Estimation

- operator database
- candidate lookup

---

## Phase 7

JSON Export

---

## Phase 8

Continuous Monitoring

---

## Phase 9

MQTT Publisher

---

# Definition of Done

The project is complete when

- rtl_power is automatically detected
- supported scan jobs execute successfully
- CSV parsing is deterministic
- carrier peak detection passes all unit tests
- supported technologies are correctly classified
- candidate operators are generated from Indonesian spectrum allocation
- replay mode reproduces identical analysis results
- JSON export validates against schema
- CLI runs continuously for at least 24 hours without memory leaks
- cross-compilation succeeds for Raspberry Pi ARM targets
- project builds warning-free using

```shell
ruff check --select E,W,F,I
mypy --strict src/
```

- unit tests require no RTL-SDR hardware
- integration tests pass on Raspberry Pi 3B using RTL-SDR Blog V3
```