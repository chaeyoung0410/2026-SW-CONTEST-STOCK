from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.wrong_answer import WrongAnswer
from app.services.learning_service import get_learning


def record_wrong_answer(db: Session, user_id: int, stage_id: int) -> None:
    db.add(WrongAnswer(user_id=user_id, stage_id=stage_id))


def get_recommended_stage_ids(db: Session, user_id: int) -> list[int]:
    last_wrong_at = func.max(WrongAnswer.created_at)
    rows = db.execute(
        select(WrongAnswer.stage_id)
        .where(WrongAnswer.user_id == user_id)
        .group_by(WrongAnswer.stage_id)
        .order_by(last_wrong_at.desc())
    ).all()
    return [row[0] for row in rows]


def get_recommendations(db: Session, user_id: int) -> list[dict]:
    stage_ids = get_recommended_stage_ids(db, user_id)
    return [get_learning(db, stage_id, None) for stage_id in stage_ids]
