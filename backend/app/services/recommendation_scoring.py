from dataclasses import dataclass


@dataclass(frozen=True)
class RecommendationWeights:
    # 각 항목의 최대 기여도. 총점은 100점에 가깝게 해석할 수 있지만
    # 최근 추천/완료/연속 노출 패널티 때문에 최종 점수는 0점 아래로 내려가지 않는다.
    wrong_count: float = 30.0
    low_accuracy: float = 25.0
    difficulty: float = 8.0
    progress_proximity: float = 15.0
    recent_wrong: float = 15.0
    unseen_topic: float = 7.0
    recent_recommendation_penalty: float = 12.0
    recent_completion_penalty: float = 18.0
    consecutive_recommendation_penalty: float = 10.0


@dataclass(frozen=True)
class RecommendationSignals:
    wrong_count: int
    total_attempts: int
    accuracy: float | None
    difficulty: int
    progress_distance: int
    days_since_last_wrong: float | None = None
    days_since_last_recommendation: float | None = None
    days_since_completion: float | None = None
    was_last_top_recommendation: bool = False


@dataclass(frozen=True)
class ScoreBreakdown:
    total: float
    wrong_count: float
    low_accuracy: float
    difficulty: float
    progress_proximity: float
    recent_wrong: float
    unseen_topic: float
    recent_recommendation_penalty: float
    recent_completion_penalty: float
    consecutive_recommendation_penalty: float


DEFAULT_WEIGHTS = RecommendationWeights()


def calculate_recommendation_score(
    signals: RecommendationSignals,
    weights: RecommendationWeights = DEFAULT_WEIGHTS,
) -> ScoreBreakdown:
    """추천 신호를 0 이상의 점수로 변환하는 순수 함수."""
    if signals.wrong_count < 0 or signals.total_attempts < 0:
        raise ValueError("Attempt counts cannot be negative")
    if signals.wrong_count > signals.total_attempts:
        raise ValueError("wrong_count cannot exceed total_attempts")
    if signals.accuracy is not None and not 0 <= signals.accuracy <= 100:
        raise ValueError("accuracy must be between 0 and 100")
    if signals.difficulty < 1 or signals.progress_distance < 0:
        raise ValueError("difficulty and progress_distance must be positive")

    # 오답 5회부터는 만점 처리해 오래 사용한 주제가 점수를 무한히 독점하지 않게 한다.
    wrong_component = min(signals.wrong_count / 5, 1.0) * weights.wrong_count
    accuracy_component = (
        ((100 - signals.accuracy) / 100) * weights.low_accuracy
        if signals.accuracy is not None
        else 0.0
    )
    difficulty_component = min(signals.difficulty / 3, 1.0) * weights.difficulty
    # 현재 진도에서 5단계 이상 떨어지면 진도 연관 점수는 0점이다.
    progress_component = max(0.0, 1 - signals.progress_distance / 5) * weights.progress_proximity
    recent_wrong_component = _recency_value(signals.days_since_last_wrong, 30) * weights.recent_wrong
    unseen_component = weights.unseen_topic if signals.total_attempts == 0 else 0.0

    # 최근 노출과 완료는 제외가 아니라 감점이다. 취약도가 충분히 높으면 다시 추천될 수 있다.
    recommend_penalty = (
        _recency_value(signals.days_since_last_recommendation, 7)
        * weights.recent_recommendation_penalty
    )
    completion_penalty = (
        _recency_value(signals.days_since_completion, 14)
        * weights.recent_completion_penalty
    )
    consecutive_penalty = (
        weights.consecutive_recommendation_penalty if signals.was_last_top_recommendation else 0.0
    )

    total = max(
        0.0,
        wrong_component
        + accuracy_component
        + difficulty_component
        + progress_component
        + recent_wrong_component
        + unseen_component
        - recommend_penalty
        - completion_penalty
        - consecutive_penalty,
    )
    return ScoreBreakdown(
        total=round(total, 2),
        wrong_count=round(wrong_component, 2),
        low_accuracy=round(accuracy_component, 2),
        difficulty=round(difficulty_component, 2),
        progress_proximity=round(progress_component, 2),
        recent_wrong=round(recent_wrong_component, 2),
        unseen_topic=round(unseen_component, 2),
        recent_recommendation_penalty=round(recommend_penalty, 2),
        recent_completion_penalty=round(completion_penalty, 2),
        consecutive_recommendation_penalty=round(consecutive_penalty, 2),
    )


# 경과일이 window_days 이내면 1(최근)~0(경과) 사이 값으로, 밖이면 0으로 감쇠
def _recency_value(days: float | None, window_days: int) -> float:
    if days is None:
        return 0.0
    if days < 0:
        raise ValueError("Recency cannot be negative")
    return max(0.0, 1 - days / window_days)
