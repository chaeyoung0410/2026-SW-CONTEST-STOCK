from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer_attempt import AnswerAttempt
from app.models.learning import Learning
from app.models.progress import Progress
from app.models.question import Question
from app.models.recommendation_history import RecommendationHistory
from app.models.result import Result
from app.models.stage import Stage
from app.models.user import User
from app.models.wrong_answer import WrongAnswer

DEFAULT_RECOMMENDATION_LIMIT = 4


@dataclass
class TopicStats:
    total_attempts: int = 0
    correct_count: int = 0
    wrong_count: int = 0
    last_wrong_at: datetime | None = None

    @property
    def accuracy(self) -> float | None:
        if self.total_attempts == 0:
            return None
        return round((self.correct_count / self.total_attempts) * 100, 2)

    @property
    def wrong_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return round((self.wrong_count / self.total_attempts) * 100, 2)


@dataclass(frozen=True)
class RecommendationInteractionResult:
    history: RecommendationHistory
    interaction: str
    already_applied: bool


def get_recommendations(
    db: Session,
    user_id: int,
    limit: int = DEFAULT_RECOMMENDATION_LIMIT,
    now: datetime | None = None,
) -> list[dict]:
    """누적 오답률 상위 주제를 반환하고 추천 노출 이력을 저장한다."""
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not 1 <= limit <= 10:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="limit must be 1-10")

    now = _as_utc(now or datetime.now(timezone.utc))
    stages = list(db.scalars(select(Stage).order_by(Stage.stage_id)))
    if not stages:
        return []

    stats = _collect_topic_stats(db, user_id)
    current_stage_id = _get_current_stage_id(db, user_id, stages)
    # 잠긴 미래 단계는 추천하지 않는다. 완료한 이전 단계와 현재 접근 가능한 단계만 후보로 둔다.
    candidates = [stage for stage in stages if stage.stage_id <= current_stage_id]
    learning_by_stage = _get_learning_by_stage(db, candidates)
    topics = _get_topics(db, candidates)
    history_by_stage = _get_recent_history(db, user_id)

    ranked: list[dict] = []
    for stage in candidates:
        stage_stats = stats.get(stage.stage_id, TopicStats())
        if stage_stats.wrong_count == 0:
            continue

        histories = history_by_stage.get(stage.stage_id, [])
        last_completion = next((item for item in histories if item.learning_completed), None)
        # 완료 이후 새 오답이 생긴 경우에만 같은 주제를 다시 후보에 올린다.
        if (
            last_completion is not None
            and last_completion.completed_at is not None
            and (
                stage_stats.last_wrong_at is None
                or _as_utc(stage_stats.last_wrong_at)
                <= _as_utc(last_completion.completed_at)
            )
        ):
            continue

        pages = learning_by_stage.get(stage.stage_id, [])
        topic = topics.get(stage.stage_id, stage.title)
        reason = (
            f"{topic} 누적 {stage_stats.total_attempts}회 풀이 중 "
            f"{stage_stats.wrong_count}회 오답으로 오답률 {stage_stats.wrong_rate:.0f}%입니다."
        )
        ranked.append(
            {
                "stage": stage,
                "pages": pages,
                "topic": topic,
                "stats": stage_stats,
                "score": stage_stats.wrong_rate,
                "reason": reason,
                "recently_recommended": bool(histories),
            }
        )

    ranked.sort(
        key=lambda item: (
            -item["stats"].wrong_rate,
            -item["stats"].wrong_count,
            item["stage"].stage_id,
        )
    )
    selected = ranked[:limit]

    try:
        response: list[dict] = []
        for priority, item in enumerate(selected, start=1):
            stage = item["stage"]
            pages = item["pages"]
            stage_stats = item["stats"]
            learning_id = pages[0].learning_id if pages else None
            history = RecommendationHistory(
                user_id=user_id,
                stage_id=stage.stage_id,
                learning_id=learning_id,
                priority=priority,
                recommendation_score=item["score"],
                reason=item["reason"],
                recommended_at=now,
                baseline_accuracy=stage_stats.accuracy,
                baseline_score=stage_stats.correct_count * 10,
                baseline_wrong_count=stage_stats.wrong_count,
                is_default_recommendation=False,
            )
            db.add(history)
            db.flush()
            response.append(
                {
                    "stage_id": stage.stage_id,
                    "title": pages[0].title if pages else stage.title,
                    "content": "\n\n".join(page.content for page in pages) or stage.description,
                    "pages": pages,
                    "recommendation_id": history.recommendation_id,
                    "content_id": learning_id or stage.stage_id,
                    "priority": priority,
                    "recommendation_score": item["score"],
                    "recommendation_reason": item["reason"],
                    "weak_topic": item["topic"],
                    "current_accuracy": stage_stats.accuracy,
                    "wrong_rate": stage_stats.wrong_rate,
                    "total_attempts": stage_stats.total_attempts,
                    "correct_count": stage_stats.correct_count,
                    "wrong_count": stage_stats.wrong_count,
                    "difficulty": stage.difficulty,
                    "recently_recommended": item["recently_recommended"],
                }
            )
        db.commit()
        return response
    except Exception:
        db.rollback()
        raise


