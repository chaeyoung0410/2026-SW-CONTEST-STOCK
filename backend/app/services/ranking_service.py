from sqlalchemy import case, desc, func, select
from sqlalchemy.orm import Session

from app.models.progress import Progress
from app.models.user import User


def get_ranking(db: Session, limit: int = 10) -> list[dict]:
    total_score = func.coalesce(func.sum(Progress.score), 0).label("total_score")
    cleared_stage_count = func.coalesce(
        func.sum(case((Progress.cleared.is_(True), 1), else_=0)),
        0,
    ).label("cleared_stage_count")

    statement = (
        select(User.nickname, total_score, cleared_stage_count)
        .join(Progress, Progress.user_id == User.user_id, isouter=True)
        .group_by(User.user_id, User.nickname)
        .order_by(desc(cleared_stage_count), desc(total_score), User.nickname)
        .limit(limit)
    )

    rows = db.execute(statement).all()
    return [
        {
            "rank": index + 1,
            "nickname": nickname,
            "score": int(score),
            "cleared_stage_count": int(cleared_count),
        }
        for index, (nickname, score, cleared_count) in enumerate(rows)
    ]
