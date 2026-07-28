"""
4. 게임 화면(홈) 대응 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import GameProgress, Stage, StageCompletion, User
from app.schemas import GameBoardResponse, StageStatus

router = APIRouter(prefix="/game", tags=["게임 화면"])


@router.get("/board", response_model=GameBoardResponse, summary="현재 보드 상태 + 단계별 완료 여부")
def get_board(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    progress = db.query(GameProgress).filter(GameProgress.user_id == current_user.id).first()

    completed_steps = {
        c.step_number
        for c in db.query(StageCompletion).filter(StageCompletion.user_id == current_user.id).all()
    }

    all_steps = [s.step_number for s in db.query(Stage.step_number).order_by(Stage.step_number).all()]

    stages = [
        StageStatus(step_number=step, completed=step in completed_steps) for step in all_steps
    ]

    return GameBoardResponse(
        level=progress.level,
        board_position=progress.board_position,
        total_score=progress.total_score,
        stages=stages,
    )
