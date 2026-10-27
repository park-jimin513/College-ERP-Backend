<<<<<<< HEAD
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
=======
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import logging
import os
import secrets
import smtplib
import ssl
from collections.abc import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from email.message import EmailMessage

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pymongo.collation import Collation
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.core.database import get_db
from app.core.mongo import mongo_collection, next_sequence
from app.core.security import create_access_token, get_password_hash, verify_password
from app.schemas.user import (
    AuthStatusResponse,
    OTPRequest,
    OTPVerify,
    PasswordResetConfirm,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)

LOCKOUT_ATTEMPTS = 10
LOCKOUT_DURATION_HOURS = 24
EMAIL_COLLATION = Collation(locale="en", strength=2)
OTP_EXPIRATION_MINUTES = 15
OTP_MAX_ATTEMPTS = 5
OTP_RESEND_INTERVAL_SECONDS = 60
RESEND_EMAILS_URL = "https://api.resend.com/emails"
GENERIC_OTP_RESPONSE = AuthStatusResponse(
    message="If an account exists for this email, a verification code will be sent.",
    status="success",
    otp_required=True,
)


class EmailProviderConfigurationError(RuntimeError):
    def __init__(self, setting_names: list[str]) -> None:
        self.setting_names = setting_names
        super().__init__()


class EmailProviderDeliveryError(RuntimeError):
    def __init__(self, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__()


def _find_user(db: Database, email: str) -> dict | None:
    return mongo_collection("users", db).find_one(
        {"email": email.strip()},
        collation=EMAIL_COLLATION,
    )


def _email_provider() -> str:
    provider = settings.EMAIL_PROVIDER.strip().lower()
    if provider != "auto":
        return provider
    if os.getenv("RENDER", "").lower() == "true":
        return "resend"
    if settings.EMAIL_API_KEY and settings.EMAIL_FROM:
        return "resend"
    if settings.EMAIL_USER and settings.EMAIL_PASS:
        return "smtp"
    return "resend"


@router.get("/me", response_model=UserResponse)
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Database = Depends(get_db),
):
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication is required.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        claims = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError as exc:
        raise unauthorized from exc

    subject = claims.get("sub")
    user = _find_user(db, subject) if isinstance(subject, str) else None
    if not user or not user.get("is_active", True):
        raise unauthorized
    return UserResponse.model_validate(user)


