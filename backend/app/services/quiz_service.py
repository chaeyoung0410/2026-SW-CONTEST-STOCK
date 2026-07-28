from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.services.stage_service import ensure_stage_access


def get_questions(db: Session, stage_id: int, user_id: int | None = None) -> list[dict]:
    ensure_stage_access(db, stage_id, user_id)
    questions = db.scalars(select(Question).where(Question.stage_id == stage_id).order_by(Question.question_id))
    return [
        {
            "question_id": question.question_id,
            "question": question.question,
            "choices": [question.choice1, question.choice2, question.choice3, question.choice4],
        }
        for question in questions
    ]


def submit_answer(db: Session, question_id: int, answer: int) -> dict:
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    correct = question.answer == answer
    return {
        "correct": correct,
        "score": 10 if correct else 0,
        "explanation": question.explanation,
    }
