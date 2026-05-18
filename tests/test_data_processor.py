"""
Tests for data processor: file reading, column mapping, value normalization.
"""

import pandas as pd
import pytest

from backend.data_processor import (
    apply_mappings,
    get_sample_data,
    normalize_category,
    normalize_fuel_type,
    parse_date,
    parse_float,
    process_dataframe,
)
from backend.schemas import ColumnMapping

# ─── parse_date ───────────────────────────────────────────────────────────────


def test_parse_date_iso():
    result = parse_date("2024-01-15")
    assert result is not None
    assert result.year == 2024
    assert result.month == 1


def test_parse_date_turkish_format():
    result = parse_date("15/01/2024")
    assert result is not None
    assert result.day == 15


def test_parse_date_none():
    assert parse_date(None) is None
    assert parse_date("") is None
    assert parse_date("nan") is None


# ─── parse_float ──────────────────────────────────────────────────────────────


def test_parse_float_standard():
    assert parse_float("123.45") == pytest.approx(123.45)


def test_parse_float_turkish_comma():
    # Turkish: period = thousands separator, comma = decimal
    assert parse_float("1.234,56") == pytest.approx(1234.56)


def test_parse_float_with_currency():
    assert parse_float("₺1.234") is not None


def test_parse_float_none():
    assert parse_float(None) is None
    assert parse_float("") is None
    assert parse_float("abc") is None


# ─── normalize_fuel_type ──────────────────────────────────────────────────────


def test_normalize_fuel_type_turkish():
    assert normalize_fuel_type("Mazot") == "diesel"
    assert normalize_fuel_type("motorin") == "diesel"
    assert normalize_fuel_type("Benzin") == "gasoline"
    assert normalize_fuel_type("LPG") == "lpg"


def test_normalize_fuel_type_english():
    assert normalize_fuel_type("diesel") == "diesel"
    assert normalize_fuel_type("gasoline") == "gasoline"
    assert normalize_fuel_type("electricity") == "electricity"


def test_normalize_fuel_type_unknown():
    assert normalize_fuel_type("hydrogen") == "other"


# ─── normalize_category ──────────────────────────────────────────────────────


def test_normalize_category():
    assert normalize_category("mobile_combustion") == "mobile_combustion"
    assert normalize_category("araç") == "mobile_combustion"
    assert normalize_category("elektrik") == "electricity"
    assert normalize_category("atık") == "waste"


# ─── sample_data ─────────────────────────────────────────────────────────────


def test_get_sample_data():
    df = pd.DataFrame(
        {
            "Tarih": ["2024-01-01", "2024-01-02", None],
            "Miktar": ["100", "200", "300"],
        }
    )
    result = get_sample_data(df, n=5)
    assert "Tarih" in result
    assert len(result["Tarih"]) == 2  # None excluded
    assert len(result["Miktar"]) == 3


# ─── apply_mappings ──────────────────────────────────────────────────────────


def test_apply_mappings_basic():
    row = {
        "Tarih": "2024-01-15",
        "Litre": "500",
        "Plaka": "34ABC123",
    }
    mappings = [
        ColumnMapping(source_column="Tarih", target_field="date", confidence=0.9, sample_values=[]),
        ColumnMapping(
            source_column="Litre", target_field="amount", confidence=0.95, sample_values=[]
        ),
        ColumnMapping(
            source_column="Plaka", target_field="vehicle_id", confidence=0.85, sample_values=[]
        ),
    ]
    record, errors = apply_mappings(row, mappings)
    assert record["amount"] == 500.0
    assert record["vehicle_id"] == "34ABC123"
    assert len(errors) == 0


def test_apply_mappings_invalid_amount():
    row = {"Miktar": "abc-invalid"}
    mappings = [
        ColumnMapping(
            source_column="Miktar", target_field="amount", confidence=0.8, sample_values=[]
        )
    ]
    record, errors = apply_mappings(row, mappings)
    assert "amount" not in record or record["amount"] is None
    assert len(errors) > 0


# ─── process_dataframe ───────────────────────────────────────────────────────


def test_process_dataframe():
    df = pd.DataFrame(
        {
            "Tarih": ["2024-01-01", "2024-01-02", "BAD_DATE"],
            "Litre": ["100", "200", "not-a-number"],
            "Plaka": ["34ABC", "06XYZ", "01DEF"],
        }
    )
    mappings = [
        ColumnMapping(source_column="Tarih", target_field="date", confidence=0.9, sample_values=[]),
        ColumnMapping(
            source_column="Litre", target_field="amount", confidence=0.9, sample_values=[]
        ),
        ColumnMapping(
            source_column="Plaka", target_field="vehicle_id", confidence=0.9, sample_values=[]
        ),
    ]
    valid, errors = process_dataframe(df, mappings)
    assert len(valid) + len(errors) == 3
