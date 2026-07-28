"""
DB 테이블 정의

users              : 회원 (아이디 + 6자리 비밀번호)
game_progress      : 유저별 게임 진행상태 (레벨, 보드 위치, 점수)
stages             : 단계(1~15)별 학습내용
questions          : 단계에 속한 문제들 (한 단계에 여러 개 가능)
question_attempts  : 유저가 어떤 문제를 맞았는지/틀렸는지 기록 (유저+문제 조합당 1행, 재제출 시 덮어씀)
stage_completions  : 유저가 어떤 단계를 완료했는지 + 그때의 맞춘 개수/전체 개수
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    nickname = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    progress = relationship("GameProgress", back_populates="user", uselist=False)


class GameProgress(Base):
    __tablename__ = "game_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    level = Column(Integer, default=1)
    board_position = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="progress")


class Stage(Base):
    __tablename__ = "stages"

    step_number = Column(Integer, primary_key=True)  # 1~15
    learning_content = Column(Text, nullable=False)

    questions = relationship("Question", back_populates="stage")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    step_number = Column(Integer, ForeignKey("stages.step_number"), nullable=False)
    question_text = Column(Text, nullable=False)
    answer = Column(String(255), nullable=False)

    stage = relationship("Stage", back_populates="questions")


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_user_question"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    is_correct = Column(Boolean, default=False)
    answered_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StageCompletion(Base):
    __tablename__ = "stage_completions"
    __table_args__ = (UniqueConstraint("user_id", "step_number", name="uq_user_stage"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    step_number = Column(Integer, ForeignKey("stages.step_number"), nullable=False)
    correct_count = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    completed_at = Column(DateTime, default=datetime.utcnow)
