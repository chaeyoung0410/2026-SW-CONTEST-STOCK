from pydantic import BaseModel, Field


class QuestionResponse(BaseModel):
    question_id: int
    question: str
    choices: list[str]
    tag: str


class AnswerRequest(BaseModel):
    user_id: int
    question_id: int
    answer: int = Field(ge=1, le=4)
    submission_id: str | None = Field(default=None, min_length=8, max_length=64)


class AnswerResponse(BaseModel):
    correct: bool
    score: int
    explanation: str
    correct_answer: str
    attempt_id: int | None = None
