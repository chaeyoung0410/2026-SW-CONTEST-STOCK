from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.answer_attempt import AnswerAttempt
from app.models.question import Question
from app.models.user import User
from app.services.stage_service import ensure_stage_access


# 스테이지 접근 권한 확인 후 해당 스테이지의 문제 목록 조회
def get_questions(db: Session, stage_id: int, user_id: int | None = None) -> list[dict]:
    ensure_stage_access(db, stage_id, user_id)
    questions = db.scalars(
        select(Question).where(Question.stage_id == stage_id).order_by(Question.question_id)
    )
    return [
        {
            "question_id": question.question_id,
            "question": question.question,
            "choices": [question.choice1, question.choice2, question.choice3, question.choice4],
            "tag": question.tag,
        }
        for question in questions
    ]


CHOICE_FIELDS = {1: "choice1", 2: "choice2", 3: "choice3", 4: "choice4"}


# 답안 채점 및 시도 기록 저장. submission_id로 중복 제출을 idempotent하게 처리
def submit_answer(
    db: Session,
    user_id: int,
    question_id: int,
    answer: int,
    submission_id: str | None = None,
) -> dict:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    ensure_stage_access(db, question.stage_id, user_id)

    if submission_id is not None:
        existing = db.scalar(
            select(AnswerAttempt).where(
                AnswerAttempt.user_id == user_id,
                AnswerAttempt.submission_id == submission_id,
            )
        )
        if existing is not None:
            # 같은 키를 다른 문제에 재사용하는 것은 잘못된 요청으로 차단한다.
            if existing.question_id != question_id or existing.selected_answer != answer:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="submission_id was already used for a different answer",
                )
            return _answer_payload(question, existing.correct, existing.attempt_id)

    correct = question.answer == answer
    attempt = AnswerAttempt(
        user_id=user_id,
        question_id=question.question_id,
        stage_id=question.stage_id,
        selected_answer=answer,
        correct=correct,
        submission_id=submission_id,
    )
    db.add(attempt)
    try:
        db.commit()
        db.refresh(attempt)
    except IntegrityError:
        db.rollback()
        # 동시 재전송이 unique 제약에 걸린 경우 기존 결과를 idempotent하게 반환한다.
        if submission_id is not None:
            existing = db.scalar(
                select(AnswerAttempt).where(
                    AnswerAttempt.user_id == user_id,
                    AnswerAttempt.submission_id == submission_id,
                )
            )
            if existing is not None:
                if existing.question_id != question_id or existing.selected_answer != answer:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="submission_id was already used for a different answer",
                    )
                return _answer_payload(question, existing.correct, existing.attempt_id)
        raise
    except Exception:
        db.rollback()
        raise

    return _answer_payload(question, correct, attempt.attempt_id)


# 채점 결과 응답(정오답/점수/해설/정답)을 조립
def _answer_payload(question: Question, correct: bool, attempt_id: int) -> dict:
    return {
        "correct": correct,
        "score": 10 if correct else 0,
        "explanation": question.explanation,
        "correct_answer": getattr(question, CHOICE_FIELDS[question.answer]),
        "attempt_id": attempt_id,
    }
