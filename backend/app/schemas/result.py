from pydantic import BaseModel, Field, model_validator


class ResultRequest(BaseModel):
    user_id: int
    stage_id: int
    score: int = Field(ge=0)
    correct_count: int | None = Field(default=None, ge=0)
    total_question: int = Field(default=10, gt=0)

    @model_validator(mode="after")
    def validate_counts(self) -> "ResultRequest":
        if self.correct_count is not None and self.correct_count > self.total_question:
            raise ValueError("correct_count cannot exceed total_question")
        return self


class ResultResponse(BaseModel):
    stage_clear: bool
    building_level: int
