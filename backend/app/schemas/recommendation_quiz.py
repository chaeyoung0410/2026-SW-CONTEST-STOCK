from pydantic import BaseModel, Field, field_validator, model_validator


class GeneratedRecommendationQuestion(BaseModel):
    question: str = Field(min_length=5, max_length=500)
    choices: list[str] = Field(min_length=4, max_length=4)
    correct_answer: int = Field(ge=0, le=3)
    explanation: str = Field(min_length=5, max_length=1000)

    @field_validator("question", "explanation")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("choices")
    @classmethod
    def validate_choices(cls, choices: list[str]) -> list[str]:
        normalized = [choice.strip() for choice in choices]
        if any(not choice for choice in normalized):
            raise ValueError("choices cannot be blank")
        if len(set(normalized)) != 4:
            raise ValueError("choices must be unique")
        return normalized


class GeminiRecommendationQuestionSet(BaseModel):
    questions: list[GeneratedRecommendationQuestion] = Field(min_length=3, max_length=3)

    @model_validator(mode="after")
    def require_distinct_questions(self) -> "GeminiRecommendationQuestionSet":
        normalized = {" ".join(item.question.lower().split()) for item in self.questions}
        if len(normalized) != 3:
            raise ValueError("generated questions must be distinct")
        return self


class RecommendationQuizResponse(BaseModel):
    recommendation_id: int
    stage_id: int
    topic: str
    questions: list[GeneratedRecommendationQuestion]


class RecommendationQuizCompletionRequest(BaseModel):
    correct_count: int = Field(ge=0, le=3)
    total_questions: int = Field(default=3)

    @model_validator(mode="after")
    def require_three_questions(self) -> "RecommendationQuizCompletionRequest":
        if self.total_questions != 3:
            raise ValueError("total_questions must be 3")
        if self.correct_count > self.total_questions:
            raise ValueError("correct_count cannot exceed total_questions")
        return self


class RecommendationQuizCompletionResponse(BaseModel):
    recommendation_id: int
    correct_count: int
    total_questions: int
    passed: bool
    learning_completed: bool
