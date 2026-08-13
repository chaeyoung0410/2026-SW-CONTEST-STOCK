from collections.abc import Callable
from datetime import datetime, timezone

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.recommendation_history import RecommendationHistory
from app.models.stage import Stage
from app.schemas.recommendation_quiz import GeminiRecommendationQuestionSet
from app.services.gemini_service import (
    GeminiNotConfiguredError,
    GeminiRateLimitError,
    GeminiServiceError,
    RecommendationQuizSource,
    generate_recommendation_quiz,
)
from app.services.recommend_service import record_recommendation_interaction

Generator = Callable[[RecommendationQuizSource], GeminiRecommendationQuestionSet]


def generate_quiz_for_recommendation(
    db: Session,
    user_id: int,
    recommendation_id: int,
    *,
    generator: Generator = generate_recommendation_quiz,
) -> dict:
    """카드를 클릭한 시점에만 Gemini 문제를 만들며 생성 결과는 저장하지 않는다."""

    history = _get_owned_history(db, user_id, recommendation_id)
    if history.learning_completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Recommendation is already completed",
        )

    stage = db.get(Stage, history.stage_id)
    if stage is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

    questions = list(
        db.scalars(
            select(Question)
            .where(Question.stage_id == stage.stage_id)
            .order_by(Question.question_id)
        )
    )
    topic = questions[0].tag if questions else stage.title
    source = RecommendationQuizSource(
        stage_id=stage.stage_id,
        stage_title=stage.title,
        stage_description=stage.description,
        stage_difficulty=stage.difficulty,
        topic=topic,
        sample_questions=[question.question for question in questions[:5]],
    )

    record_recommendation_interaction(db, user_id, recommendation_id, "click")
    try:
        generated = GeminiRecommendationQuestionSet.model_validate(generator(source))
    except GeminiNotConfiguredError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini 문제 생성 기능이 설정되지 않았습니다.",
        ) from error
    except GeminiRateLimitError as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI 문제 생성 요청이 많습니다. 잠시 후 다시 시도해 주세요.",
        ) from error
    except (GeminiServiceError, ValidationError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 문제를 생성하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 문제를 생성하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from error

    record_recommendation_interaction(db, user_id, recommendation_id, "start")
    return {
        "recommendation_id": recommendation_id,
        "stage_id": stage.stage_id,
        "topic": topic,
        "questions": generated.questions,
    }


# 추천 퀴즈 채점: 3문제 중 2문제 이상 정답이면 통과 처리하고 추천 완료 상태로 기록
def complete_recommendation_quiz(
    db: Session,
    user_id: int,
    recommendation_id: int,
    correct_count: int,
    total_questions: int,
    *,
    now: datetime | None = None,
) -> dict:
    history = _get_owned_history(db, user_id, recommendation_id)
    passed = total_questions == 3 and correct_count >= 2

    if passed and not history.learning_completed:
        completed_at = _as_utc(now or datetime.now(timezone.utc))
        history.clicked = True
        history.clicked_at = history.clicked_at or completed_at
        history.learning_started = True
        history.started_at = history.started_at or completed_at
        history.learning_completed = True
        history.completed_at = completed_at
        try:
            db.commit()
            db.refresh(history)
        except Exception:
            db.rollback()
            raise

    return {
        "recommendation_id": recommendation_id,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "passed": passed,
        "learning_completed": history.learning_completed,
    }


# 추천 기록 조회 + 소유자 검증 (없으면 404, 남의 것이면 403)
def _get_owned_history(
    db: Session, user_id: int, recommendation_id: int
) -> RecommendationHistory:
    history = db.get(RecommendationHistory, recommendation_id)
    if history is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    if history.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Recommendation access denied")
    return history


# tz 정보가 없는 datetime을 UTC로 간주해 비교 가능하게 정규화
def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
