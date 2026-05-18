"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ─── Template Schemas ──────────────────────────────────────────────────────────

class MappingTemplateCreate(BaseModel):
    name: str
    description: str | None = None
    target_schema: list | dict

class MappingTemplateOut(MappingTemplateCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime

# ─── Column Mapping Schemas ───────────────────────────────────────────────────


class ColumnMapping(BaseModel):
    """AI-detected mapping for a single source column."""

    source_column: str = Field(..., description="Original column name in uploaded file")
    target_field: str = Field(..., description="Standard field name in our schema")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score")
    transformation: str | None = Field(None, description="Value transformation to apply")
    sample_values: list[Any] = Field(
        default_factory=list, description="Sample values from the column"
    )
    notes: str | None = Field(None, description="AI explanation for this mapping")


class AIAnalysisResult(BaseModel):
    """Full AI analysis of uploaded file columns."""

    detected_mappings: list[ColumnMapping]
    primary_category: str | None = Field(None, description="General category of the data")
    missing_fields: list[str] = Field(default_factory=list)
    data_quality_issues: list[str] = Field(default_factory=list)
    ai_summary: str
    confidence_overall: float = Field(ge=0.0, le=1.0)
    recommendations: list[str] = Field(default_factory=list)


# ─── Job Schemas ──────────────────────────────────────────────────────────────


class JobCreate(BaseModel):
    """Schema for creating a new upload job."""

    filename: str


class JobStatus(BaseModel):
    """Response schema for job status."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    original_filename: str
    status: str
    progress: int
    total_rows: int
    processed_rows: int
    error_rows: int
    data_quality_score: float | None = None
    ai_summary: str | None = None
    column_mappings: dict | None = None
    detected_columns: dict | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class JobListItem(BaseModel):
    """Lightweight schema for job list view."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    status: str
    progress: int
    total_rows: int
    processed_rows: int
    error_rows: int
    data_quality_score: float | None = None
    created_at: datetime


# ─── Record Schemas ───────────────────────────────────────────────────────────


class MappedRecordOut(BaseModel):
    """Output schema for a mapped record."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    row_number: int
    extracted_data: dict
    raw_data: dict | None = None
    is_valid: bool
    validation_errors: list | None = None
    confidence_score: float | None = None
    ai_description: str | None = None
    created_at: datetime


class RecordListResponse(BaseModel):
    """Paginated list of records."""

    total: int
    page: int
    page_size: int
    items: list[MappedRecordOut]


# ─── Upload Response ──────────────────────────────────────────────────────────


class UploadResponse(BaseModel):
    """Response after file upload."""

    job_id: str
    message: str
    task_id: str | None = None


# ─── Analytics Schemas ────────────────────────────────────────────────────────


class CategorySummary(BaseModel):
    """Summary of records by category."""

    emission_category: str
    count: int
    total_amount: float
    avg_confidence: float


class DashboardStats(BaseModel):
    """Dashboard overview statistics."""

    total_jobs: int
    total_records: int
    valid_records: int
    error_records: int
    avg_quality_score: float
    categories: list[CategorySummary]
    recent_jobs: list[JobListItem]


# ─── Health Check ─────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    ai_service: str
    version: str
