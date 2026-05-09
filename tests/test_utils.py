"""Tests for solarpipeline utility functions."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from solarpipeline import normalize_district, compute_cuf_theoretical
from solarpipeline.utils import safe_read_csv


# ── normalize_district ─────────────────────────────────────────

def test_normalize_district_lowercase():
    assert normalize_district("Hyderabad") == "hyderabad"


def test_normalize_district_strip():
    assert normalize_district("  Rangareddy  ") == "rangareddy"


def test_normalize_district_en_dash():
    assert normalize_district("Medchal\u2013Malkajgiri") == "medchal-malkajgiri"


def test_normalize_district_em_dash():
    assert normalize_district("Alluri\u2014Sitharama") == "alluri-sitharama"


def test_normalize_district_nan():
    assert normalize_district(float("nan")) is None


def test_normalize_district_none():
    assert normalize_district(None) is None


# ── compute_cuf_theoretical ────────────────────────────────────

def test_cuf_moderate_conditions():
    # GHI=5.5, temp=28 -> reasonable CUF
    cuf = compute_cuf_theoretical(5.5, 28.0)
    assert 0.10 < cuf < 0.25


def test_cuf_low_temp():
    # Low temp should give slightly higher PR
    cuf = compute_cuf_theoretical(5.0, 15.0)
    assert 0.12 < cuf < 0.25


def test_cuf_high_temp_penalty():
    # High temp reduces PR
    cuf_hot = compute_cuf_theoretical(6.0, 45.0)
    cuf_cool = compute_cuf_theoretical(6.0, 20.0)
    assert cuf_hot < cuf_cool


def test_cuf_zero_ghi():
    assert compute_cuf_theoretical(0.0, 25.0) == 0.0


def test_cuf_reproducible():
    v1 = compute_cuf_theoretical(5.2, 27.5)
    v2 = compute_cuf_theoretical(5.2, 27.5)
    assert v1 == v2


# ── safe_read_csv ──────────────────────────────────────────────

def _fake_logger():
    import logging
    return logging.getLogger("test")


def test_safe_read_csv_missing_file():
    logger = _fake_logger()
    result = safe_read_csv(Path("/nonexistent/file.csv"), "test", ["col1"], logger)
    assert result is None


def test_safe_read_csv_empty_file():
    logger = _fake_logger()
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        f.write("")  # Just write header
        p = Path(f.name)
    # Empty file (header-only, no data)
    result = safe_read_csv(p, "empty", ["col1"], logger)
    assert result is None
    p.unlink(missing_ok=True)


def test_safe_read_csv_missing_columns():
    logger = _fake_logger()
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        f.write("a,b\n1,2\n")
        p = Path(f.name)
    result = safe_read_csv(p, "test", ["a", "b", "c"], logger)
    assert result is None
    p.unlink(missing_ok=True)


def test_safe_read_csv_ok():
    logger = _fake_logger()
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        f.write("a,b\n1,2\n3,4\n")
        p = Path(f.name)
    result = safe_read_csv(p, "test", ["a", "b"], logger)
    assert result is not None
    assert len(result) == 2
    p.unlink(missing_ok=True)
