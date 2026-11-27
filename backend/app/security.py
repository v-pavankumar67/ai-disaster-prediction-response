"""Password hashing and signed authentication cookie helpers."""

import base64
import hashlib
import hmac
import secrets
import time
from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.user import User

AUTH_COOKIE_NAME = "disaster_session"
PASSWORD_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    encoded_salt = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
    encoded_digest = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${encoded_salt}${encoded_digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_text, encoded_salt, encoded_digest = password_hash.split("$")
        iterations = int(iterations_text)
        if algorithm != "pbkdf2_sha256" or not 1 <= iterations <= 1_000_000:
            return False
        salt = base64.urlsafe_b64decode(encoded_salt + "=" * (-len(encoded_salt) % 4))
        expected = base64.urlsafe_b64decode(encoded_digest + "=" * (-len(encoded_digest) % 4))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_auth_token(user_id: int) -> str:
    expires_at = int(time.time()) + settings.AUTH_SESSION_TTL_SECONDS
    payload = base64.urlsafe_b64encode(f"{user_id}:{expires_at}".encode("ascii"))
    encoded_payload = payload.decode("ascii").rstrip("=")
    signature = hmac.new(
        settings.AUTH_SECRET_KEY.encode("utf-8"),
        encoded_payload.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    return f"{encoded_payload}.{signature}"


def get_token_user_id(token: Optional[str]) -> Optional[int]:
    if not token:
        return None
    try:
        encoded_payload, signature = token.split(".", 1)
        expected_signature = hmac.new(
            settings.AUTH_SECRET_KEY.encode("utf-8"),
            encoded_payload.encode("ascii"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return None
        payload = base64.urlsafe_b64decode(encoded_payload + "=" * (-len(encoded_payload) % 4))
        user_id_text, expires_at_text = payload.decode("ascii").split(":", 1)
        user_id = int(user_id_text)
        if user_id < 1 or int(expires_at_text) <= int(time.time()):
            return None
        return user_id
    except (ValueError, TypeError, UnicodeDecodeError):
        return None


def set_auth_cookie(response, user_id: int) -> None:
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=create_auth_token(user_id),
        max_age=settings.AUTH_SESSION_TTL_SECONDS,
        httponly=True,
        secure=settings.ENVIRONMENT.lower() in {"production", "prod"},
        samesite="lax",
        path="/",
    )


def get_optional_current_user(
    request: Request, db: Session = Depends(get_db)
) -> Optional[User]:
    user_id = get_token_user_id(request.cookies.get(AUTH_COOKIE_NAME))
    user = db.get(User, user_id) if user_id is not None else None
    if user is not None and user.is_demo and not settings.DEMO_LOGIN_ENABLED:
        return None
    return user


def get_current_user(
    user: Optional[User] = Depends(get_optional_current_user),
) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="Please sign in to continue.")
    return user