import re
from datetime import datetime

from pydantic import BaseModel, field_validator


# ---------- 인증 ----------
class CheckIdResponse(BaseModel):
    available: bool


class SignupRequest(BaseModel):
    user_id: str
    password: str

    @field_validator("password")
    @classmethod
    def password_must_be_6_digits(cls, v: str) -> str:
        if not re.fullmatch(r"\d{6}", v):
            raise ValueError("비밀번호는 숫자 6자리여야 합니다.")
        return v


class SignupResponse(BaseModel):
    user_id: str
    created_at: datetime


class LoginRequest(BaseModel):
    user_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    message: str


# ---------- 게임 화면 ----------
class StageStatus(BaseModel):
    step_number: int
    completed: bool


class GameBoardResponse(BaseModel):
    level: int
    board_position: int
    total_score: int
    stages: list[StageStatus]


# ---------- 학습/문제풀이 ----------
class StageSummaryResponse(BaseModel):
    step_number: int
    learning_content: str
    total_questions: int
    is_completed: bool


class LearningContentResponse(BaseModel):
    step_number: int
    learning_content: str


class QuestionItem(BaseModel):
    question_id: int
    question: str


class QuestionListResponse(BaseModel):
    step_number: int
    questions: list[QuestionItem]


class SubmitAnswerRequest(BaseModel):
    answer: str


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    message: str
    correct_answer: str | None = None


# ---------- 결과 화면 ----------
class StageResultResponse(BaseModel):
    step_number: int
    total_questions: int
    correct_count: int


class StageCompleteResponse(BaseModel):
    step_number: int
    level: int
    leveled_up: bool


# ---------- 마이페이지 ----------
class MyInfoResponse(BaseModel):
    user_id: str
    nickname: str
    level: int
    total_score: int
    joined_at: datetime


class BuildingItem(BaseModel):
    level: int
    unlocked: bool


class MyBuildingsResponse(BaseModel):
    current_level: int
    buildings: list[BuildingItem]


class HistoryItem(BaseModel):
    step_number: int
    correct_count: int
    total_questions: int
    completed_at: datetime


class MyHistoryResponse(BaseModel):
    history: list[HistoryItem]
