from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.stage import StageResponse
from app.services.stage_service import get_stage_list

router = APIRouter(tags=["Stage"])


# 전체 스테이지 목록(잠금/클리어 상태 포함) 조회
@router.get("/stage", response_model=list[StageResponse])
def get_stages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return get_stage_list(db, current_user.user_id)
