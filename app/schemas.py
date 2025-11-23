# app/schemas.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from pydantic.v1 import validator


# User Schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    is_active: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Suggestion Schemas
class SuggestionBase(BaseModel):
    title: str
    text: str


class SuggestionCreate(SuggestionBase):
    pass


class Suggestion(SuggestionBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Response schemas
class SuggestionResponse(Suggestion):
    user_email: str  # Анонимно - только email, не весь user


class SuggestionUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    status: Optional[str] = None  # Только для модераторов

    @validator("status")
    def validate_status(cls, v):
        if v and v not in ["pending", "approved", "rejected"]:
            raise ValueError("Status must be pending, approved or rejected")
        return v


# 🆕 Схема для изменения статуса
class StatusUpdate(BaseModel):
    status: str

    @validator("status")
    def validate_status(cls, v):
        if v not in ["pending", "approved", "rejected"]:
            raise ValueError("Status must be pending, approved or rejected")
        return v
