from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.history import History
from app.models.stage import Stage


# 사용자의 스테이지별 플레이 기록(점수/정답률)을 최신순으로 조회
def get_history(db: Session, user_id: int) -> list[dict]:
    statement = (
        select(Stage.title, History.score, History.accuracy)
        .join(Stage, Stage.stage_id == History.stage_id)
        .where(History.user_id == user_id)
        .order_by(desc(History.play_time))
    )
    return [
        {"stage": title, "score": score, "accuracy": accuracy}
        for title, score, accuracy in db.execute(statement).all()
    ]
