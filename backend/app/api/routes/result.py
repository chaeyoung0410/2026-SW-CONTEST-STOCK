from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import ensure_same_user, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.result import ResultRequest, ResultResponse
from app.services.result_service import save_result

router = APIRouter(tags=["Result"])


@router.post("/result", response_model=ResultResponse)
def save_stage_result(
    request: ResultRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    ensure_same_user(request.user_id, current_user)
    return save_result(
        db,
        request.user_id,
        request.stage_id,
        request.score,
        request.correct_count,
        request.total_question,
    )