def _send_otp_email(recipient: str, otp: str) -> None:
    provider = _email_provider()
    message_text = (
        f"Your College ERP verification code is {otp}. "
        f"It expires in {OTP_EXPIRATION_MINUTES} minutes."
    )

    if provider == "resend":
        missing_settings = [
            name
            for name, value in (
                ("EMAIL_API_KEY", settings.EMAIL_API_KEY),
                ("EMAIL_FROM", settings.EMAIL_FROM),
            )
            if not value
        ]
        if missing_settings:
            raise EmailProviderConfigurationError(missing_settings)

        body = json.dumps(
            {
                "from": settings.EMAIL_FROM,
                "to": [recipient],
                "subject": "College ERP OTP Verification",
                "text": message_text,
            }
        ).encode("utf-8")
        request = Request(
            RESEND_EMAILS_URL,
            data=body,
            headers={
                "Authorization": f"Bearer {settings.EMAIL_API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                if not 200 <= response.status < 300:
                    raise EmailProviderDeliveryError(response.status)
        except HTTPError as exc:
            raise EmailProviderDeliveryError(exc.code) from None
        except (OSError, TimeoutError, URLError) as exc:
            raise EmailProviderDeliveryError() from exc
        return

    if provider == "smtp":
        missing_settings = [
            name
            for name, value in (
                ("EMAIL_USER", settings.EMAIL_USER),
                ("EMAIL_PASS", settings.EMAIL_PASS),
            )
            if not value
        ]
        if missing_settings:
            raise EmailProviderConfigurationError(missing_settings)

        message = EmailMessage()
        message["Subject"] = "College ERP OTP Verification"
        message["From"] = settings.EMAIL_USER
        message["To"] = recipient
        message.set_content(message_text)

        try:
            if settings.SMTP_PORT == 465:
                with smtplib.SMTP_SSL(
                    settings.SMTP_HOST,
                    settings.SMTP_PORT,
                    timeout=15,
                    context=ssl.create_default_context(),
                ) as smtp:
                    smtp.login(settings.EMAIL_USER, settings.EMAIL_PASS)
                    smtp.send_message(message)
            else:
                with smtplib.SMTP(
                    settings.SMTP_HOST,
                    settings.SMTP_PORT,
                    timeout=15,
                ) as smtp:
                    smtp.starttls(context=ssl.create_default_context())
                    smtp.login(settings.EMAIL_USER, settings.EMAIL_PASS)
                    smtp.send_message(message)
        except (OSError, smtplib.SMTPException) as exc:
            raise EmailProviderDeliveryError() from exc
        return

    raise EmailProviderConfigurationError(["EMAIL_PROVIDER"])


def _issue_otp(user: dict, db: Database) -> AuthStatusResponse:
    otp = f"{secrets.randbelow(900000) + 100000:06d}"
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=OTP_EXPIRATION_MINUTES)
    collection = mongo_collection("users", db)
    otp_digest = _hash_otp(user["email"], otp)
    reservation = collection.update_one(
        {
            "_id": user["_id"],
            "$or": [
                {"otp_last_sent_at": None},
                {
                    "otp_last_sent_at": {
                        "$lte": now - timedelta(seconds=OTP_RESEND_INTERVAL_SECONDS)
                    }
                },
            ],
        },
        {
            "$set": {
                "otp_code": otp_digest,
                "otp_expires_at": expires_at,
                "otp_attempts": 0,
                "otp_last_sent_at": now,
            }
        },
    )
    if not reservation.matched_count:
        return GENERIC_OTP_RESPONSE

    try:
        _send_otp_email(user["email"], otp)
    except EmailProviderConfigurationError as exc:
        logger.error(
            "OTP email provider is not configured; missing environment variable(s): %s.",
            ", ".join(exc.setting_names),
        )
    except EmailProviderDeliveryError as exc:
        logger.error(
            "OTP email delivery failed (provider=%s, HTTP status=%s).",
            _email_provider(),
            exc.status_code or "unavailable",
        )
    except (OSError, smtplib.SMTPException) as exc:
        logger.error(
            "OTP email delivery failed (provider=%s, error=%s).",
            _email_provider(),
            type(exc).__name__,
        )
    else:
        return GENERIC_OTP_RESPONSE

    collection.update_one(
        {"_id": user["_id"], "otp_code": otp_digest},
        {"$set": {"otp_code": None, "otp_expires_at": None}},
    )
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Verification email delivery is temporarily unavailable. Please try again later.",
    )


def _hash_otp(email: str, otp: str) -> str:
    key = settings.SECRET_KEY.encode("utf-8")
    value = f"{email.strip().lower()}:{otp.strip()}".encode("utf-8")
    return hmac.new(key, value, hashlib.sha256).hexdigest()


def _otp_is_expired(expires_at: datetime | str) -> bool:
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at < datetime.now(timezone.utc)


def _consume_otp(
    user: dict,
    otp: str,
    db: Database,
    updates: dict | Callable[[], dict],
) -> bool:
    stored_digest = user.get("otp_code")
    expires_at = user.get("otp_expires_at")
    attempts = int(user.get("otp_attempts") or 0)
    now = datetime.now(timezone.utc)
    if (
        not stored_digest
        or not expires_at
        or _otp_is_expired(expires_at)
        or attempts >= OTP_MAX_ATTEMPTS
    ):
        return False

    collection = mongo_collection("users", db)
    valid_otp = hmac.compare_digest(
        str(stored_digest),
        _hash_otp(user["email"], otp),
    )
    state_filter = {
        "_id": user["_id"],
        "otp_code": stored_digest,
        "otp_expires_at": {"$gt": now},
        "otp_attempts": {"$lt": OTP_MAX_ATTEMPTS},
    }
    if not valid_otp:
        collection.update_one(state_filter, {"$inc": {"otp_attempts": 1}})
        return False

    result = collection.update_one(
        state_filter,
        {
            "$set": {
                **(updates() if callable(updates) else updates),
                "otp_code": None,
                "otp_expires_at": None,
                "otp_attempts": 0,
            }
        },
    )
    return bool(result.matched_count)


