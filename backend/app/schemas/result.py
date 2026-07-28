from pydantic import BaseModel, Field


class ResultRequest(BaseModel):
    user_id: int
    stage_id: int
    score: int = Field(ge=0)
    correct_count: int | None = Field(default=None, ge=0)
    total_question: int = Field(default=10, gt=0)


class ResultResponse(BaseModel):
    stage_clear: bool
    building_level: int
