from pydantic import BaseModel, Field, field_validator

from app.schemas.common import validate_login_id_format


class LoginRequest(BaseModel):
    login_id: str = Field(max_length=30)
    password: str


class LoginResponse(BaseModel):
    success: bool
    user_id: int
    access_token: str
    token_type: str = "bearer"


class SignUpRequest(BaseModel):
    login_id: str = Field(min_length=3, max_length=16, examples=["user01"])
    password: str = Field(min_length=4, max_length=100, examples=["1234"])

    @field_validator("login_id")
    @classmethod
    def check_login_id_format(cls, value: str) -> str:
        return validate_login_id_format(value)


class SignUpResponse(BaseModel):
    success: bool


class AuthStatusResponse(BaseModel):
    logged_in: bool
