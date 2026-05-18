"""
AI Service: Gemini-powered column analysis and data mapping.
Uses structured output (JSON mode) for reliable parsing.
"""

import json
import re
from typing import Optional
import google.generativeai as genai
from loguru import logger
from backend.config import settings
from backend.schemas import AIAnalysisResult, ColumnMapping


# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)


SYSTEM_PROMPT = """
You are an expert data analyst specializing in ERP systems, environmental reporting, 
and carbon footprint data. Your task is to analyze column headers and sample data 
from uploaded Excel/CSV files and map them to a standard data model.

Standard target fields:
- emission_category: Category of emission (mobile_combustion, stationary_combustion, 
  electricity, refrigerants, waste, water, business_travel, employee_commuting, 
  purchased_goods, other)
- fuel_type: Type of fuel (diesel, gasoline, lpg, natural_gas, coal, electricity, other)
- amount: Numeric quantity/volume consumed
- unit: Unit of measurement (litre, kg, kWh, ton, m3, km, piece, etc.)
- date: Date of the transaction/record (map to invoice_date, transaction_date, etc.)
- vehicle_id: Vehicle identifier (license plate, fleet number, etc.)
- description: Description or notes
- supplier: Supplier/vendor name
- cost: Financial cost/price
- currency: Currency code (TRY, USD, EUR, etc.)
- location: Location/site of the activity

Analyze Turkish AND English column names. Common Turkish terms:
- "Mazot/Motorin" = diesel fuel
- "Benzin" = gasoline
- "Litre/lt" = litre
- "Tarih" = date
- "Plaka" = vehicle license plate
- "Araç" = vehicle
- "Tedarikçi/Tedarikçi" = supplier
- "Tutar/Miktar" = amount
- "Birim" = unit
- "Yakıt" = fuel
- "Tüketim" = consumption
- "Fatura" = invoice
- "Açıklama" = description

Always respond with valid JSON only, no markdown code blocks.
"""

ANALYSIS_PROMPT_TEMPLATE = """
Analyze the following Excel/CSV file columns and sample data.
Map each column to the standard field schema and identify:
1. What type of data this file contains
2. The emission category
3. Missing required fields
4. Data quality issues

File columns and sample values:
{columns_json}

Respond with this exact JSON structure:
{{
  "detected_mappings": [
    {{
      "source_column": "original column name",
      "target_field": "standard_field_name",
      "confidence": 0.95,
      "transformation": "lowercase | date_parse | numeric | none",
      "sample_values": ["val1", "val2"],
      "notes": "reason for mapping"
    }}
  ],
  "emission_category": "mobile_combustion",
  "fuel_type": "diesel",
  "missing_fields": ["field1", "field2"],
  "data_quality_issues": ["issue description"],
  "ai_summary": "Human-readable summary of what this data contains and how it was mapped",
  "confidence_overall": 0.88,
  "recommendations": ["recommendation 1", "recommendation 2"]
}}
"""


