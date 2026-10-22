from datetime import datetime, timedelta, timezone
import logging
import secrets
import smtplib
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


class MissingEmailSettingsError(RuntimeError):
    def __init__(self, setting_names: list[str]) -> None:
        self.setting_names = setting_names
        super().__init__()


def _find_user(db: Database, email: str) -> dict | None:
    return mongo_collection("users", db).find_one(
        {"email": email.strip()},
        collation=EMAIL_COLLATION,
    )


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
    missing_settings = [
        name
        for name, value in (
            ("EMAIL_USER", settings.EMAIL_USER),
            ("EMAIL_PASS", settings.EMAIL_PASS),
        )
        if not value
    ]
    if missing_settings:
        raise MissingEmailSettingsError(missing_settings)

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


def _issue_otp(user: dict, db: Database) -> AuthStatusResponse:
    otp = f"{secrets.randbelow(900000) + 100000}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    collection = mongo_collection("users", db)
    collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"otp_code": otp, "otp_expires_at": expires_at}},
    )

    try:
        _send_otp_email(user["email"], otp)
    except MissingEmailSettingsError as exc:
        logger.error(
            "OTP email was not sent: missing required environment variable(s): %s.",
            ", ".join(exc.setting_names),
        )
        email_error = exc
    except (OSError, smtplib.SMTPException) as exc:
        logger.error(
            "OTP email delivery failed while communicating with the configured SMTP server (%s).",
            type(exc).__name__,
        )
        email_error = exc
    else:
        return AuthStatusResponse(
            message=f"OTP sent to {user['email']} (valid for 15 minutes).",
            status="success",
            otp_required=True,
        )

    collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"otp_code": None, "otp_expires_at": None}},
    )
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Could not send the verification email. Check SMTP configuration and try again.",
    ) from email_error


def _otp_is_expired(expires_at: datetime | str) -> bool:
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at < datetime.now(timezone.utc)


def _validate_otp(user: dict, otp: str) -> None:
    if not user.get("otp_code") or not user.get("otp_expires_at"):
        raise HTTPException(status_code=400, detail="No OTP has been requested for this account.")
    if _otp_is_expired(user["otp_expires_at"]):
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")
    if str(user["otp_code"]).strip() != otp.strip():
        raise HTTPException(status_code=400, detail="Invalid OTP code.")


@router.post("/send-otp", response_model=AuthStatusResponse)
def send_otp(payload: OTPRequest, db: Database = Depends(get_db)):
    user = _find_user(db, str(payload.email))
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found.")

    return _issue_otp(user, db)


@router.post("/verify-otp", response_model=AuthStatusResponse)
def verify_otp(payload: OTPVerify, db: Database = Depends(get_db)):
    user = _find_user(db, str(payload.email))
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found.")

    _validate_otp(user, payload.otp)
    mongo_collection("users", db).update_one(
        {"_id": user["_id"]},
        {"$set": {"otp_code": None, "otp_expires_at": None, "is_verified": True}},
    )
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
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.post("/reset-password", response_model=AuthStatusResponse)
def reset_password(payload: PasswordResetConfirm, db: Database = Depends(get_db)):
    user = _find_user(db, str(payload.email))
    if not user:
        raise HTTPException(status_code=404, detail="User with this email not found.")
    _validate_otp(user, payload.otp)

    if len(payload.newPassword) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    mongo_collection("users", db).update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "hashed_password": get_password_hash(payload.newPassword),
                "failed_attempts": 0,
                "locked_until": None,
                "otp_code": None,
                "otp_expires_at": None,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    return AuthStatusResponse(
        message="Password reset successfully. Please log in with your new password.",
        status="success",
    )
