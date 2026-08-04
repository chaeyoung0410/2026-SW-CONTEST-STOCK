from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.recommendation_history import RecommendationHistory
from app.models.result import Result
from app.models.stage import Stage
from app.models.user import User

RECENT_STATISTICS_DAYS = 30
REPEAT_RECOMMENDATION_DAYS = 7


@dataclass(frozen=True)
class RecommendationQualityMetrics:
    recommendation_count: int
    click_rate: float | None
    completion_rate: float | None
    retest_rate: float | None
    post_recommendation_improvement_rate: float | None
    top_recommendation_selection_rate: float | None
    repeat_recommendation_rate: float | None
    default_recommendation_completion_rate: float | None


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _accuracy(result: Result | None) -> float | None:
    if result is None or result.total_question <= 0:
        return None
    return round((result.correct_count / result.total_question) * 100, 2)


def _wrong_count(result: Result | None) -> int | None:
    if result is None:
        return None
    return max(0, result.total_question - result.correct_count)


def _topic_by_stage(db: Session) -> dict[int, str]:
    topics: dict[int, str] = {}
    for question in db.scalars(select(Question).order_by(Question.question_id)):
        topics.setdefault(question.stage_id, question.tag)
    return topics


def _result_before(
    results: list[Result], stage_id: int, before: datetime
) -> Result | None:
    candidates = [
        result
        for result in results
        if result.stage_id == stage_id and _as_utc(result.created_at) < before
    ]
    return candidates[-1] if candidates else None


def _post_result(
    history: RecommendationHistory,
    results: list[Result],
    results_by_id: dict[int, Result],
) -> Result | None:
    if history.completion_result_id is not None:
        return results_by_id.get(history.completion_result_id)
    if history.completed_at is None:
        return None
    completed_at = _as_utc(history.completed_at)
    return next(
        (
            result
            for result in results
            if result.stage_id == history.stage_id
            and _as_utc(result.created_at) >= completed_at
        ),
        None,
    )


def _build_recommendation_effects(
    histories: list[RecommendationHistory],
    results: list[Result],
    topics: dict[int, str],
) -> list[dict]:
    results_by_id = {result.result_id: result for result in results}
    effects: list[dict] = []
    for history in histories:
        if not history.learning_completed or history.completed_at is None:
            continue
        post_result = _post_result(history, results, results_by_id)
        baseline_accuracy = history.baseline_accuracy
        baseline_score = history.baseline_score
        baseline_wrong_count = history.baseline_wrong_count
        if baseline_accuracy is None and baseline_score is None:
            baseline_result = _result_before(
                results, history.stage_id, _as_utc(history.recommended_at)
            )
            baseline_accuracy = _accuracy(baseline_result)
            baseline_score = baseline_result.score if baseline_result else None
            baseline_wrong_count = _wrong_count(baseline_result)

        post_accuracy = _accuracy(post_result)
        post_score = post_result.score if post_result else None
        post_wrong_count = _wrong_count(post_result)
        if post_result is None:
            effect_status = "pending"
        elif baseline_accuracy is None:
            effect_status = "insufficient_baseline"
        else:
            effect_status = "measured"

        effects.append(
            {
                "recommendation_id": history.recommendation_id,
                "stage_id": history.stage_id,
                "topic": topics.get(history.stage_id, history.stage.title),
                "status": effect_status,
                "completed_at": history.completed_at,
                "baseline_accuracy": baseline_accuracy,
                "post_accuracy": post_accuracy,
                "accuracy_change": (
                    round(post_accuracy - baseline_accuracy, 2)
                    if post_accuracy is not None and baseline_accuracy is not None
                    else None
                ),
                "baseline_score": baseline_score,
                "post_score": post_score,
                "score_change": (
                    post_score - baseline_score
                    if post_score is not None and baseline_score is not None
                    else None
                ),
                "baseline_wrong_count": baseline_wrong_count,
                "post_wrong_count": post_wrong_count,
                "wrong_count_change": (
                    post_wrong_count - baseline_wrong_count
                    if post_wrong_count is not None
                    and baseline_wrong_count is not None
                    else None
                ),
                "retested_after_recommendation": post_result is not None,
            }
        )
    return effects


