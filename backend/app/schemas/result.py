from pydantic import BaseModel, Field, model_validator


class ResultRequest(BaseModel):
    user_id: int
    stage_id: int
    score: int = Field(ge=0)
    correct_count: int | None = Field(default=None, ge=0)
    total_question: int = Field(default=10, gt=0)
    answer_attempt_ids: list[int] | None = Field(default=None, min_length=1)
    submission_id: str | None = Field(default=None, min_length=8, max_length=64)
    recommendation_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_counts(self) -> "ResultRequest":
        if self.correct_count is not None and self.correct_count > self.total_question:
            raise ValueError("correct_count cannot exceed total_question")
        if self.score % 10 != 0:
            raise ValueError("score must be a multiple of 10")
        if self.score > self.total_question * 10:
            raise ValueError("score cannot exceed total_question * 10")
        if self.correct_count is not None and self.score != self.correct_count * 10:
            raise ValueError("score does not match correct_count")
        if self.answer_attempt_ids is not None and len(set(self.answer_attempt_ids)) != len(
            self.answer_attempt_ids
        ):
            raise ValueError("answer_attempt_ids cannot contain duplicates")
        return self


class ResultResponse(BaseModel):
    stage_clear: bool
    building_level: int
