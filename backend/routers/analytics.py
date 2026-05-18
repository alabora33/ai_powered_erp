"""
Analytics router: dashboard stats, category breakdowns, exports.
"""

import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import MappedRecord, UploadJob
from backend.schemas import CategorySummary, DashboardStats

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """Get overview statistics for the dashboard."""

    # Total jobs
    total_jobs_result = await db.execute(select(func.count()).select_from(UploadJob))
    total_jobs = total_jobs_result.scalar() or 0

    # Total / valid / error records
    total_records_result = await db.execute(select(func.count()).select_from(MappedRecord))
    total_records = total_records_result.scalar() or 0

    valid_result = await db.execute(
        select(func.count()).select_from(MappedRecord).where(MappedRecord.is_valid.is_(True))
    )
    valid_records = valid_result.scalar() or 0
    error_records = total_records - valid_records

    # Average quality score
    avg_quality_result = await db.execute(
        select(func.avg(UploadJob.data_quality_score)).where(
            UploadJob.data_quality_score.isnot(None)
        )
    )
    avg_quality = avg_quality_result.scalar() or 0.0

    # Categories breakdown
    category_result = await db.execute(
        select(
            MappedRecord.emission_category,
            func.count().label("count"),
            func.coalesce(func.sum(MappedRecord.amount), 0).label("total_amount"),
            func.coalesce(func.avg(MappedRecord.confidence_score), 0).label("avg_confidence"),
        )
        .where(MappedRecord.emission_category.isnot(None))
        .group_by(MappedRecord.emission_category)
        .order_by(desc("count"))
    )
    categories = [
        CategorySummary(
            emission_category=row.emission_category or "unknown",
            count=row.count,
            total_amount=float(row.total_amount or 0),
            avg_confidence=float(row.avg_confidence or 0),
        )
        for row in category_result.fetchall()
    ]

    # Recent jobs
    recent_result = await db.execute(
        select(UploadJob).order_by(desc(UploadJob.created_at)).limit(5)
    )
    recent_jobs = recent_result.scalars().all()

    return DashboardStats(
        total_jobs=total_jobs,
        total_records=total_records,
        valid_records=valid_records,
        error_records=error_records,
        avg_quality_score=round(float(avg_quality), 3),
        categories=categories,
        recent_jobs=recent_jobs,
    )


@router.get("/jobs/{job_id}/export/csv")
async def export_records_csv(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Export processed records as CSV."""
    result = await db.execute(select(UploadJob).where(UploadJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    records_result = await db.execute(
        select(MappedRecord).where(MappedRecord.job_id == job_id).order_by(MappedRecord.row_number)
    )
    records = records_result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "row_number",
            "emission_category",
            "fuel_type",
            "amount",
            "unit",
            "date",
            "vehicle_id",
            "description",
            "supplier",
            "cost",
            "currency",
            "location",
            "is_valid",
            "confidence_score",
            "validation_errors",
        ]
    )

    for rec in records:
        writer.writerow(
            [
                rec.row_number,
                rec.emission_category or "",
                rec.fuel_type or "",
                rec.amount or "",
                rec.unit or "",
                rec.date.isoformat() if rec.date else "",
                rec.vehicle_id or "",
                rec.description or "",
                rec.supplier or "",
                rec.cost or "",
                rec.currency or "",
                rec.location or "",
                rec.is_valid,
                rec.confidence_score or "",
                "; ".join(rec.validation_errors) if rec.validation_errors else "",
            ]
        )

    output.seek(0)
    filename = f"ai_erp_export_{job_id[:8]}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/jobs/{job_id}/export/json")
async def export_records_json(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Export processed records as JSON."""
    result = await db.execute(select(UploadJob).where(UploadJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    records_result = await db.execute(
        select(MappedRecord).where(MappedRecord.job_id == job_id).order_by(MappedRecord.row_number)
    )
    records = records_result.scalars().all()

    data = {
        "job_id": job_id,
        "filename": job.original_filename,
        "total_records": len(records),
        "exported_at": __import__("datetime").datetime.utcnow().isoformat(),
        "records": [
            {
                "row_number": r.row_number,
                "emission_category": r.emission_category,
                "fuel_type": r.fuel_type,
                "amount": r.amount,
                "unit": r.unit,
                "date": r.date.isoformat() if r.date else None,
                "vehicle_id": r.vehicle_id,
                "description": r.description,
                "supplier": r.supplier,
                "cost": r.cost,
                "currency": r.currency,
                "location": r.location,
                "is_valid": r.is_valid,
                "confidence_score": r.confidence_score,
                "validation_errors": r.validation_errors,
            }
            for r in records
        ],
    }

    json_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    filename = f"ai_erp_export_{job_id[:8]}.json"
    return StreamingResponse(
        iter([json_str]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