class AIService:
    """Gemini AI service for column analysis and data mapping."""

    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temp for consistent structured output
                top_p=0.95,
                max_output_tokens=4096,
            ),
        )

    async def analyze_columns(
        self,
        columns: list[str],
        sample_data: dict[str, list],
    ) -> AIAnalysisResult:
        """
        Analyze columns and sample data using Gemini AI.
        Returns structured mapping result.
        """
        columns_info = {}
        for col in columns:
            samples = sample_data.get(col, [])
            # Take up to 5 non-null samples
            clean_samples = [str(s) for s in samples if s is not None and str(s).strip()][:5]
            columns_info[col] = clean_samples

        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            columns_json=json.dumps(columns_info, ensure_ascii=False, indent=2)
        )

        try:
            logger.info(f"Sending {len(columns)} columns to Gemini for analysis...")
            response = self.model.generate_content(
                [SYSTEM_PROMPT, prompt]
            )
            raw_text = response.text.strip()

            # Strip markdown code blocks if present
            raw_text = re.sub(r"```json\s*", "", raw_text)
            raw_text = re.sub(r"```\s*", "", raw_text)
            raw_text = raw_text.strip()

            data = json.loads(raw_text)
            result = AIAnalysisResult(**data)
            logger.info(
                f"✅ AI analysis complete. Category: {result.emission_category}, "
                f"Confidence: {result.confidence_overall:.2%}"
            )
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}\nRaw: {raw_text[:500]}")
            return self._fallback_analysis(columns, sample_data)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_analysis(columns, sample_data)

    def _fallback_analysis(
        self, columns: list[str], sample_data: dict[str, list]
    ) -> AIAnalysisResult:
        """Heuristic-based fallback when AI fails."""
        logger.warning("Using heuristic fallback analysis...")
        mappings = []

        KEYWORD_MAP = {
            # Date keywords
            ("tarih", "date", "tarih", "invoice_date", "transaction_date"): "date",
            # Amount keywords
            ("litre", "lt", "liters", "miktar", "tutar", "amount", "quantity", "tüketim"): "amount",
            # Fuel type keywords
            ("yakıt", "fuel", "mazot", "motorin", "benzin", "diesel", "gasoline"): "fuel_type",
            # Vehicle keywords
            ("plaka", "plate", "araç", "vehicle", "fleet"): "vehicle_id",
            # Supplier keywords
            ("tedarikçi", "supplier", "vendor", "firma"): "supplier",
            # Cost keywords
            ("tutar", "fiyat", "cost", "price", "ücret", "bedel"): "cost",
            # Description keywords
            ("açıklama", "description", "notes", "not", "aciklama"): "description",
            # Location keywords
            ("konum", "lokasyon", "location", "adres", "site"): "location",
            # Unit keywords
            ("birim", "unit", "ölçü"): "unit",
        }

        for col in columns:
            col_lower = col.lower().strip()
            target = "description"  # default
            confidence = 0.5

            for keywords, field in KEYWORD_MAP.items():
                if any(kw in col_lower for kw in keywords):
                    target = field
                    confidence = 0.7
                    break

            mappings.append(ColumnMapping(
                source_column=col,
                target_field=target,
                confidence=confidence,
                transformation="none",
                sample_values=sample_data.get(col, [])[:3],
                notes="Heuristic mapping (AI unavailable)",
            ))

        return AIAnalysisResult(
            detected_mappings=mappings,
            emission_category="mobile_combustion",
            fuel_type="diesel",
            missing_fields=[],
            data_quality_issues=["AI analysis unavailable – heuristic mapping applied"],
            ai_summary="Heuristic analysis applied due to AI service unavailability.",
            confidence_overall=0.5,
            recommendations=["Please review mappings manually"],
        )

    async def generate_record_description(
        self,
        record_data: dict,
        emission_category: str,
    ) -> str:
        """Generate a human-readable description for a mapped record."""
        try:
            prompt = f"""
Generate a concise one-sentence description (max 100 chars) for this emission record:
Category: {emission_category}
Data: {json.dumps(record_data, ensure_ascii=False)}
Respond with only the description text, no quotes.
"""
            response = self.model.generate_content(prompt)
            return response.text.strip()[:200]
        except Exception as e:
            logger.warning(f"Failed to generate record description: {e}")
            return f"{emission_category} record"

    async def validate_data_quality(
        self,
        records: list[dict],
        column_mappings: list[ColumnMapping],
    ) -> dict:
        """Perform AI-powered data quality analysis."""
        try:
            sample = records[:20]  # First 20 records
            prompt = f"""
Analyze these {len(records)} data records (showing first {len(sample)}) for quality issues.

Column mappings used: {json.dumps([m.model_dump() for m in column_mappings], ensure_ascii=False)}

Sample records: {json.dumps(sample, ensure_ascii=False, default=str)}

Respond with JSON:
{{
  "quality_score": 0.85,
  "issues": ["issue1", "issue2"],
  "error_rows": [row_indices],
  "recommendations": ["recommendation"]
}}
"""
            response = self.model.generate_content(prompt)
            raw = response.text.strip()
            raw = re.sub(r"```json\s*", "", raw)
            raw = re.sub(r"```\s*", "", raw)
            return json.loads(raw.strip())
        except Exception as e:
            logger.warning(f"Quality validation error: {e}")
            return {"quality_score": 0.7, "issues": [], "error_rows": [], "recommendations": []}


# Singleton instance
ai_service = AIService()
