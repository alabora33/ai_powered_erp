"""
SQLAlchemy ORM Models for AI ERP.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Text, DateTime, Integer, Float, Boolean, JSON,
    ForeignKey, Enum as SAEnum, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


# ─── Upload Job ───────────────────────────────────────────────────────────────

class UploadJob(Base):
    """Represents a file upload and processing job."""
    __tablename__ = "upload_jobs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=gen_uuid
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # xlsx, csv, xls

    status: Mapped[str] = mapped_column(
        SAEnum("pending", "processing", "completed", "failed", "cancelled",
               name="job_status", create_type=False),
        default="pending",
        nullable=False,
    )

    # Celery task ID
    task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # AI analysis results
    detected_columns: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    column_mappings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Processing stats
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    processed_rows: Mapped[int] = mapped_column(Integer, default=0)
    error_rows: Mapped[int] = mapped_column(Integer, default=0)
    error_details: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Progress (0-100)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    records: Mapped[list["MappedRecord"]] = relationship(
        "MappedRecord", back_populates="job", cascade="all, delete-orphan"
    )


# ─── Mapped Record ────────────────────────────────────────────────────────────

class MappedRecord(Base):
    """A single row from an uploaded file, mapped to standard schema."""
    __tablename__ = "mapped_records"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=gen_uuid
    )
    job_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("upload_jobs.id", ondelete="CASCADE"),
        nullable=False
    )
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Standard mapped fields
    emission_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    vehicle_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    supplier: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Original raw data preserved
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Quality flags
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    validation_errors: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # AI-generated description
    ai_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    job: Mapped["UploadJob"] = relationship("UploadJob", back_populates="records")
