from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    login_id: str


class UserUpdateRequest(BaseModel):
    login_id: str = Field(min_length=2, max_length=30)