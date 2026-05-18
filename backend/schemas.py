"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


# ─── Column Mapping Schemas ───────────────────────────────────────────────────

class ColumnMapping(BaseModel):
    """AI-detected mapping for a single source column."""
    source_column: str = Field(..., description="Original column name in uploaded file")
    target_field: str = Field(..., description="Standard field name in our schema")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score")
    transformation: Optional[str] = Field(None, description="Value transformation to apply")
    sample_values: list[Any] = Field(default_factory=list, description="Sample values from the column")
    notes: Optional[str] = Field(None, description="AI explanation for this mapping")


class AIAnalysisResult(BaseModel):
    """Full AI analysis of uploaded file columns."""
    detected_mappings: list[ColumnMapping]
    emission_category: str
    fuel_type: Optional[str] = None
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
    data_quality_score: Optional[float] = None
    ai_summary: Optional[str] = None
    column_mappings: Optional[dict] = None
    detected_columns: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


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
    data_quality_score: Optional[float] = None
    created_at: datetime


# ─── Record Schemas ───────────────────────────────────────────────────────────

class MappedRecordOut(BaseModel):
    """Output schema for a mapped record."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    row_number: int
    emission_category: Optional[str] = None
    fuel_type: Optional[str] = None
    amount: Optional[float] = None
    unit: Optional[str] = None
    date: Optional[datetime] = None
    vehicle_id: Optional[str] = None
    description: Optional[str] = None
    supplier: Optional[str] = None
    cost: Optional[float] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    raw_data: Optional[dict] = None
    is_valid: bool
    validation_errors: Optional[list] = None
    confidence_score: Optional[float] = None
    ai_description: Optional[str] = None
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
    task_id: Optional[str] = None


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