# 추천 콘텐츠의 클릭/학습 시작 상태를 기록 (이미 적용된 경우 already_applied=True로 알림)
def record_recommendation_interaction(
    db: Session,
    user_id: int,
    recommendation_id: int,
    interaction: str,
    now: datetime | None = None,
) -> RecommendationInteractionResult:
    if interaction not in {"click", "start"}:
        raise ValueError("Unsupported recommendation interaction")
    history = _get_owned_recommendation(db, user_id, recommendation_id)
    updated_at = _as_utc(now or datetime.now(timezone.utc))
    already_applied = {
        "click": history.clicked,
        "start": history.learning_started,
    }[interaction]

    if not already_applied:
        if not history.clicked:
            history.clicked = True
            history.clicked_at = updated_at
        if interaction == "start" and not history.learning_started:
            history.learning_started = True
            history.started_at = updated_at

    try:
        db.commit()
        db.refresh(history)
    except Exception:
        db.rollback()
        raise
    return RecommendationInteractionResult(
        history=history,
        interaction=interaction,
        already_applied=already_applied,
    )


# 추천 기록 조회 + 소유자 검증 (없으면 404, 남의 것이면 403)
def _get_owned_recommendation(
    db: Session, user_id: int, recommendation_id: int
) -> RecommendationHistory:
    history = db.get(RecommendationHistory, recommendation_id)
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RECOMMENDATION_NOT_FOUND",
                "message": "추천 기록을 찾을 수 없습니다.",
                "details": {"recommendation_id": recommendation_id},
            },
        )
    if history.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "RECOMMENDATION_ACCESS_DENIED",
                "message": "다른 사용자의 추천 기록은 수정할 수 없습니다.",
                "details": {"recommendation_id": recommendation_id},
            },
        )
    return history


