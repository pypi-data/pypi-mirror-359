"""User model definitions."""

from typing import Optional

from pydantic import EmailStr, Field

from .base import BaseModel


class UserBase(BaseModel):
    """Base user model."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    is_active: bool = Field(True, description="Is user active")
    is_admin: bool = Field(False, description="Is user admin")


class UserCreate(UserBase):
    """Model for creating a user."""
    
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """Model for updating a user."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class User(UserBase):
    """User model for database storage."""
    
    hashed_password: str = Field(..., description="Hashed password")