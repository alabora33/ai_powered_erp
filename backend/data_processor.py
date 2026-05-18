"""
Data Processor: Reads Excel/CSV files, applies AI-detected mappings,
validates records, and saves to the database.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from backend.config import settings
from backend.schemas import ColumnMapping

# ─── File Reading ─────────────────────────────────────────────────────────────


def read_file(file_path: str) -> pd.DataFrame:
    """Read Excel or CSV file into a DataFrame."""
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext in (".xlsx", ".xlsm"):
        df = pd.read_excel(file_path, engine="openpyxl", dtype=str)
    elif ext == ".xls":
        df = pd.read_excel(file_path, engine="xlrd", dtype=str)
    elif ext == ".csv":
        # Try to detect encoding
        import chardet

        with open(file_path, "rb") as f:
            raw = f.read(10000)
        enc = chardet.detect(raw).get("encoding", "utf-8") or "utf-8"
        try:
            df = pd.read_csv(file_path, dtype=str, encoding=enc)
        except Exception:
            df = pd.read_csv(file_path, dtype=str, encoding="latin-1")
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]
    # Drop fully empty rows
    df = df.dropna(how="all")
    logger.info(f"📄 File loaded: {path.name} — {len(df)} rows, {len(df.columns)} columns")
    return df


def get_sample_data(df: pd.DataFrame, n: int = 10) -> dict[str, list]:
    """Extract sample values per column for AI analysis."""
    result = {}
    for col in df.columns:
        values = df[col].dropna().tolist()[:n]
        result[col] = [str(v).strip() for v in values if str(v).strip() not in ("", "nan", "None")]
    return result


# ─── Value Transformers ───────────────────────────────────────────────────────


def parse_date(value: Any) -> datetime | None:
    """Parse various date formats."""
    if value is None or str(value).strip() in ("", "nan", "None"):
        return None
    from dateutil.parser import parse as dateutil_parse

    try:
        return dateutil_parse(str(value), dayfirst=True)
    except Exception:
        return None


def parse_float(value: Any) -> float | None:
    """Parse numeric value, handling Turkish decimal notation."""
    if value is None or str(value).strip() in ("", "nan", "None"):
        return None
    s = str(value).strip()
    # Turkish uses comma as decimal separator
    s = s.replace(".", "").replace(",", ".") if "," in s else s.replace(",", "")
    # Remove currency symbols and spaces
    s = s.replace("₺", "").replace("$", "").replace("€", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


FUEL_TYPE_MAP = {
    "mazot": "diesel",
    "motorin": "diesel",
    "dizel": "diesel",
    "diesel": "diesel",
    "benzin": "gasoline",
    "petrol": "gasoline",
    "gasoline": "gasoline",
    "lpg": "lpg",
    "tüpgaz": "lpg",
    "doğalgaz": "natural_gas",
    "dogalgaz": "natural_gas",
    "natural_gas": "natural_gas",
    "kömür": "coal",
    "coal": "coal",
    "elektrik": "electricity",
    "electricity": "electricity",
}

CATEGORY_MAP = {
    "mobile_combustion": "mobile_combustion",
    "mobil yanma": "mobile_combustion",
    "araç": "mobile_combustion",
    "vehicle": "mobile_combustion",
    "stationary_combustion": "stationary_combustion",
    "sabit yanma": "stationary_combustion",
    "electricity": "electricity",
    "elektrik": "electricity",
    "refrigerants": "refrigerants",
    "soğutucu": "refrigerants",
    "waste": "waste",
    "atık": "waste",
    "water": "water",
    "su": "water",
    "business_travel": "business_travel",
    "iş seyahati": "business_travel",
    "employee_commuting": "employee_commuting",
    "çalışan": "employee_commuting",
}


def normalize_fuel_type(value: Any) -> str | None:
    """Normalize fuel type to standard enum value."""
    if not value:
        return None
    v = str(value).lower().strip()
    for key, std in FUEL_TYPE_MAP.items():
        if key in v:
            return std
    return "other"


def normalize_category(value: Any) -> str | None:
    """Normalize emission category."""
    if not value:
        return None
    v = str(value).lower().strip()
    for key, std in CATEGORY_MAP.items():
        if key in v:
            return std
    return "other"


# ─── Row Mapping ──────────────────────────────────────────────────────────────


def apply_mappings(
    row: dict,
    mappings: list[ColumnMapping],
    default_category: str,
    default_fuel_type: str | None,
) -> tuple[dict, list[str]]:
    """
    Apply AI column mappings to a single row.
    Returns (mapped_record_dict, validation_errors)
    """
    record = {
        "emission_category": default_category,
        "fuel_type": default_fuel_type,
        "amount": None,
        "unit": None,
        "date": None,
        "vehicle_id": None,
        "description": None,
        "supplier": None,
        "cost": None,
        "currency": None,
        "location": None,
    }
    errors = []

    for mapping in mappings:
        src_col = mapping.source_column
        target = mapping.target_field
        raw_value = row.get(src_col)

        if raw_value is None or str(raw_value).strip() in ("", "nan", "None"):
            continue

        try:
            if target == "date":
                record["date"] = parse_date(raw_value)
                if record["date"] is None:
                    errors.append(f"Could not parse date: '{raw_value}' in column '{src_col}'")
            elif target == "amount":
                record["amount"] = parse_float(raw_value)
                if record["amount"] is None:
                    errors.append(f"Could not parse amount: '{raw_value}' in column '{src_col}'")
            elif target == "cost":
                record["cost"] = parse_float(raw_value)
            elif target == "fuel_type":
                record["fuel_type"] = normalize_fuel_type(raw_value) or default_fuel_type
            elif target == "emission_category":
                record["emission_category"] = normalize_category(raw_value) or default_category
            elif target in record:
                record[target] = str(raw_value).strip()
        except Exception as e:
            errors.append(f"Mapping error for '{src_col}' -> '{target}': {str(e)}")

    return record, errors


# ─── Full File Processing ─────────────────────────────────────────────────────


def process_dataframe(
    df: pd.DataFrame,
    mappings: list[ColumnMapping],
    default_category: str,
    default_fuel_type: str | None,
) -> tuple[list[dict], list[dict]]:
    """
    Process entire DataFrame with mappings.
    Returns (valid_records, error_records)
    """
    valid_records = []
    error_records = []

    for idx, row in df.iterrows():
        row_dict = {col: row.get(col) for col in df.columns}
        mapped, errors = apply_mappings(row_dict, mappings, default_category, default_fuel_type)

        record = {
            "row_number": int(idx) + 2,  # +2: 1-indexed + header row
            "raw_data": {k: str(v) for k, v in row_dict.items() if v is not None},
            "is_valid": len(errors) == 0,
            "validation_errors": errors if errors else None,
            **mapped,
        }

        if errors:
            error_records.append(record)
        else:
            valid_records.append(record)

    logger.info(
        f"✅ Processed {len(df)} rows: {len(valid_records)} valid, {len(error_records)} with errors"
    )
    return valid_records, error_records


# ─── File Save ────────────────────────────────────────────────────────────────


def save_upload_file(content: bytes, original_filename: str) -> tuple[str, str]:
    """
    Save uploaded file to disk.
    Returns (saved_filename, full_path)
    """
    ext = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    full_path = upload_dir / unique_name
    with open(full_path, "wb") as f:
        f.write(content)
    logger.info(f"💾 File saved: {full_path} ({len(content):,} bytes)")
    return unique_name, str(full_path)
