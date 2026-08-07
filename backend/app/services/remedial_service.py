import logging
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.answer_attempt import AnswerAttempt
from app.models.question import Question
from app.models.remedial_question_cache import RemedialQuestionCache
from app.models.stage import Stage
from app.schemas.remedial import GeminiRemedialQuestionSet, RemedialQuestionsResponse
from app.services.gemini_service import (
    GeminiNotConfiguredError,
    GeminiRateLimitError,
    GeminiServiceError,
    RemedialQuestionSource,
    generate_remedial_questions,
)

logger = logging.getLogger(__name__)

Generator = Callable[[RemedialQuestionSource], GeminiRemedialQuestionSet]
UNAVAILABLE_MESSAGE = "추가 학습 문제를 현재 생성할 수 없습니다. 잠시 후 다시 시도해 주세요."
DISABLED_MESSAGE = "추가 학습 문제 기능이 현재 비활성화되어 있습니다."
RATE_LIMIT_MESSAGE = "추가 학습 문제 요청이 잠시 많습니다. 기존 게임은 계속 이용할 수 있습니다."


def get_or_generate_remedial_questions(
    db: Session,
    user_id: int,
    question_id: int,
    *,
    generator: Generator = generate_remedial_questions,
    now: datetime | None = None,
) -> RemedialQuestionsResponse:
    """실제 오답을 확인하고 사용자+문제 단위로 생성 결과를 재사용한다."""

    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    wrong_attempt = db.scalar(
        select(AnswerAttempt)
        .where(
            AnswerAttempt.user_id == user_id,
            AnswerAttempt.question_id == question_id,
            AnswerAttempt.correct.is_(False),
        )
        .order_by(AnswerAttempt.created_at.desc(), AnswerAttempt.attempt_id.desc())
    )
    if wrong_attempt is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Remedial questions require an incorrect answer",
        )

    stage = db.get(Stage, question.stage_id)
    if stage is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

    generated_at = _as_utc(now or datetime.now(timezone.utc))
    cache = _get_cache(db, user_id, question_id)
    cached_response = _read_ready_cache(cache)
    if cached_response is not None:
        return cached_response

    if cache is not None and _retry_is_active(cache, generated_at):
        return _unavailable_response(cached=True)

    cache, claimed = _claim_generation(
        db,
        cache,
        user_id=user_id,
        question=question,
        now=generated_at,
    )
    if not claimed:
        cached_response = _read_ready_cache(cache)
        return cached_response or _unavailable_response(cached=True)

    source = RemedialQuestionSource(
        stage_id=stage.stage_id,
        stage_title=stage.title,
        stage_description=stage.description,
        stage_difficulty=stage.difficulty,
        question=question.question,
        choices=[question.choice1, question.choice2, question.choice3, question.choice4],
        correct_answer_index=question.answer - 1,
        correct_answer_text=getattr(question, f"choice{question.answer}"),
        topic=question.tag,
        explanation=question.explanation,
    )

    try:
        generated = GeminiRemedialQuestionSet.model_validate(generator(source))
        if any(
            _normalize_text(item.question) == _normalize_text(source.question)
            for item in generated.questions
        ):
            raise GeminiServiceError("copied_source_question")
    except GeminiNotConfiguredError:
        _mark_unavailable(db, cache, generated_at)
        return _unavailable_response(cached=False, message=DISABLED_MESSAGE)
    except GeminiRateLimitError:
        _mark_unavailable(
            db,
            cache,
            generated_at,
            cooldown_seconds=settings.gemini_rate_limit_cooldown_seconds,
        )
        return _unavailable_response(cached=False, message=RATE_LIMIT_MESSAGE)
    except (GeminiServiceError, ValidationError):
        _mark_unavailable(db, cache, generated_at)
        return _unavailable_response(cached=False)
    except Exception as error:
        # 주입된 생성기나 예상 밖 SDK 오류도 정답 제출 흐름으로 전파하지 않는다.
        logger.warning("Unexpected remedial generator failure (%s)", type(error).__name__)
        _mark_unavailable(db, cache, generated_at)
        return _unavailable_response(cached=False)

    cache.status = "ready"
    cache.payload_json = generated.model_dump_json()
    cache.model_name = settings.gemini_model
    cache.retry_after = None
    cache.updated_at = generated_at
    try:
        db.commit()
        db.refresh(cache)
    except Exception:
        db.rollback()
        logger.warning("Failed to persist remedial question cache")
        return RemedialQuestionsResponse(
            questions=generated.questions,
            available=True,
            cached=False,
        )

    return RemedialQuestionsResponse(
        questions=generated.questions,
        available=True,
        cached=False,
    )


def _get_cache(
    db: Session, user_id: int, question_id: int
) -> RemedialQuestionCache | None:
    return db.scalar(
        select(RemedialQuestionCache).where(
            RemedialQuestionCache.user_id == user_id,
            RemedialQuestionCache.source_question_id == question_id,
        )
    )


def _read_ready_cache(
    cache: RemedialQuestionCache | None,
) -> RemedialQuestionsResponse | None:
    if cache is None or cache.status != "ready" or not cache.payload_json:
        return None
    try:
        payload = GeminiRemedialQuestionSet.model_validate_json(cache.payload_json)
    except ValidationError:
        logger.warning("Ignoring invalid remedial question cache payload")
        return None
    return RemedialQuestionsResponse(
        questions=payload.questions,
        available=True,
        cached=True,
    )


def _claim_generation(
    db: Session,
    cache: RemedialQuestionCache | None,
    *,
    user_id: int,
    question: Question,
    now: datetime,
) -> tuple[RemedialQuestionCache, bool]:
    pending_until = now + timedelta(
        seconds=max(int(settings.gemini_timeout_seconds * 2), 30)
    )
    if cache is None:
        cache = RemedialQuestionCache(
            user_id=user_id,
            source_question_id=question.question_id,
            stage_id=question.stage_id,
            status="pending",
            retry_after=pending_until,
            model_name=settings.gemini_model,
            created_at=now,
            updated_at=now,
        )
        db.add(cache)
    else:
        cache.status = "pending"
        cache.payload_json = None
        cache.retry_after = pending_until
        cache.model_name = settings.gemini_model
        cache.updated_at = now

    try:
        db.commit()
        db.refresh(cache)
        return cache, True
    except IntegrityError:
        db.rollback()
        concurrent_cache = _get_cache(db, user_id, question.question_id)
        if concurrent_cache is None:
            raise
        return concurrent_cache, False


def _mark_unavailable(
    db: Session,
    cache: RemedialQuestionCache,
    now: datetime,
    *,
    cooldown_seconds: int | None = None,
) -> None:
    cache.status = "unavailable"
    cache.payload_json = None
    cache.retry_after = now + timedelta(
        seconds=cooldown_seconds or settings.gemini_retry_cooldown_seconds
    )
    cache.updated_at = now
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.warning("Failed to persist remedial generation cooldown")


def _retry_is_active(cache: RemedialQuestionCache, now: datetime) -> bool:
    return cache.retry_after is not None and _as_utc(cache.retry_after) > now


def _unavailable_response(
    *, cached: bool, message: str = UNAVAILABLE_MESSAGE
) -> RemedialQuestionsResponse:
    return RemedialQuestionsResponse(
        questions=[],
        available=False,
        cached=cached,
        message=message,
    )


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_text(value: str) -> str:
    return "".join(value.lower().split())
