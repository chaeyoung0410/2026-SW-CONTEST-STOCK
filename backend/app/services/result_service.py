from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.answer_attempt import AnswerAttempt
from app.models.history import History
from app.models.progress import Progress
from app.models.question import Question
from app.models.result import Result
from app.models.stage import Stage
from app.models.user import User
from app.services.building_service import get_building_state
from app.services.stage_service import ensure_stage_access


# 422 Unprocessable Entity 예외를 만드는 헬퍼
def _unprocessable(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detail,
    )


# submission_id로 이미 저장된 결과가 있는지 조회 (중복 제출 방지용)
def _find_result_by_submission(
    db: Session, user_id: int, submission_id: str | None
) -> Result | None:
    if submission_id is None:
        return None
    return db.scalar(
        select(Result).where(
            Result.user_id == user_id,
            Result.submission_id == submission_id,
        )
    )


# 같은 submission_id로 재요청됐을 때, 내용이 같으면 기존 결과를 그대로 응답
def _idempotent_result_response(
    db: Session,
    existing: Result,
    *,
    stage_id: int,
    score: int,
    correct_count: int,
    total_question: int,
) -> dict:
    if (
        existing.stage_id != stage_id
        or existing.score != score
        or existing.correct_count != correct_count
        or existing.total_question != total_question
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="submission_id was already used for a different result",
        )
    building_state = get_building_state(db, existing.user_id)
    return {"stage_clear": True, "building_level": building_state["level"]}


# 스테이지 결과 저장: 입력값 검증 → 제출된 답안 시도와 서버 기록 대조 →
# Result/History/Progress 갱신까지 한 트랜잭션으로 처리
def save_result(
    db: Session,
    user_id: int,
    stage_id: int,
    score: int,
    correct_count: int | None,
    total_question: int,
    answer_attempt_ids: list[int] | None = None,
    submission_id: str | None = None,
    recommendation_id: int | None = None,
) -> dict:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db.get(Stage, stage_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")
    ensure_stage_access(db, stage_id, user_id)

    if score < 0 or total_question <= 0 or score % 10 != 0:
        raise _unprocessable("Invalid result counts")
    resolved_correct_count = correct_count if correct_count is not None else score // 10
    if resolved_correct_count < 0 or resolved_correct_count > total_question:
        raise _unprocessable("correct_count cannot exceed total_question")
    if score != resolved_correct_count * 10:
        raise _unprocessable("score does not match correct_count")

    existing = _find_result_by_submission(db, user_id, submission_id)
    if existing is not None:
        return _idempotent_result_response(
            db,
            existing,
            stage_id=stage_id,
            score=score,
            correct_count=resolved_correct_count,
            total_question=total_question,
        )

    stage_question_count = int(
        db.scalar(
            select(func.count())
            .select_from(Question)
            .where(Question.stage_id == stage_id)
        )
        or 0
    )
    if stage_question_count == 0:
        raise _unprocessable("Stage has no questions")
    if total_question != stage_question_count:
        raise _unprocessable("total_question does not match the stage question count")

    answer_attempts: list[AnswerAttempt] = []
    if answer_attempt_ids is not None:
        if len(set(answer_attempt_ids)) != len(answer_attempt_ids):
            raise _unprocessable("answer_attempt_ids cannot contain duplicates")
        answer_attempts = list(
            db.scalars(
                select(AnswerAttempt).where(
                    AnswerAttempt.attempt_id.in_(answer_attempt_ids)
                )
            )
        )
        if len(answer_attempts) != len(answer_attempt_ids):
            raise _unprocessable("One or more answer attempts do not exist")
        if any(
            attempt.user_id != user_id or attempt.stage_id != stage_id
            for attempt in answer_attempts
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Answer attempt access denied",
            )
        if any(attempt.result_id is not None for attempt in answer_attempts):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="One or more answer attempts are already finalized",
            )
        if len({attempt.question_id for attempt in answer_attempts}) != stage_question_count:
            raise _unprocessable("Answer attempts do not cover every stage question")
        server_correct_count = sum(1 for attempt in answer_attempts if attempt.correct)
        server_score = server_correct_count * 10
        if server_correct_count != resolved_correct_count or server_score != score:
            raise _unprocessable("Submitted result does not match server answer records")

    if recommendation_id is not None:
        raise _unprocessable(
            "recommendation_id is only supported by the AI recommendation quiz endpoint"
        )

    accuracy = round((resolved_correct_count / total_question) * 100, 2)
    # Preserve the existing game rule: finishing a stage unlocks the next one.
    stage_clear = True
    result = Result(
        user_id=user_id,
        stage_id=stage_id,
        score=score,
        correct_count=resolved_correct_count,
        total_question=total_question,
        submission_id=submission_id,
    )
    history = History(
        user_id=user_id,
        stage_id=stage_id,
        score=score,
        accuracy=accuracy,
    )

    progress = db.scalar(
        select(Progress).where(
            Progress.user_id == user_id,
            Progress.stage_id == stage_id,
        )
    )
    if progress is None:
        progress = Progress(
            user_id=user_id,
            stage_id=stage_id,
            cleared=stage_clear,
            score=score,
            accuracy=accuracy,
        )
        db.add(progress)
    else:
        progress.cleared = progress.cleared or stage_clear
        progress.score = max(progress.score, score)
        progress.accuracy = max(progress.accuracy, accuracy)

    try:
        db.add(result)
        db.add(history)
        db.flush()
        for attempt in answer_attempts:
            attempt.result_id = result.result_id
        building_state = get_building_state(db, user_id)
        level = building_state["level"]
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = _find_result_by_submission(db, user_id, submission_id)
        if existing is None:
            raise
        return _idempotent_result_response(
            db,
            existing,
            stage_id=stage_id,
            score=score,
            correct_count=resolved_correct_count,
            total_question=total_question,
        )
    except Exception:
        db.rollback()
        raise

    return {"stage_clear": stage_clear, "building_level": level}
