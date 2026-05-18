"""
Celery tasks: async file processing pipeline.
Each task updates job status in the DB as it progresses.
"""

import asyncio
from datetime import datetime, timezone
from celery import shared_task
from loguru import logger
from sqlalchemy import select

from backend.celery_app import celery_app
from backend.config import settings


def run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, name="backend.tasks.process_upload")
def process_upload(self, job_id: str) -> dict:
    """
    Main processing task:
    1. Read the uploaded file
    2. Send columns to AI for analysis
    3. Apply mappings to each row
    4. Validate records
    5. Save records to DB
    6. Update job status
    """
    logger.info(f"🚀 Starting processing for job: {job_id}")
    return run_async(_process_upload_async(self, job_id))


async def _process_upload_async(task, job_id: str) -> dict:
    """Async implementation of the processing pipeline."""
    from backend.database import AsyncSessionLocal
    from backend.models import UploadJob, MappedRecord
    from backend.data_processor import read_file, get_sample_data, process_dataframe
    from backend.ai_service import ai_service
    from backend.schemas import ColumnMapping

    async with AsyncSessionLocal() as db:
        # 1. Fetch job from DB
        result = await db.execute(select(UploadJob).where(UploadJob.id == job_id))
        job = result.scalar_one_or_none()

        if not job:
            logger.error(f"Job {job_id} not found!")
            return {"error": "Job not found"}

        try:
            # Update status: processing
            job.status = "processing"
            job.progress = 5
            await db.commit()

            # 2. Read file
            logger.info(f"📂 Reading file: {job.file_path}")
            df = read_file(job.file_path)
            job.total_rows = len(df)
            job.progress = 15
            await db.commit()

            # Store detected columns info
            job.detected_columns = {
                "columns": list(df.columns),
                "row_count": len(df),
                "sample_data": get_sample_data(df, n=3),
            }
            await db.commit()

            # 3. AI analysis
            logger.info("🤖 Running AI column analysis...")
            sample_data = get_sample_data(df, n=10)
            ai_result = await ai_service.analyze_columns(
                columns=list(df.columns),
                sample_data=sample_data,
            )

            job.progress = 40
            job.ai_summary = ai_result.ai_summary
            job.column_mappings = {
                "mappings": [m.model_dump() for m in ai_result.detected_mappings],
                "emission_category": ai_result.emission_category,
                "fuel_type": ai_result.fuel_type,
                "missing_fields": ai_result.missing_fields,
                "data_quality_issues": ai_result.data_quality_issues,
                "recommendations": ai_result.recommendations,
                "confidence_overall": ai_result.confidence_overall,
            }
            await db.commit()

            # 4. Process rows
            logger.info("⚙️ Applying column mappings to all rows...")
            valid_records, error_records = process_dataframe(
                df=df,
                mappings=ai_result.detected_mappings,
                default_category=ai_result.emission_category,
                default_fuel_type=ai_result.fuel_type,
            )
            job.progress = 70
            await db.commit()

            # 5. Save records to DB in batches
            all_records = valid_records + error_records
            batch_size = 100

            for i in range(0, len(all_records), batch_size):
                batch = all_records[i:i + batch_size]
                for rec in batch:
                    db_record = MappedRecord(
                        job_id=job_id,
                        row_number=rec["row_number"],
                        emission_category=rec.get("emission_category"),
                        fuel_type=rec.get("fuel_type"),
                        amount=rec.get("amount"),
                        unit=rec.get("unit"),
                        date=rec.get("date"),
                        vehicle_id=rec.get("vehicle_id"),
                        description=rec.get("description"),
                        supplier=rec.get("supplier"),
                        cost=rec.get("cost"),
                        currency=rec.get("currency"),
                        location=rec.get("location"),
                        raw_data=rec.get("raw_data"),
                        is_valid=rec.get("is_valid", True),
                        validation_errors=rec.get("validation_errors"),
                        confidence_score=ai_result.confidence_overall,
                    )
                    db.add(db_record)

                await db.commit()
                progress = 70 + int((i / len(all_records)) * 25)
                job.progress = min(progress, 95)
                await db.commit()

            # 6. Finalize job
            job.status = "completed"
            job.progress = 100
            job.processed_rows = len(valid_records)
            job.error_rows = len(error_records)
            job.error_details = [
                {"row": r["row_number"], "errors": r.get("validation_errors", [])}
                for r in error_records[:50]  # Cap error details at 50
            ]
            job.data_quality_score = ai_result.confidence_overall
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()

            logger.info(
                f"✅ Job {job_id} completed: {len(valid_records)} valid, "
                f"{len(error_records)} errors"
            )
            return {
                "status": "completed",
                "job_id": job_id,
                "total_rows": len(df),
                "valid_rows": len(valid_records),
                "error_rows": len(error_records),
                "quality_score": ai_result.confidence_overall,
            }

        except Exception as e:
            logger.exception(f"❌ Job {job_id} failed: {e}")
            job.status = "failed"
            job.error_message = str(e)
            job.progress = 0
            await db.commit()
            return {"status": "failed", "error": str(e)}