def get_user_statistics(
    db: Session,
    user_id: int,
    *,
    now: datetime | None = None,
) -> dict:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    evaluated_at = _as_utc(now or datetime.now(timezone.utc))
    results = list(
        db.scalars(
            select(Result)
            .where(Result.user_id == user_id)
            .order_by(Result.created_at, Result.result_id)
        )
    )
    stages = {stage.stage_id: stage for stage in db.scalars(select(Stage))}
    topics = _topic_by_stage(db)

    total_attempts = sum(result.total_question for result in results)
    correct_count = sum(result.correct_count for result in results)
    wrong_count = max(0, total_attempts - correct_count)
    overall_accuracy = (
        round((correct_count / total_attempts) * 100, 2)
        if total_attempts
        else None
    )
    recent_cutoff = evaluated_at - timedelta(days=RECENT_STATISTICS_DAYS)
    recent_results = [
        result for result in results if _as_utc(result.created_at) >= recent_cutoff
    ]
    recent_total = sum(result.total_question for result in recent_results)
    recent_correct = sum(result.correct_count for result in recent_results)
    recent_accuracy = (
        round((recent_correct / recent_total) * 100, 2)
        if recent_total
        else None
    )

    grouped: dict[int, list[Result]] = {}
    for result in results:
        grouped.setdefault(result.stage_id, []).append(result)
    stage_statistics: list[dict] = []
    topic_summaries: list[dict] = []
    improvement_summaries: list[dict] = []
    for stage_id, stage_results in grouped.items():
        stage = stages.get(stage_id)
        if stage is None:
            continue
        stage_total = sum(result.total_question for result in stage_results)
        stage_correct = sum(result.correct_count for result in stage_results)
        stage_wrong = max(0, stage_total - stage_correct)
        stage_accuracy = (
            round((stage_correct / stage_total) * 100, 2) if stage_total else None
        )
        score_change = (
            stage_results[-1].score - stage_results[-2].score
            if len(stage_results) >= 2
            else None
        )
        topic = topics.get(stage_id, stage.title)
        stage_statistics.append(
            {
                "stage_id": stage_id,
                "title": stage.title,
                "topic": topic,
                "total_attempts": stage_total,
                "correct_count": stage_correct,
                "wrong_count": stage_wrong,
                "accuracy": stage_accuracy,
                "cumulative_score": sum(result.score for result in stage_results),
                "latest_score": stage_results[-1].score,
                "score_change": score_change,
            }
        )
        topic_summaries.append(
            {
                "stage_id": stage_id,
                "topic": topic,
                "accuracy": stage_accuracy,
                "wrong_count": stage_wrong,
                "accuracy_change": None,
            }
        )
        if len(stage_results) >= 2:
            first_accuracy = _accuracy(stage_results[0])
            latest_accuracy = _accuracy(stage_results[-1])
            if first_accuracy is not None and latest_accuracy is not None:
                improvement_summaries.append(
                    {
                        "stage_id": stage_id,
                        "topic": topic,
                        "accuracy": latest_accuracy,
                        "wrong_count": _wrong_count(stage_results[-1]) or 0,
                        "accuracy_change": round(latest_accuracy - first_accuracy, 2),
                    }
                )

    stage_statistics.sort(key=lambda item: item["stage_id"])
    weakest_topic = (
        min(
            topic_summaries,
            key=lambda item: (
                item["accuracy"] if item["accuracy"] is not None else 101,
                -item["wrong_count"],
            ),
        )
        if topic_summaries
        else None
    )
    most_improved_topic = (
        max(improvement_summaries, key=lambda item: item["accuracy_change"])
        if improvement_summaries
        else None
    )

    histories = list(
        db.scalars(
            select(RecommendationHistory)
            .where(RecommendationHistory.user_id == user_id)
            .order_by(RecommendationHistory.recommended_at)
        )
    )
    effects = _build_recommendation_effects(histories, results, topics)
    measured = [item for item in effects if item["status"] == "measured"]
    accuracy_changes = [item["accuracy_change"] for item in measured]
    improved_count = sum(1 for value in accuracy_changes if value is not None and value > 0)

    return {
        "total_attempts": total_attempts,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "overall_accuracy": overall_accuracy,
        "recent_accuracy": recent_accuracy,
        "cumulative_score": sum(result.score for result in results),
        "recent_score_change": (
            results[-1].score - results[-2].score if len(results) >= 2 else None
        ),
        "stages": stage_statistics,
        "weakest_topic": weakest_topic,
        "most_improved_topic": most_improved_topic,
        "recommendations": {
            "recommended_count": len(histories),
            "clicked_count": sum(1 for item in histories if item.clicked),
            "started_count": sum(1 for item in histories if item.learning_started),
            "completed_count": sum(1 for item in histories if item.learning_completed),
        },
        "recommendation_effectiveness": {
            "completed_content_count": len(effects),
            "evaluated_count": len(measured),
            "pending_count": sum(1 for item in effects if item["status"] == "pending"),
            "average_accuracy_change": (
                round(sum(accuracy_changes) / len(accuracy_changes), 2)
                if accuracy_changes
                else None
            ),
            "improved_recommendation_rate": (
                round((improved_count / len(measured)) * 100, 2)
                if measured
                else None
            ),
            "effects": effects,
        },
    }


