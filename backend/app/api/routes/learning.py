from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.learning import (
    LearningResponse,
    RecommendationFeedbackRequest,
    RecommendationFeedbackResponse,
    RecommendationResponse,
)
from app.services.learning_service import get_learning
from app.services.recommend_service import get_recommendations, update_recommendation_feedback

router = APIRouter(tags=["Learning"])


@router.get("/learning/recommend", response_model=list[RecommendationResponse])
def get_recommended_learning(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=4, ge=1, le=10),
) -> list[dict]:
    return get_recommendations(db, current_user.user_id, limit=limit)


@router.patch(
    "/learning/recommendations/{recommendation_id}",
    response_model=RecommendationFeedbackResponse,
)
def update_recommendation(
    recommendation_id: int,
    request: RecommendationFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    history = update_recommendation_feedback(
        db,
        current_user.user_id,
        recommendation_id,
        request.clicked,
        request.learning_completed,
    )
    return {
        "recommendation_id": history.recommendation_id,
        "clicked": history.clicked,
        "learning_completed": history.learning_completed,
        "completed_at": history.completed_at,
    }


@router.get("/learning/{stage_id}", response_model=LearningResponse)
def get_learning_content(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return get_learning(db, stage_id, current_user.user_id)
