from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    nickname: str


class UserUpdateRequest(BaseModel):
    nickname: str = Field(min_length=2, max_length=30)
