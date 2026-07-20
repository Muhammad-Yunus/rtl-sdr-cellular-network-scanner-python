"""Unit tests for technology classifier and operator estimator."""

from __future__ import annotations

from pathlib import Path

from cellscan.analysis.classifier import TechnologyClassifier, OperatorEstimator
from cellscan.analysis.peak_detector import RawPeak
from cellscan.model.spectrum import Band, Technology


def test_lte_b5_detection():
    classifier = TechnologyClassifier()
    peak = RawPeak(frequency_hz=875_000_000, power_dbm=-70.0)
    cls = classifier.classify(peak)
    assert cls is not None
    assert cls[0] == Technology.LTE_B5
    assert cls[1] == Band.BAND_5


def test_lte_b8_detection():
    classifier = TechnologyClassifier()
    # 930 MHz is in LTE B8 (925-960) but below GSM900 (935-960)
    peak = RawPeak(frequency_hz=930_000_000, power_dbm=-70.0)
    cls = classifier.classify(peak)
    assert cls is not None
    assert cls[0] == Technology.LTE_B8
    assert cls[1] == Band.BAND_8


def test_umts_b8_detection():
    classifier = TechnologyClassifier()
    peak = RawPeak(frequency_hz=945_000_000, power_dbm=-70.0)
    cls = classifier.classify(peak)
    assert cls is not None


def test_unknown_frequency_returns_none():
    classifier = TechnologyClassifier()
    peak = RawPeak(frequency_hz=1_500_000_000, power_dbm=-70.0)
    cls = classifier.classify(peak)
    assert cls is None


def test_operator_estimator_returns_candidates():
    estim = OperatorEstimator()
    candidates = estim.estimate(Technology.LTE_B5, Band.BAND_5)
    assert len(candidates) > 0
    names = [c.name for c in candidates]
    assert "Telkomsel" in names
    assert "Indosat Ooredoo" in names


def test_operator_estimator_filters_by_band():
    estim = OperatorEstimator()
    from cellscan.model.spectrum import CandidateOperator
    candidates = estim.estimate(Technology.LTE_B5, Band.BAND_5)
    for c in candidates:
        assert isinstance(c, CandidateOperator)
        assert "B5" in c.bands
