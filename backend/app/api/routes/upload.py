from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.import_batch import ImportBatch
from app.models.import_error import ImportError
from app.schemas.upload import DeleteBatchResponse, ImportErrorItem, UploadBatchListItem, UploadResponse
from app.services.excel_import import DuplicateImportError, ExcelImportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["uploads"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Результат загрузки Excel с карточками МТР.",
            "content": {
                "application/json": {
                    "example": {
                        "batch_id": 12,
                        "file_name": "brief_cards.xlsx",
                        "status": "completed",
                        "rows_total": 320,
                        "rows_success": 300,
                        "rows_error": 5,
                        "rows_duplicate": 15,
                    }
                }
            },
        }
    },
)
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
    try:
        batch = service.import_excel(file.filename, content)
    except DuplicateImportError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    logger.info("Import finished for file=%s batch_id=%s", file.filename, batch.id)
    return UploadResponse(
        batch_id=batch.id,
        file_name=batch.file_name,
        status=batch.status,
        rows_total=batch.rows_total,
        rows_success=batch.rows_success,
        rows_error=batch.rows_error,
        rows_duplicate=batch.rows_duplicate,
    )


@router.get(
    "/uploads",
    response_model=list[UploadBatchListItem],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 12,
                            "file_name": "brief_cards.xlsx",
                            "uploaded_at": "2026-04-10T08:10:00Z",
                            "status": "completed",
                            "rows_total": 320,
                            "rows_success": 300,
                            "rows_error": 5,
                            "rows_duplicate": 15,
                        }
                    ]
                }
            }
        }
    },
)
def list_uploads(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ImportBatch]:
    query = select(ImportBatch).order_by(ImportBatch.uploaded_at.desc()).limit(limit)
    return list(db.scalars(query))


@router.get(
    "/uploads/{batch_id}/errors",
    response_model=list[ImportErrorItem],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "batch_id": 12,
                            "row_number": 15,
                            "error_message": "Некорректный GUID карточки: wrong-guid",
                            "raw_row_json": {"GUID": "wrong-guid"},
                            "created_at": "2026-04-10T08:15:00Z",
                        }
                    ]
                }
            }
        }
    },
)
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


@router.delete(
    "/uploads/{batch_id}",
    response_model=DeleteBatchResponse,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"batch_id": 12, "status": "deleted"}
                }
            }
        }
    },
)
def delete_upload_batch(batch_id: int, db: Session = Depends(get_db)) -> DeleteBatchResponse:
    batch = db.get(ImportBatch, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Upload batch not found")
    db.delete(batch)
    db.commit()
    return DeleteBatchResponse(batch_id=batch_id, status="deleted")
