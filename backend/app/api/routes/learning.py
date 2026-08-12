from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.learning import (
    LearningResponse,
    RecommendationInteractionResponse,
    RecommendationResponse,
)
from app.schemas.recommendation_quiz import (
    RecommendationQuizCompletionRequest,
    RecommendationQuizCompletionResponse,
    RecommendationQuizResponse,
)
from app.services.learning_service import get_learning
from app.services.recommend_service import (
    get_recommendations,
    record_recommendation_interaction,
)
from app.services.recommendation_quiz_service import (
    complete_recommendation_quiz,
    generate_quiz_for_recommendation,
)

router = APIRouter(tags=["Learning"])


@router.get("/learning/recommend", response_model=list[RecommendationResponse])
def get_recommended_learning(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=4, ge=1, le=10),
) -> list[dict]:
    return get_recommendations(db, current_user.user_id, limit=limit)


@router.post(
    "/learning/recommendations/{recommendation_id}/quiz",
    response_model=RecommendationQuizResponse,
)
def generate_recommendation_quiz_questions(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return generate_quiz_for_recommendation(db, current_user.user_id, recommendation_id)


@router.post(
    "/learning/recommendations/{recommendation_id}/quiz/complete",
    response_model=RecommendationQuizCompletionResponse,
)
def submit_recommendation_quiz_result(
    recommendation_id: int,
    request: RecommendationQuizCompletionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return complete_recommendation_quiz(
        db,
        current_user.user_id,
        recommendation_id,
        request.correct_count,
        request.total_questions,
    )


def _record_interaction(
    interaction: str,
    recommendation_id: int,
    db: Session,
    current_user: User,
) -> dict:
    result = record_recommendation_interaction(
        db,
        current_user.user_id,
        recommendation_id,
        interaction,
    )
    history = result.history
    return {
        "recommendation_id": history.recommendation_id,
        "interaction": result.interaction,
        "already_applied": result.already_applied,
        "clicked": history.clicked,
        "clicked_at": history.clicked_at,
        "learning_started": history.learning_started,
        "started_at": history.started_at,
        "learning_completed": history.learning_completed,
        "completed_at": history.completed_at,
    }


@router.post(
    "/learning/recommendations/{recommendation_id}/click",
    response_model=RecommendationInteractionResponse,
)
def click_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return _record_interaction("click", recommendation_id, db, current_user)


@router.post(
    "/learning/recommendations/{recommendation_id}/start",
    response_model=RecommendationInteractionResponse,
)
def start_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return _record_interaction("start", recommendation_id, db, current_user)


@router.get("/learning/{stage_id}", response_model=LearningResponse)
def get_learning_content(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    return get_learning(db, stage_id, current_user.user_id)
