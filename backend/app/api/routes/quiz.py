from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import ensure_same_user, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.quiz import AnswerRequest, AnswerResponse, QuestionResponse
from app.services.quiz_service import get_questions, submit_answer

router = APIRouter(tags=["Quiz"])


@router.get("/question/{stage_id}", response_model=list[QuestionResponse])
def get_stage_questions(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return get_questions(db, stage_id, current_user.user_id)


@router.post("/answer", response_model=AnswerResponse)
def submit_quiz_answer(
    request: AnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    ensure_same_user(request.user_id, current_user)
    return submit_answer(db, current_user.user_id, request.question_id, request.answer)
