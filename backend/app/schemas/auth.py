from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    login_id: str = Field(max_length=30)
    password: str


class LoginResponse(BaseModel):
    success: bool
    user_id: int
    access_token: str
    token_type: str = "bearer"


class SignUpRequest(BaseModel):
    login_id: str = Field(min_length=2, max_length=30, examples=["user01"])
    password: str = Field(min_length=4, max_length=100, examples=["1234"])


class SignUpResponse(BaseModel):
    success: bool


class AuthStatusResponse(BaseModel):
    logged_in: bool
