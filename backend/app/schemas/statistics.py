from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class StageStatistics(BaseModel):
    stage_id: int
    title: str
    topic: str
    total_attempts: int = Field(ge=0)
    correct_count: int = Field(ge=0)
    wrong_count: int = Field(ge=0)
    accuracy: float | None = Field(default=None, ge=0, le=100)
    cumulative_score: int = Field(ge=0)
    latest_score: int | None = Field(default=None, ge=0)
    score_change: int | None = None


class TopicStatistics(BaseModel):
    stage_id: int
    topic: str
    accuracy: float | None = Field(default=None, ge=0, le=100)
    wrong_count: int = Field(ge=0)
    accuracy_change: float | None = None


class RecommendationEffect(BaseModel):
    recommendation_id: int
    stage_id: int
    topic: str
    status: Literal["measured", "pending", "insufficient_baseline"]
    completed_at: datetime
    baseline_accuracy: float | None = None
    post_accuracy: float | None = None
    accuracy_change: float | None = None
    baseline_score: int | None = None
    post_score: int | None = None
    score_change: int | None = None
    baseline_wrong_count: int | None = Field(default=None, ge=0)
    post_wrong_count: int | None = Field(default=None, ge=0)
    wrong_count_change: int | None = None
    retested_after_recommendation: bool


class RecommendationEffectiveness(BaseModel):
    completed_content_count: int = Field(ge=0)
    evaluated_count: int = Field(ge=0)
    pending_count: int = Field(ge=0)
    average_accuracy_change: float | None = None
    improved_recommendation_rate: float | None = None
    effects: list[RecommendationEffect]


class RecommendationInteractionStatistics(BaseModel):
    recommended_count: int = Field(ge=0)
    clicked_count: int = Field(ge=0)
    started_count: int = Field(ge=0)
    completed_count: int = Field(ge=0)


class UserStatisticsResponse(BaseModel):
    total_attempts: int = Field(ge=0)
    correct_count: int = Field(ge=0)
    wrong_count: int = Field(ge=0)
    overall_accuracy: float | None = Field(default=None, ge=0, le=100)
    recent_accuracy: float | None = Field(default=None, ge=0, le=100)
    cumulative_score: int = Field(ge=0)
    recent_score_change: int | None = None
    stages: list[StageStatistics]
    weakest_topic: TopicStatistics | None
    most_improved_topic: TopicStatistics | None
    recommendations: RecommendationInteractionStatistics
    recommendation_effectiveness: RecommendationEffectiveness
