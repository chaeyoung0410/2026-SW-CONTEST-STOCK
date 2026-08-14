from datetime import datetime

from pydantic import BaseModel, Field


class LearningPageResponse(BaseModel):
    learning_id: int
    title: str
    content: str
    image: str | None
    page_order: int


class LearningResponse(BaseModel):
    stage_id: int
    title: str
    content: str
    pages: list[LearningPageResponse]


class RecommendationResponse(LearningResponse):
    recommendation_id: int
    content_id: int
    priority: int = Field(ge=1)
    recommendation_score: float = Field(ge=0)
    recommendation_reason: str
    weak_topic: str
    current_accuracy: float | None = Field(default=None, ge=0, le=100)
    wrong_rate: float = Field(ge=0, le=100)
    total_attempts: int = Field(ge=0)
    correct_count: int = Field(ge=0)
    wrong_count: int = Field(ge=0)
    difficulty: int = Field(ge=1)
    recently_recommended: bool


class RecommendationInteractionState(BaseModel):
    recommendation_id: int
    clicked: bool
    clicked_at: datetime | None
    learning_started: bool
    started_at: datetime | None
    learning_completed: bool
    completed_at: datetime | None


class RecommendationInteractionResponse(RecommendationInteractionState):
    interaction: str
    already_applied: bool
