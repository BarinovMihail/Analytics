from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.comparison_task import ComparisonTask
from app.schemas.compare import CompareRequest, CompareResponse, CompareTaskDetail
from app.services.card_comparator import filter_cards, get_filter_characteristic_names, run_comparison_task
from app.services.excel_exporter import export_cards_to_excel

EXPORT_DIR = Path(__file__).resolve().parents[3] / "storage" / "compare_exports"

router = APIRouter(prefix="/api", tags=["compare"])


def _to_compare_response(task: ComparisonTask) -> CompareResponse:
    return CompareResponse(
        task_id=task.id,
        task_name=task.name,
        matched_cards=task.matched_cards,
        total_cards=task.total_cards,
        status=task.status,
        created_at=task.created_at,
    )


def _to_compare_detail(task: ComparisonTask) -> CompareTaskDetail:
    return CompareTaskDetail(
        task_id=task.id,
        task_name=task.name,
        matched_cards=task.matched_cards,
        total_cards=task.total_cards,
        status=task.status,
        created_at=task.created_at,
        filter_params_json=task.filter_params_json,
        output_file_path=task.output_file_path,
        finished_at=task.finished_at,
    )


@router.post(
    "/compare",
    response_model=CompareResponse,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "task_id": 7,
                        "task_name": "Фильтр 2026-04-09",
                        "matched_cards": 14,
                        "total_cards": 300,
                        "status": "done",
                        "created_at": "2026-04-10T08:20:00Z",
                    }
                }
            }
        }
    },
)
def create_compare_task(payload: CompareRequest, db: Session = Depends(get_db)) -> CompareResponse:
    task = run_comparison_task(
        db,
        task_name=payload.task_name,
        filters=payload.filters,
        export_dir=EXPORT_DIR,
    )
    return _to_compare_response(task)


@router.get(
    "/compare/{task_id}",
    response_model=CompareTaskDetail,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "task_id": 7,
                        "task_name": "Фильтр 2026-04-09",
                        "matched_cards": 14,
                        "total_cards": 300,
                        "status": "done",
                        "created_at": "2026-04-10T08:20:00Z",
                        "filter_params_json": {"dn": "20", "pressure_min": "2.5"},
                        "output_file_path": "backend/storage/compare_exports/comparison_task_7.xlsx",
                        "finished_at": "2026-04-10T08:20:02Z",
                    }
                }
            }
        }
    },
)
def get_compare_task(task_id: int, db: Session = Depends(get_db)) -> CompareTaskDetail:
    task = db.get(ComparisonTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Comparison task not found")
    return _to_compare_detail(task)


@router.get(
    "/compare",
    response_model=list[CompareResponse],
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "task_id": 7,
                            "task_name": "Фильтр 2026-04-09",
                            "matched_cards": 14,
                            "total_cards": 300,
                            "status": "done",
                            "created_at": "2026-04-10T08:20:00Z",
                        }
                    ]
                }
            }
        }
    },
)
def list_compare_tasks(db: Session = Depends(get_db)) -> list[CompareResponse]:
    query = select(ComparisonTask).order_by(ComparisonTask.created_at.desc(), ComparisonTask.id.desc())
    return [_to_compare_response(task) for task in db.scalars(query)]


@router.get("/compare/{task_id}/download")
def download_compare_task(task_id: int, db: Session = Depends(get_db)) -> FileResponse:
    task = db.get(ComparisonTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Comparison task not found")
    if task.status != "done":
        raise HTTPException(status_code=409, detail="Comparison task is not finished")

    if task.output_file_path:
        file_path = Path(task.output_file_path)
    else:
        file_path = EXPORT_DIR / f"comparison_task_{task.id}.xlsx"

    if not file_path.exists():
        cards = filter_cards(db, task.filter_params_json)
        char_names = get_filter_characteristic_names(task.filter_params_json)
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(export_cards_to_excel(cards, char_names))
        task.output_file_path = str(file_path)
        db.commit()

    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=file_path.name,
    )
