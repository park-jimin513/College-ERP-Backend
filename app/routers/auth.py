from datetime import datetime, timedelta
import random
import smtplib
from email.message import EmailMessage
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.mongo import sync_to_mongodb
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    OTPRequest,
    OTPVerify,
    PasswordResetRequest,
    PasswordResetConfirm,
    AuthStatusResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

LOCKOUT_ATTEMPTS = 10
LOCKOUT_DURATION_HOURS = 24


def _send_otp_email(recipient: str, otp: str) -> None:
    if not settings.EMAIL_USER or not settings.EMAIL_PASS:
        print(f"[DEMO OTP] {recipient}: {otp}")
        return

    message = EmailMessage()
    message["Subject"] = "College ERP OTP Verification"
    message["From"] = settings.EMAIL_USER
    message["To"] = recipient
    message.set_content(
        f"Your College ERP verification code is {otp}. It expires in 15 minutes."
    )

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
        smtp.starttls()
        smtp.login(settings.EMAIL_USER, settings.EMAIL_PASS)
        smtp.send_message(message)


@router.post("/send-otp", response_model=AuthStatusResponse)
def send_otp(payload: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email.ilike(payload.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found.")

    otp = f"{random.randint(100000, 999999)}"
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    user.otp_code = otp
    user.otp_expires_at = expires_at
    db.commit()

    demo_otp = None
    if not settings.EMAIL_USER or not settings.EMAIL_PASS:
        demo_otp = otp

    try:
        _send_otp_email(user.email, otp)
    except (OSError, smtplib.SMTPException, RuntimeError) as exc:
        demo_otp = otp
        print(f"[OTP SMTP fallback] {payload.email}: {exc}")

    message = f"OTP sent to {payload.email} (valid for 15 minutes)."
    if demo_otp:
        message = (
            f"Demo OTP generated for {payload.email}. Use this verification code: {demo_otp}. "
            "It is valid for 15 minutes."
        )

    return AuthStatusResponse(
        message=message,
        status="success",
        otp_required=True,
        demo_otp=demo_otp,
    )


@router.post("/verify-otp", response_model=AuthStatusResponse)
def verify_otp(payload: OTPVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email.ilike(payload.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found.")

    if not user.otp_code or not user.otp_expires_at:
        raise HTTPException(status_code=400, detail="No OTP has been requested for this account.")

    if user.otp_expires_at < datetime.utcnow():
        user.otp_code = None
        user.otp_expires_at = None
        db.commit()
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

    if user.otp_code.strip() != payload.otp.strip():
        raise HTTPException(status_code=400, detail="Invalid OTP code.")

    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    return AuthStatusResponse(message="OTP verified successfully.", status="success")


@router.post("/signup", response_model=Token)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email.ilike(payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered.")

    new_user = User(
        name=payload.name,
        email=payload.email.lower(),
        hashed_password=get_password_hash(payload.password),
        role=payload.role or "admin",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    sync_to_mongodb('users', {
        'id': new_user.id,
        'name': new_user.name,
        'email': new_user.email,
        'role': new_user.role,
        'is_active': new_user.is_active,
        'created_at': new_user.created_at.isoformat() if new_user.created_at else None,
        'hashed_password': new_user.hashed_password,
    })

    token = create_access_token(subject=new_user.email)
    return Token(access_token=token, user=UserResponse.model_validate(new_user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Check lockout
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to too many failed attempts. Try again later."
        )

    # Verify password
    if not verify_password(payload.password, user.hashed_password):
        user.failed_attempts = (user.failed_attempts or 0) + 1
        if user.failed_attempts >= LOCKOUT_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(hours=LOCKOUT_DURATION_HOURS)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Reset failed attempts on success
    user.failed_attempts = 0
    user.locked_until = None
    db.commit()

    token = create_access_token(subject=user.email)
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.post("/reset-password", response_model=AuthStatusResponse)
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email.ilike(payload.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found.")

    if not user.otp_code or not user.otp_expires_at:
        raise HTTPException(status_code=400, detail="No OTP has been requested for this account.")

    if user.otp_expires_at < datetime.utcnow():
        user.otp_code = None
        user.otp_expires_at = None
        db.commit()
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

    if user.otp_code.strip() != payload.otp.strip():
        raise HTTPException(status_code=400, detail="Invalid OTP code.")

    if len(payload.newPassword) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    user.hashed_password = get_password_hash(payload.newPassword)
    user.failed_attempts = 0
    user.locked_until = None
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()

    return AuthStatusResponse(message="Password reset successfully. Please log in with your new password.", status="success")
