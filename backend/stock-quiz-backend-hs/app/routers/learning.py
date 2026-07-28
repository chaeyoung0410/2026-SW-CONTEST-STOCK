"""
4-2. 단계 클릭 팝업 / 5. 문제 풀이 화면 / 7. 결과 화면 대응 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import GameProgress, Question, QuestionAttempt, Stage, StageCompletion, User
from app.schemas import (
    LearningContentResponse,
    QuestionItem,
    QuestionListResponse,
    StageCompleteResponse,
    StageResultResponse,
    StageSummaryResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)

router = APIRouter(prefix="/learning", tags=["학습/문제풀이"])

MAX_LEVEL = 15


def _get_stage_or_404(db: Session, step_number: int) -> Stage:
    stage = db.query(Stage).filter(Stage.step_number == step_number).first()
    if not stage:
        raise HTTPException(status_code=404, detail=f"{step_number}번 단계를 찾을 수 없습니다.")
    return stage


def _count_correct(db: Session, user_id: int, step_number: int) -> tuple[int, int]:
    """해당 단계에서 유저가 맞춘 문제 수와 전체 문제 수를 반환"""
    question_ids = [q.id for q in db.query(Question.id).filter(Question.step_number == step_number).all()]
    total = len(question_ids)
    if total == 0:
        return 0, 0
    correct = (
        db.query(QuestionAttempt)
        .filter(
            QuestionAttempt.user_id == user_id,
            QuestionAttempt.question_id.in_(question_ids),
            QuestionAttempt.is_correct == True,  # noqa: E712
        )
        .count()
    )
    return correct, total


@router.get(
    "/{step_number}/summary",
    response_model=StageSummaryResponse,
    summary="4-2. 단계 클릭 시 팝업에 표시할 요약 정보",
)
def get_stage_summary(
    step_number: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    stage = _get_stage_or_404(db, step_number)
    total_questions = db.query(Question).filter(Question.step_number == step_number).count()
    is_completed = (
        db.query(StageCompletion)
        .filter(StageCompletion.user_id == current_user.id, StageCompletion.step_number == step_number)
        .first()
        is not None
    )
    return StageSummaryResponse(
        step_number=step_number,
        learning_content=stage.learning_content,
        total_questions=total_questions,
        is_completed=is_completed,
    )


@router.get(
    "/{step_number}/content",
    response_model=LearningContentResponse,
    summary="5-1. 학습 내용 표시",
)
def get_learning_content(step_number: int, db: Session = Depends(get_db)):
    stage = _get_stage_or_404(db, step_number)
    return LearningContentResponse(step_number=step_number, learning_content=stage.learning_content)


@router.get(
    "/{step_number}/questions",
    response_model=QuestionListResponse,
    summary="5-2. 해당 단계 문제 목록 (정답 미포함)",
)
def get_questions(step_number: int, db: Session = Depends(get_db)):
    _get_stage_or_404(db, step_number)
    questions = (
        db.query(Question).filter(Question.step_number == step_number).order_by(Question.id).all()
    )
    return QuestionListResponse(
        step_number=step_number,
        questions=[QuestionItem(question_id=q.id, question=q.question_text) for q in questions],
    )


@router.post(
    "/{step_number}/questions/{question_id}/submit",
    response_model=SubmitAnswerResponse,
    summary="5-3. 답안 제출",
)
def submit_answer(
    step_number: int,
    question_id: int,
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.step_number == step_number)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")

    is_correct = payload.answer.strip().lower() == question.answer.strip().lower()

    # 유저+문제 조합으로 기존 시도가 있으면 덮어쓰고, 없으면 새로 생성 (재도전 지원)
    attempt = (
        db.query(QuestionAttempt)
        .filter(QuestionAttempt.user_id == current_user.id, QuestionAttempt.question_id == question_id)
        .first()
    )
    if attempt:
        attempt.is_correct = is_correct
    else:
        db.add(QuestionAttempt(user_id=current_user.id, question_id=question_id, is_correct=is_correct))
    db.commit()

    if is_correct:
        return SubmitAnswerResponse(is_correct=True, message="정답입니다!")
    return SubmitAnswerResponse(
        is_correct=False, message="아쉽지만 오답이에요.", correct_answer=question.answer
    )


@router.get(
    "/{step_number}/result",
    response_model=StageResultResponse,
    summary="7-1. 단계 결과(맞춘 개수) 조회",
)
def get_result(
    step_number: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    _get_stage_or_404(db, step_number)
    correct, total = _count_correct(db, current_user.id, step_number)
    return StageResultResponse(step_number=step_number, total_questions=total, correct_count=correct)


@router.post(
    "/{step_number}/complete",
    response_model=StageCompleteResponse,
    summary="7-2. 종료 버튼 - 단계 완료 처리 및 레벨업",
)
def complete_stage(
    step_number: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    _get_stage_or_404(db, step_number)
    correct, total = _count_correct(db, current_user.id, step_number)

    completion = (
        db.query(StageCompletion)
        .filter(StageCompletion.user_id == current_user.id, StageCompletion.step_number == step_number)
        .first()
    )
    if completion:
        completion.correct_count = correct
        completion.total_questions = total
    else:
        db.add(
            StageCompletion(
                user_id=current_user.id,
                step_number=step_number,
                correct_count=correct,
                total_questions=total,
            )
        )

    progress = db.query(GameProgress).filter(GameProgress.user_id == current_user.id).first()
    leveled_up = False
    # 지금 막 완료한 단계가 "현재 진행 중이던 단계"였을 때만 레벨업 (재도전 시 중복 레벨업 방지)
    if step_number == progress.level and progress.level < MAX_LEVEL:
        progress.level += 1
        progress.total_score += correct * 10
        leveled_up = True

    db.commit()

    return StageCompleteResponse(step_number=step_number, level=progress.level, leveled_up=leveled_up)
