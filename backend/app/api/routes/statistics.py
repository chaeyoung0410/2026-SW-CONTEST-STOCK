from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.statistics import UserStatisticsResponse
from app.services.statistics_service import get_user_statistics

router = APIRouter(tags=["Statistics"])


@router.get("/users/me/statistics", response_model=UserStatisticsResponse)
def get_my_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return get_user_statistics(db, current_user.user_id)
