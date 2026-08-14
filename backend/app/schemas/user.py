from pydantic import BaseModel, Field, field_validator

from app.schemas.common import validate_login_id_format


class UserResponse(BaseModel):
    login_id: str


class UserUpdateRequest(BaseModel):
    login_id: str = Field(min_length=3, max_length=16)

    @field_validator("login_id")
    @classmethod
    def check_login_id_format(cls, value: str) -> str:
        return validate_login_id_format(value)