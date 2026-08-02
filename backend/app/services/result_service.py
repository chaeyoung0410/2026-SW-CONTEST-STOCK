from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.history import History
from app.models.progress import Progress
from app.models.result import Result
from app.models.stage import Stage
from app.models.user import User
from app.services.building_service import get_building_state


def save_result(
    db: Session,
    user_id: int,
    stage_id: int,
    score: int,
    correct_count: int | None,
    total_question: int,
) -> dict:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db.get(Stage, stage_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

    resolved_correct_count = correct_count if correct_count is not None else min(total_question, score // 10)
    accuracy = round((resolved_correct_count / total_question) * 100, 2)
    # 정답/오답과 상관없이 스테이지를 끝까지 풀면 클리어로 처리 (다음 단계 진행 가능)
    stage_clear = True

    result = Result(
        user_id=user_id,
        stage_id=stage_id,
        score=score,
        correct_count=resolved_correct_count,
        total_question=total_question,
    )
    history = History(user_id=user_id, stage_id=stage_id, score=score, accuracy=accuracy)

    progress = db.scalar(select(Progress).where(Progress.user_id == user_id, Progress.stage_id == stage_id))
    if progress is None:
        progress = Progress(user_id=user_id, stage_id=stage_id, cleared=stage_clear, score=score, accuracy=accuracy)
        db.add(progress)
    else:
        progress.cleared = progress.cleared or stage_clear
        progress.score = max(progress.score, score)
        progress.accuracy = max(progress.accuracy, accuracy)

    db.add(result)
    db.add(history)
    db.flush()
    level, _ = get_building_state(db, user_id)
    db.commit()

    return {"stage_clear": stage_clear, "building_level": level}