def _collect_topic_stats(db: Session, user_id: int) -> dict[int, TopicStats]:
    """answer_attempt, result, legacy wrong_answer 순으로 중복 없이 집계한다."""
    stats: dict[int, TopicStats] = {}
    attempts = list(
        db.scalars(
            select(AnswerAttempt)
            .where(AnswerAttempt.user_id == user_id)
            .order_by(AnswerAttempt.created_at)
        )
    )
    result_ids_covered_by_attempts: set[int] = set()
    stages_with_attempts: set[int] = set()
    for attempt in attempts:
        item = stats.setdefault(attempt.stage_id, TopicStats())
        stages_with_attempts.add(attempt.stage_id)
        if attempt.result_id is not None:
            result_ids_covered_by_attempts.add(attempt.result_id)
        item.total_attempts += 1
        if attempt.correct:
            item.correct_count += 1
        else:
            item.wrong_count += 1
            item.last_wrong_at = _latest(item.last_wrong_at, attempt.created_at)

    results = list(db.scalars(select(Result).where(Result.user_id == user_id)))
    stages_with_results: set[int] = set()
    for result in results:
        # New results are linked to their per-question AnswerAttempt rows. Only
        # legacy/unlinked results are added, preserving old history without
        # double-counting newly finalized quizzes.
        if result.result_id in result_ids_covered_by_attempts:
            continue
        stages_with_results.add(result.stage_id)
        item = stats.setdefault(result.stage_id, TopicStats())
        correct_count = min(max(result.correct_count, 0), result.total_question)
        item.total_attempts += result.total_question
        item.correct_count += correct_count
        item.wrong_count += result.total_question - correct_count
        if result.total_question - correct_count > 0:
            item.last_wrong_at = _latest(item.last_wrong_at, result.created_at)

    legacy_wrong_answers = list(db.scalars(select(WrongAnswer).where(WrongAnswer.user_id == user_id)))
    for wrong in legacy_wrong_answers:
        item = stats.setdefault(wrong.stage_id, TopicStats())
        item.last_wrong_at = _latest(item.last_wrong_at, wrong.created_at)
        if (
            wrong.stage_id not in stages_with_results
            and wrong.stage_id not in stages_with_attempts
        ):
            item.total_attempts += 1
            item.wrong_count += 1
    return stats


# 아직 클리어하지 못한 가장 앞선 스테이지(=현재 진도)를 찾는다. 전부 클리어했으면 마지막 스테이지.
def _get_current_stage_id(db: Session, user_id: int, stages: list[Stage]) -> int:
    cleared_ids = set(
        db.scalars(
            select(Progress.stage_id).where(
                Progress.user_id == user_id,
                Progress.cleared.is_(True),
            )
        )
    )
    for stage in stages:
        if stage.stage_id not in cleared_ids:
            return stage.stage_id
    return stages[-1].stage_id


# 스테이지별 학습 페이지 목록을 미리 조회해 stage_id로 묶어둔다
def _get_learning_by_stage(db: Session, stages: list[Stage]) -> dict[int, list[Learning]]:
    stage_ids = [stage.stage_id for stage in stages]
    if not stage_ids:
        return {}
    pages = list(
        db.scalars(
            select(Learning)
            .where(Learning.stage_id.in_(stage_ids))
            .order_by(Learning.stage_id, Learning.page_order)
        )
    )
    grouped: dict[int, list[Learning]] = {}
    for page in pages:
        grouped.setdefault(page.stage_id, []).append(page)
    return grouped


# 스테이지별 대표 주제 태그(첫 문제의 tag)를 조회
def _get_topics(db: Session, stages: list[Stage]) -> dict[int, str]:
    stage_ids = [stage.stage_id for stage in stages]
    if not stage_ids:
        return {}
    questions = list(db.scalars(select(Question).where(Question.stage_id.in_(stage_ids))))
    topics: dict[int, str] = {}
    for question in questions:
        topics.setdefault(question.stage_id, question.tag)
    return topics


# 사용자의 추천 노출 이력을 스테이지별로 최신순 그룹핑 (재노출/재추천 판단에 사용)
def _get_recent_history(
    db: Session, user_id: int
) -> dict[int, list[RecommendationHistory]]:
    histories = list(
        db.scalars(
            select(RecommendationHistory)
            .where(RecommendationHistory.user_id == user_id)
            .order_by(RecommendationHistory.recommended_at.desc(), RecommendationHistory.recommendation_id.desc())
        )
    )
    grouped: dict[int, list[RecommendationHistory]] = {}
    for history in histories:
        grouped.setdefault(history.stage_id, []).append(history)
    return grouped


# 두 시각 중 더 최근 값을 반환
def _latest(current: datetime | None, candidate: datetime) -> datetime:
    if current is None or _as_utc(candidate) > _as_utc(current):
        return candidate
    return current


# tz 정보가 없는 datetime을 UTC로 간주해 비교 가능하게 정규화
def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
