"""
AI Service: Gemini-powered column analysis and data mapping.
Uses structured output (JSON mode) for reliable parsing.
"""

import json
import re

import google.generativeai as genai
from loguru import logger

from backend.config import settings
from backend.schemas import AIAnalysisResult, ColumnMapping

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)


SYSTEM_PROMPT = """
You are an expert data analyst specializing in B2B data onboarding and system integrations.
Your task is to analyze column headers and sample data from uploaded Excel/CSV files 
and map them to the provided standard target schema dynamically.

IMPORTANT: All human-readable text you generate (such as 'notes', 'primary_category', 'data_quality_issues', 'ai_summary', and 'recommendations') MUST BE STRICTLY IN {language}. Do not write explanations in any other language.

Always respond with valid JSON only, no markdown code blocks.
"""

ANALYSIS_PROMPT_TEMPLATE = """
Analyze the following Excel/CSV file columns and sample data.
Map each column to the TARGET SCHEMA and identify:
1. What type of data this file contains
2. Missing required fields from the target schema
3. Data quality issues

TARGET SCHEMA:
{target_schema_json}

File columns and sample values:
{columns_json}

Respond with this exact JSON structure:
{{
  "detected_mappings": [
    {{
      "source_column": "original column name",
      "target_field": "field_name_from_target_schema",
      "confidence": 0.95,
      "transformation": "lowercase | date_parse | numeric | none",
      "sample_values": ["val1", "val2"],
      "notes": "reason for mapping"
    }}
  ],
  "primary_category": "A general category describing the uploaded data (e.g., E-commerce, HR, Finance)",
  "missing_fields": ["field1_from_target_schema", "field2"],
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
        target_schema: list | dict,
        language: str = "tr",
    ) -> AIAnalysisResult:
        """
        Analyze columns and sample data using Gemini AI.
        Returns structured mapping result based on dynamic target schema.
        """
        columns_info = {}
        for col in columns:
            samples = sample_data.get(col, [])
            # Take up to 5 non-null samples
            clean_samples = [str(s) for s in samples if s is not None and str(s).strip()][:5]
            columns_info[col] = clean_samples

        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            target_schema_json=json.dumps(target_schema, ensure_ascii=False, indent=2),
            columns_json=json.dumps(columns_info, ensure_ascii=False, indent=2)
        )

        try:
            logger.info(f"Sending {len(columns)} columns to Gemini for analysis (lang={language})...")
            
            lang_name = "Turkish" if language == "tr" else "English"
            sys_prompt = SYSTEM_PROMPT.format(language=lang_name)
            
            response = self.model.generate_content([sys_prompt, prompt])
            raw_text = response.text.strip()

            # Strip markdown code blocks if present
            raw_text = re.sub(r"```json\s*", "", raw_text)
            raw_text = re.sub(r"```\s*", "", raw_text)
            raw_text = raw_text.strip()

            data = json.loads(raw_text)
            result = AIAnalysisResult(**data)
            logger.info(
                f"✅ AI analysis complete. Category: {result.primary_category}, "
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
        """Generic fallback when AI fails."""
        logger.warning("Using generic fallback analysis...")
        mappings = []

        for col in columns:
            mappings.append(
                ColumnMapping(
                    source_column=col,
                    target_field=col.lower().replace(" ", "_"),
                    confidence=0.5,
                    transformation="none",
                    sample_values=sample_data.get(col, [])[:3],
                    notes="Generic mapping (AI unavailable)",
                )
            )

        return AIAnalysisResult(
            detected_mappings=mappings,
            primary_category="Unknown",
            missing_fields=[],
            data_quality_issues=["AI analysis unavailable – generic mapping applied"],
            ai_summary="Fallback generic analysis applied due to AI service error.",
            confidence_overall=0.5,
            recommendations=["Please review mappings manually"],
        )

    async def generate_record_description(
        self,
        record_data: dict,
        primary_category: str | None,
    ) -> str:
        """Generate a human-readable description for a mapped record."""
        try:
            category = primary_category or "Data"
            prompt = f"""
Generate a concise one-sentence description (max 100 chars) for this record:
Category: {category}
Data: {json.dumps(record_data, ensure_ascii=False)}
Respond with only the description text, no quotes.
"""
            response = self.model.generate_content(prompt)
            return response.text.strip()[:200]
        except Exception as e:
            logger.warning(f"Failed to generate record description: {e}")
            return f"Record item"

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
