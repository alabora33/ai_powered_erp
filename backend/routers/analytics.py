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
from backend.schemas import DashboardStats

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

    # Categories breakdown (Disabled for now as we transitioned to dynamic schemas)
    categories = []

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
    dynamic_headers = []
    if records and records[0].extracted_data:
        dynamic_headers = list(records[0].extracted_data.keys())

    header = (
        ["row_number"] + dynamic_headers + ["is_valid", "confidence_score", "validation_errors"]
    )
    writer.writerow(header)

    for rec in records:
        row = [rec.row_number]
        for h in dynamic_headers:
            row.append((rec.extracted_data or {}).get(h, ""))

        row.extend(
            [
                rec.is_valid,
                rec.confidence_score or "",
                "; ".join(rec.validation_errors) if rec.validation_errors else "",
            ]
        )
        writer.writerow(row)

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
                **(r.extracted_data or {}),
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
