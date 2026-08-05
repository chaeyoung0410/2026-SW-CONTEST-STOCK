from datetime import datetime

from pydantic import BaseModel, Field, model_validator


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
    total_attempts: int = Field(ge=0)
    correct_count: int = Field(ge=0)
    wrong_count: int = Field(ge=0)
    difficulty: int = Field(ge=1)
    recently_recommended: bool


class RecommendationFeedbackRequest(BaseModel):
    clicked: bool | None = None
    learning_completed: bool | None = None

    @model_validator(mode="after")
    def require_update(self) -> "RecommendationFeedbackRequest":
        if self.clicked is None and self.learning_completed is None:
            raise ValueError("clicked or learning_completed is required")
        return self


class RecommendationFeedbackResponse(BaseModel):
    recommendation_id: int
    clicked: bool
    clicked_at: datetime | None
    learning_started: bool
    started_at: datetime | None
    learning_completed: bool
    completed_at: datetime | None


class RecommendationInteractionResponse(RecommendationFeedbackResponse):
    interaction: str
    already_applied: bool
