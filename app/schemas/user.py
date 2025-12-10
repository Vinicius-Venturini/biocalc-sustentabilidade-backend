from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional


# User schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    company_name: Optional[str] = None
    cnpj: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets requirements"""
        if len(v) < 8:
            raise ValueError('A senha deve ter pelo menos 8 caracteres')
        if len(v) > 72:
            raise ValueError('A senha não pode ter mais de 72 caracteres')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    company_name: Optional[str] = Field(None, max_length=200)
    cnpj: Optional[str] = Field(None, max_length=18)
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password meets requirements if provided"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('A senha deve ter pelo menos 8 caracteres')
        if len(v) > 72:
            raise ValueError('A senha não pode ter mais de 72 caracteres')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    company_name: Optional[str] = None
    cnpj: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=72)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('')
        if len(v) > 72:
            raise ValueError('A senha não pode ter mais de 72 caracteres')
        return v
