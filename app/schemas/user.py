from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Optional[str] = "admin"


class UserCreate(UserBase):
    password: str
    otp: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    otp: Optional[str] = None


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    otp: str
    newPassword: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AuthStatusResponse(BaseModel):
    message: str
    status: str
    otp_required: bool = False
    demo_otp: Optional[str] = None
