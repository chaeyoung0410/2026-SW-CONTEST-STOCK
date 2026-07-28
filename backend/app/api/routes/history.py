from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.history import HistoryResponse
from app.services.history_service import get_history

router = APIRouter(tags=["History"])


@router.get("/history", response_model=list[HistoryResponse])
def get_learning_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return get_history(db, current_user.user_id)
