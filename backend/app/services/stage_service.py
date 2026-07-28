from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.progress import Progress
from app.models.stage import Stage


def get_stage_list(db: Session, user_id: int | None = None) -> list[dict]:
    stages = list(db.scalars(select(Stage).order_by(Stage.stage_id)))
    cleared_stage_ids: set[int] = set()

    if user_id is not None:
        progress_rows = db.scalars(
            select(Progress).where(Progress.user_id == user_id, Progress.cleared.is_(True))
        )
        cleared_stage_ids = {row.stage_id for row in progress_rows}

    response = []
    for stage in stages:
        previous_stage_id = stage.stage_id - 1
        locked = stage.stage_id != 1 and previous_stage_id not in cleared_stage_ids
        response.append(
            {
                "stage_id": stage.stage_id,
                "title": stage.title,
                "cleared": stage.stage_id in cleared_stage_ids,
                "locked": locked,
            }
        )
    return response


def ensure_stage_access(db: Session, stage_id: int, user_id: int | None = None) -> Stage:
    stage = db.get(Stage, stage_id)
    if stage is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

    if user_id is None or stage_id == 1:
        return stage

    previous_progress = db.scalar(
        select(Progress).where(
            Progress.user_id == user_id,
            Progress.stage_id == stage_id - 1,
            Progress.cleared.is_(True),
        )
    )
    if previous_progress is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Stage is locked")

    return stage
