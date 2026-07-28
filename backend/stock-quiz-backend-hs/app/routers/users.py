"""
8. 마이페이지 대응 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import GameProgress, StageCompletion, User
from app.routers.learning import MAX_LEVEL
from app.schemas import BuildingItem, HistoryItem, MyBuildingsResponse, MyHistoryResponse, MyInfoResponse

router = APIRouter(prefix="/users", tags=["마이페이지"])


@router.get("/me", response_model=MyInfoResponse, summary="8-1. 내 정보")
def get_my_info(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    progress = db.query(GameProgress).filter(GameProgress.user_id == current_user.id).first()
    return MyInfoResponse(
        user_id=current_user.user_id,
        nickname=current_user.nickname,
        level=progress.level,
        total_score=progress.total_score,
        joined_at=current_user.created_at,
    )


@router.get("/me/buildings", response_model=MyBuildingsResponse, summary="8-2. 나의 건물")
def get_my_buildings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    progress = db.query(GameProgress).filter(GameProgress.user_id == current_user.id).first()
    buildings = [
        BuildingItem(level=lv, unlocked=lv <= progress.level) for lv in range(1, MAX_LEVEL + 1)
    ]
    return MyBuildingsResponse(current_level=progress.level, buildings=buildings)


@router.get("/me/history", response_model=MyHistoryResponse, summary="8-3. 학습 기록 조회")
def get_my_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    completions = (
        db.query(StageCompletion)
        .filter(StageCompletion.user_id == current_user.id)
        .order_by(StageCompletion.completed_at)
        .all()
    )
    return MyHistoryResponse(
        history=[
            HistoryItem(
                step_number=c.step_number,
                correct_count=c.correct_count,
                total_questions=c.total_questions,
                completed_at=c.completed_at,
            )
            for c in completions
        ]
    )
