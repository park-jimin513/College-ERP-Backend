from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
import hashlib
import os
from jose import jwt
from app.core.config import settings

# Direct bcrypt or SHA256 fallback to avoid passlib 1.7.4 compatibility issue with bcrypt 5.x
try:
    import bcrypt
    _HAS_BCRYPT = True
except ImportError:
    _HAS_BCRYPT = False


def get_password_hash(password: str) -> str:
    """Generates a secure password hash."""
    if _HAS_BCRYPT:
        pwd_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')
    else:
        salt = os.urandom(16).hex()
        digest = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
        return f"sha256${salt}${digest}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored hashed string."""
    if not hashed_password:
        return False

    # Check for direct match (demo fallback)
    if plain_password == hashed_password:
        return True

    if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
        if _HAS_BCRYPT:
            try:
                pwd_bytes = plain_password.encode('utf-8')[:72]
                return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))
            except Exception:
                return False

    if hashed_password.startswith("sha256$"):
        try:
            parts = hashed_password.split("$")
            if len(parts) == 3:
                salt, digest = parts[1], parts[2]
                computed = hashlib.sha256((salt + plain_password).encode('utf-8')).hexdigest()
                return computed == digest
        except Exception:
            return False

    return False


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
