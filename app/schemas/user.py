"""Pydantic schemas for users and authentication."""
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Literal


class UserSignup(BaseModel):
    """Input for signing up."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=100)

    @field_validator("password")
    @classmethod
    def password_byte_limit(cls, value):
        if len(value.encode("utf8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        return value


class UserLogin(BaseModel):
    """Input for logging in."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Output — safe user info (no password)."""
    id: int
    email: str
    full_name: str
    role: Literal["citizen", "social_worker", "admin"]

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Response after login — JWT token."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse