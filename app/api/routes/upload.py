from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.import_batch import ImportBatch
from app.models.import_error import ImportError
from app.schemas.upload import ImportErrorItem, UploadBatchListItem, UploadResponse
from app.services.excel_import import ExcelImportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["uploads"])


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > settings.upload_max_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Max size is {settings.upload_max_size_mb} MB",
        )

    service = ExcelImportService(db)
    batch = service.import_excel(file.filename, content)
    logger.info("Import finished for file=%s batch_id=%s", file.filename, batch.id)
    return UploadResponse(
        batch_id=batch.id,
        file_name=batch.file_name,
        status=batch.status,
        rows_total=batch.rows_total,
        rows_success=batch.rows_success,
        rows_error=batch.rows_error,
    )


@router.get("/uploads", response_model=list[UploadBatchListItem])
def list_uploads(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ImportBatch]:
    query = select(ImportBatch).order_by(ImportBatch.uploaded_at.desc()).limit(limit)
    return list(db.scalars(query))


@router.get("/uploads/{batch_id}/errors", response_model=list[ImportErrorItem])
def batch_errors(batch_id: int, db: Session = Depends(get_db)) -> list[ImportError]:
    batch = db.get(ImportBatch, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Upload batch not found")

    query = (
        select(ImportError)
        .where(ImportError.batch_id == batch_id)
        .order_by(ImportError.row_number.asc(), ImportError.id.asc())
    )
    return list(db.scalars(query))
