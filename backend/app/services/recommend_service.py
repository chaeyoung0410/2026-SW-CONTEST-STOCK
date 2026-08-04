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
from app.services.recommendation_scoring import RecommendationSignals, calculate_recommendation_score

DEFAULT_RECOMMENDATION_LIMIT = 4
RECENT_RECOMMENDATION_DAYS = 7


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
    """취약도 점수를 계산하고 추천 노출 이력까지 원자적으로 저장한다."""
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
    history_by_stage, last_top_stage_id = _get_recent_history(db, user_id)
    latest_result_by_stage = _get_latest_results_by_stage(db, user_id)
    is_default_recommendation = not any(
        item.total_attempts > 0 for item in stats.values()
    )

    ranked: list[dict] = []
    for stage in candidates:
        stage_stats = stats.get(stage.stage_id, TopicStats())
        histories = history_by_stage.get(stage.stage_id, [])
        last_recommendation = histories[0] if histories else None
        last_completion = next((item for item in histories if item.learning_completed), None)
        days_since_wrong = _days_since(now, stage_stats.last_wrong_at)
        days_since_recommendation = _days_since(
            now, last_recommendation.recommended_at if last_recommendation else None
        )
        days_since_completion = _days_since(
            now, last_completion.completed_at if last_completion else None
        )

        breakdown = calculate_recommendation_score(
            RecommendationSignals(
                wrong_count=stage_stats.wrong_count,
                total_attempts=stage_stats.total_attempts,
                accuracy=stage_stats.accuracy,
                difficulty=stage.difficulty,
                progress_distance=abs(current_stage_id - stage.stage_id),
                days_since_last_wrong=days_since_wrong,
                days_since_last_recommendation=days_since_recommendation,
                days_since_completion=days_since_completion,
                was_last_top_recommendation=stage.stage_id == last_top_stage_id,
            )
        )
        pages = learning_by_stage.get(stage.stage_id, [])
        topic = topics.get(stage.stage_id, stage.title)
        reason = _build_reason(stage_stats, topic, days_since_wrong, last_completion is not None)
        ranked.append(
            {
                "stage": stage,
                "pages": pages,
                "topic": topic,
                "stats": stage_stats,
                "score": breakdown.total,
                "reason": reason,
                "recently_recommended": (
                    days_since_recommendation is not None
                    and days_since_recommendation <= RECENT_RECOMMENDATION_DAYS
                ),
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["stage"].stage_id))
    # A penalty alone cannot guarantee rotation when one topic is much weaker.
    # Keep the previous top eligible, but place one alternative ahead whenever
    # at least two accessible candidates exist.
    if (
        len(ranked) > 1
        and last_top_stage_id is not None
        and ranked[0]["stage"].stage_id == last_top_stage_id
    ):
        previous_top = ranked.pop(0)
        previous_top["score"] = round(max(0.0, ranked[0]["score"] - 0.01), 2)
        ranked.insert(1, previous_top)
    selected = ranked[:limit]

    try:
        response: list[dict] = []
        for priority, item in enumerate(selected, start=1):
            stage = item["stage"]
            pages = item["pages"]
            stage_stats = item["stats"]
            learning_id = pages[0].learning_id if pages else None
            baseline_result = latest_result_by_stage.get(stage.stage_id)
            baseline_total = baseline_result.total_question if baseline_result else 0
            baseline_correct = (
                min(max(baseline_result.correct_count, 0), baseline_total)
                if baseline_result and baseline_total > 0
                else 0
            )
            baseline_accuracy = (
                round((baseline_correct / baseline_total) * 100, 2)
                if baseline_total > 0
                else None
            )
            history = RecommendationHistory(
                user_id=user_id,
                stage_id=stage.stage_id,
                learning_id=learning_id,
                priority=priority,
                recommendation_score=item["score"],
                reason=item["reason"],
                recommended_at=now,
                baseline_accuracy=baseline_accuracy,
                baseline_score=(baseline_result.score if baseline_result else None),
                baseline_wrong_count=(
                    baseline_total - baseline_correct
                    if baseline_total > 0
                    else None
                ),
                is_default_recommendation=is_default_recommendation,
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


def update_recommendation_feedback(
    db: Session,
    user_id: int,
    recommendation_id: int,
    clicked: bool | None,
    learning_completed: bool | None,
    now: datetime | None = None,
) -> RecommendationHistory:
    history = _get_owned_recommendation(db, user_id, recommendation_id)
    updated_at = _as_utc(now or datetime.now(timezone.utc))

    if clicked is not None and not (history.learning_completed and not clicked):
        history.clicked = clicked
        history.clicked_at = updated_at if clicked else None
    if learning_completed:
        if not history.learning_completed:
            history.learning_completed = True
            history.completed_at = updated_at
        if not history.learning_started:
            history.learning_started = True
            history.started_at = updated_at
        if not history.clicked:
            history.clicked = True
            history.clicked_at = updated_at

    try:
        db.commit()
        db.refresh(history)
        return history
    except Exception:
        db.rollback()
        raise


def record_recommendation_interaction(
    db: Session,
    user_id: int,
    recommendation_id: int,
    interaction: str,
    now: datetime | None = None,
) -> RecommendationInteractionResult:
    if interaction not in {"click", "start", "complete"}:
        raise ValueError("Unsupported recommendation interaction")
    history = _get_owned_recommendation(db, user_id, recommendation_id)
    updated_at = _as_utc(now or datetime.now(timezone.utc))
    already_applied = {
        "click": history.clicked,
        "start": history.learning_started,
        "complete": history.learning_completed,
    }[interaction]

    if not already_applied:
        if not history.clicked:
            history.clicked = True
            history.clicked_at = updated_at
        if interaction in {"start", "complete"} and not history.learning_started:
            history.learning_started = True
            history.started_at = updated_at
        if interaction == "complete" and not history.learning_completed:
            history.learning_completed = True
            history.completed_at = updated_at

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


def _get_latest_results_by_stage(db: Session, user_id: int) -> dict[int, Result]:
    rows = list(
        db.scalars(
            select(Result)
            .where(Result.user_id == user_id)
            .order_by(Result.created_at.desc(), Result.result_id.desc())
        )
    )
    latest: dict[int, Result] = {}
    for result in rows:
        latest.setdefault(result.stage_id, result)
    return latest


def _get_topics(db: Session, stages: list[Stage]) -> dict[int, str]:
    stage_ids = [stage.stage_id for stage in stages]
    if not stage_ids:
        return {}
    questions = list(db.scalars(select(Question).where(Question.stage_id.in_(stage_ids))))
    topics: dict[int, str] = {}
    for question in questions:
        topics.setdefault(question.stage_id, question.tag)
    return topics


def _get_recent_history(
    db: Session, user_id: int
) -> tuple[dict[int, list[RecommendationHistory]], int | None]:
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
    last_top = next((item.stage_id for item in histories if item.priority == 1), None)
    return grouped, last_top


def _build_reason(
    stats: TopicStats,
    topic: str,
    days_since_wrong: float | None,
    was_completed: bool,
) -> str:
    if stats.total_attempts == 0:
        return f"아직 풀이 기록이 없어 현재 진도에 맞는 {topic} 입문 학습을 추천합니다."
    if stats.wrong_count and days_since_wrong is not None and days_since_wrong <= 7:
        return f"최근 {topic} 문제에서 {stats.wrong_count}회 오답이 발생해 복습이 필요합니다."
    if stats.accuracy is not None and stats.accuracy < 60:
        return f"현재 {topic} 정답률이 {stats.accuracy:.0f}%로 낮아 우선 학습을 추천합니다."
    if stats.wrong_count:
        suffix = " 최근 학습을 완료했지만 취약도가 남아 다시 추천합니다." if was_completed else ""
        return f"{topic} 문제에서 누적 {stats.wrong_count}회 오답이 확인되었습니다.{suffix}".strip()
    return f"현재 학습 진도와 가까운 {topic} 개념을 다음 학습으로 추천합니다."


def _days_since(now: datetime, value: datetime | None) -> float | None:
    if value is None:
        return None
    seconds = (now - _as_utc(value)).total_seconds()
    return max(0.0, seconds / 86400)


def _latest(current: datetime | None, candidate: datetime) -> datetime:
    if current is None or _as_utc(candidate) > _as_utc(current):
        return candidate
    return current


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
