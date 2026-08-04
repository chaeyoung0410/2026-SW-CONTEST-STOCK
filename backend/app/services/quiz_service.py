from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.services.recommend_service import record_wrong_answer
from app.services.stage_service import ensure_stage_access


def get_questions(db: Session, stage_id: int, user_id: int | None = None) -> list[dict]:
    ensure_stage_access(db, stage_id, user_id)
    questions = db.scalars(select(Question).where(Question.stage_id == stage_id).order_by(Question.question_id))
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


def submit_answer(db: Session, user_id: int, question_id: int, answer: int) -> dict:
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    correct = question.answer == answer
    if not correct:
        record_wrong_answer(db, user_id, question.stage_id)
        db.commit()

    return {
        "correct": correct,
        "score": 10 if correct else 0,
        "explanation": question.explanation,
        "correct_answer": getattr(question, CHOICE_FIELDS[question.answer]),
    }