def calculate_recommendation_quality_metrics(db: Session) -> dict:
    """Calculate admin-facing quality metrics without exposing a public API.

    TODO: expose this through an admin-only route after an administrator role
    and authorization policy are implemented.
    """

    histories = list(
        db.scalars(
            select(RecommendationHistory).order_by(
                RecommendationHistory.user_id,
                RecommendationHistory.recommended_at,
                RecommendationHistory.recommendation_id,
            )
        )
    )
    results = list(db.scalars(select(Result).order_by(Result.created_at)))
    results_by_user: dict[int, list[Result]] = {}
    for result in results:
        results_by_user.setdefault(result.user_id, []).append(result)

    effects: list[dict] = []
    for user_id, user_histories in _group_histories_by_user(histories).items():
        effects.extend(
            _build_recommendation_effects(
                user_histories,
                results_by_user.get(user_id, []),
                {},
            )
        )
    measured = [item for item in effects if item["status"] == "measured"]
    completed = [item for item in histories if item.learning_completed]
    clicked = [item for item in histories if item.clicked]
    top_clicked = [item for item in clicked if item.priority == 1]
    default_items = [item for item in histories if item.is_default_recommendation]

    repeated_count = 0
    latest_by_user_stage: dict[tuple[int, int], datetime] = {}
    for history in histories:
        key = (history.user_id, history.stage_id)
        previous = latest_by_user_stage.get(key)
        if previous is not None:
            elapsed = (_as_utc(history.recommended_at) - previous).total_seconds()
            if 0 <= elapsed <= REPEAT_RECOMMENDATION_DAYS * 86400:
                repeated_count += 1
        latest_by_user_stage[key] = _as_utc(history.recommended_at)

    metrics = RecommendationQualityMetrics(
        recommendation_count=len(histories),
        click_rate=_rate(len(clicked), len(histories)),
        completion_rate=_rate(len(completed), len(histories)),
        retest_rate=_rate(
            sum(1 for item in effects if item["retested_after_recommendation"]),
            len(effects),
        ),
        post_recommendation_improvement_rate=_rate(
            sum(1 for item in measured if (item["accuracy_change"] or 0) > 0),
            len(measured),
        ),
        top_recommendation_selection_rate=_rate(len(top_clicked), len(clicked)),
        repeat_recommendation_rate=_rate(repeated_count, len(histories)),
        default_recommendation_completion_rate=_rate(
            sum(1 for item in default_items if item.learning_completed),
            len(default_items),
        ),
    )
    return asdict(metrics)


def _group_histories_by_user(
    histories: list[RecommendationHistory],
) -> dict[int, list[RecommendationHistory]]:
    grouped: dict[int, list[RecommendationHistory]] = {}
    for history in histories:
        grouped.setdefault(history.user_id, []).append(history)
    return grouped


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round((numerator / denominator) * 100, 2)
