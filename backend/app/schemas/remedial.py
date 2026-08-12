from pydantic import BaseModel, Field, field_validator, model_validator


class GeneratedRemedialQuestion(BaseModel):
    question: str = Field(min_length=5, max_length=500)
    choices: list[str] = Field(min_length=4, max_length=4)
    correct_answer: int = Field(ge=0, le=3)
    explanation: str = Field(min_length=5, max_length=1000)
    topic: str = Field(min_length=1, max_length=100)

    @field_validator("question", "explanation", "topic")
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


class GeminiRemedialQuestionSet(BaseModel):
    questions: list[GeneratedRemedialQuestion] = Field(min_length=2, max_length=2)

    @model_validator(mode="after")
    def require_distinct_questions(self) -> "GeminiRemedialQuestionSet":
        normalized = {
            " ".join(item.question.lower().split()) for item in self.questions
        }
        if len(normalized) != 2:
            raise ValueError("generated questions must be distinct")
        return self


class RemedialQuestionsResponse(BaseModel):
    questions: list[GeneratedRemedialQuestion]
    available: bool
    cached: bool
    message: str | None = None

    @model_validator(mode="after")
    def validate_availability(self) -> "RemedialQuestionsResponse":
        if self.available and len(self.questions) != 2:
            raise ValueError("available responses must contain exactly two questions")
        if not self.available and self.questions:
            raise ValueError("unavailable responses cannot contain questions")
        return self