def _invalid_otp_error() -> HTTPException:
    return HTTPException(status_code=400, detail="Invalid or expired OTP code.")


@router.post("/send-otp", response_model=AuthStatusResponse)
def send_otp(payload: OTPRequest, db: Database = Depends(get_db)):
    user = _find_user(db, str(payload.email))
    if not user or not user.get("is_active", True):
        return GENERIC_OTP_RESPONSE

    return _issue_otp(user, db)


@router.post("/verify-otp", response_model=AuthStatusResponse)
def verify_otp(payload: OTPVerify, db: Database = Depends(get_db)):
    user = _find_user(db, str(payload.email))
    if not user:
        raise _invalid_otp_error()

    if not _consume_otp(user, payload.otp, db, {"is_verified": True}):
        raise _invalid_otp_error()
    return AuthStatusResponse(message="OTP verified successfully.", status="success")


@router.post("/signup", response_model=AuthStatusResponse)
def signup(payload: UserCreate, db: Database = Depends(get_db)):
    email = str(payload.email).strip().lower()
    if _find_user(db, email):
        raise HTTPException(status_code=400, detail="Email is already registered.")

    user = {
        "id": next_sequence(db, "users"),
        "name": payload.name.strip(),
        "email": email,
        "hashed_password": get_password_hash(payload.password),
        "role": payload.role or "admin",
        "is_active": True,
        "is_verified": False,
        "otp_code": None,
        "otp_expires_at": None,
        "otp_attempts": 0,
        "otp_last_sent_at": None,
        "failed_attempts": 0,
        "locked_until": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    user["_id"] = str(user["id"])
    try:
        mongo_collection("users", db).insert_one(user)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=400, detail="Email is already registered.") from exc

    try:
        return _issue_otp(user, db)
    except HTTPException:
        mongo_collection("users", db).delete_one({"_id": user["_id"]})
        raise


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Database = Depends(get_db)):
    email = str(payload.email).strip().lower()
    user = _find_user(db, email)
    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not user.get("is_verified", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verify your email address before signing in.",
        )

    now = datetime.now(timezone.utc)
    locked_until = user.get("locked_until")
    if isinstance(locked_until, str):
        locked_until = datetime.fromisoformat(locked_until.replace("Z", "+00:00"))
    if locked_until:
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)
        if locked_until > now:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is temporarily locked due to too many failed attempts. Try again later.",
            )

    collection = mongo_collection("users", db)
    if not verify_password(payload.password, user.get("hashed_password", "")):
        failed_attempts = int(user.get("failed_attempts") or 0) + 1
        updates = {"failed_attempts": failed_attempts}
        if failed_attempts >= LOCKOUT_ATTEMPTS:
            updates["locked_until"] = now + timedelta(hours=LOCKOUT_DURATION_HOURS)
        collection.update_one({"_id": user["_id"]}, {"$set": updates})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"failed_attempts": 0, "locked_until": None}},
    )
    token = create_access_token(subject=user["email"])
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.post("/reset-password", response_model=AuthStatusResponse)
<<<<<<< HEAD
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
=======
def reset_password(payload: PasswordResetConfirm, db: Database = Depends(get_db)):
    user = _find_user(db, str(payload.email))
    if not user:
        raise _invalid_otp_error()

    def password_updates() -> dict:
        if len(payload.newPassword) < 6:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 6 characters.",
            )
        return {
            "hashed_password": get_password_hash(payload.newPassword),
            "failed_attempts": 0,
            "locked_until": None,
            "updated_at": datetime.now(timezone.utc),
        }

    if not _consume_otp(user, payload.otp, db, password_updates):
        raise _invalid_otp_error()
    return AuthStatusResponse(
        message="Password reset successfully. Please log in with your new password.",
        status="success",
    )
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
