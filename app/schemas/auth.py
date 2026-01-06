"""
Pydantic schemas for authentication
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, field_validator


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: constr(min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: constr(min_length=6, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for user profile update"""
    username: Optional[constr(min_length=3, max_length=50)] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_admin: bool
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


class TokenData(BaseModel):
    """Schema for token payload"""
    user_id: Optional[int] = None
