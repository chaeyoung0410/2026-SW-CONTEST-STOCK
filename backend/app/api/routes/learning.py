from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.learning import LearningResponse
from app.services.learning_service import get_learning
from app.services.recommend_service import get_recommendations

router = APIRouter(tags=["Learning"])


@router.get("/learning/recommend", response_model=list[LearningResponse])
def get_recommended_learning(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return get_recommendations(db, current_user.user_id)


@router.get("/learning/{stage_id}", response_model=LearningResponse)
def get_learning_content(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return get_learning(db, stage_id, current_user.user_id)
