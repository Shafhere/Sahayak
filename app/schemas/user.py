"""Pydantic schemas for users and authentication."""
from pydantic import BaseModel, EmailStr
from typing import Literal


class UserSignup(BaseModel):
    """Input for signing up."""
    email: EmailStr
    password: str
    full_name: str


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

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response after login — JWT token."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse