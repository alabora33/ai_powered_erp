"""
Upload router: file upload, job management, status polling.
"""

import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from loguru import logger
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.data_processor import save_upload_file
from backend.database import get_db
from backend.models import MappedRecord, UploadJob
from backend.schemas import (
    JobListItem,
    JobStatus,
    RecordListResponse,
    UploadResponse,
)

router = APIRouter(prefix="/api/upload", tags=["Upload & Processing"])


@router.post("", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload an Excel or CSV file for AI-powered processing.
    Returns a job_id to track processing status.
    """
    # Validate file type
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {settings.allowed_extensions}",
        )

    # Validate file size
    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_file_size_mb}MB",
        )

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    try:
        # Save file to disk
        saved_name, full_path = save_upload_file(content, file.filename)

        # Create job record
        job = UploadJob(
            filename=saved_name,
            original_filename=file.filename,
            file_path=full_path,
            file_size=len(content),
            file_type=ext.lstrip("."),
            status="pending",
        )
        db.add(job)
        await db.flush()  # Get the ID
        job_id = job.id
        await db.commit()

        # Dispatch Celery task
        from backend.tasks import process_upload

        task = process_upload.delay(job_id)

        # Update task_id
        job.task_id = task.id
        await db.commit()

        logger.info(f"📤 Upload accepted: job={job_id}, task={task.id}")
        return UploadResponse(
            job_id=job_id,
            message=f"File '{file.filename}' uploaded successfully. Processing started.",
            task_id=task.id,
        )

    except Exception as e:
        logger.exception(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/jobs", response_model=list[JobListItem])
async def list_jobs(
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all upload jobs, most recent first."""
    query = select(UploadJob).order_by(desc(UploadJob.created_at)).limit(limit).offset(offset)
    if status:
        query = query.where(UploadJob.status == status)
    result = await db.execute(query)
    jobs = result.scalars().all()
    return jobs


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed status of a specific job."""
    result = await db.execute(select(UploadJob).where(UploadJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return job


@router.get("/jobs/{job_id}/records", response_model=RecordListResponse)
async def get_job_records(
    job_id: str,
    page: int = 1,
    page_size: int = 50,
    valid_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get processed records for a job with pagination."""
    # Verify job exists
    result = await db.execute(select(UploadJob).where(UploadJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    offset = (page - 1) * page_size

    query = select(MappedRecord).where(MappedRecord.job_id == job_id)
    count_query = (
        select(func.count()).select_from(MappedRecord).where(MappedRecord.job_id == job_id)
    )

    if valid_only:
        query = query.where(MappedRecord.is_valid.is_(True))
        count_query = count_query.where(MappedRecord.is_valid.is_(True))

    query = query.order_by(MappedRecord.row_number).limit(page_size).offset(offset)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    records_result = await db.execute(query)
    records = records_result.scalars().all()

    return RecordListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=records,
    )


@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a job and all its records."""
    result = await db.execute(select(UploadJob).where(UploadJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    # Delete file from disk
    try:
        if os.path.exists(job.file_path):
            os.remove(job.file_path)
    except Exception as e:
        logger.warning(f"Could not delete file {job.file_path}: {e}")

    await db.delete(job)
    await db.commit()
    return {"message": f"Job '{job_id}' deleted successfully"}
