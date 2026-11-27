"""Registration, login, and logout endpoints."""

import threading
import time

import requests
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi import Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import SessionLocal, get_db
from backend.app.models.user import User
from backend.app.schemas.auth import (
    AuthResponse,
    LocationUpdateRequest,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from backend.app.security import (
    AUTH_COOKIE_NAME,
    get_current_user,
    hash_password,
    set_auth_cookie,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
DEMO_MOBILE_NUMBER = "9999999999"
DEMO_PASSWORD = "Rescue@2026!"
_LOCATION_SEARCH_LOCK = threading.Lock()
_LAST_LOCATION_SEARCH = 0.0


def seed_demo_account() -> None:
    if not settings.DEMO_LOGIN_ENABLED:
        return
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.mobile_number == DEMO_MOBILE_NUMBER).first()
        if existing is None:
            db.add(
                User(
                    mobile_number=DEMO_MOBILE_NUMBER,
                    location="Emergency Operations Center",
                    password_hash=hash_password(DEMO_PASSWORD),
                    is_demo=True,
                )
            )
            db.commit()
    finally:
        db.close()


@router.get("/demo-credentials")
def demo_credentials():
    if not settings.DEMO_LOGIN_ENABLED:
        raise HTTPException(status_code=404, detail="Demo login is disabled.")
    return {"mobile_number": DEMO_MOBILE_NUMBER, "password": DEMO_PASSWORD}


@router.get("/locations/search")
def search_locations(q: str = Query(min_length=3, max_length=120)):
    """Resolve a typed place query using OpenStreetMap Nominatim."""
    global _LAST_LOCATION_SEARCH
    with _LOCATION_SEARCH_LOCK:
        wait_seconds = 1.05 - (time.monotonic() - _LAST_LOCATION_SEARCH)
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        _LAST_LOCATION_SEARCH = time.monotonic()

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q.strip(), "format": "jsonv2", "limit": 5, "addressdetails": 1},
            headers={"User-Agent": "AI-Disaster-Prediction-Response/1.0"},
            timeout=8,
        )
        response.raise_for_status()
        places = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Location search is temporarily unavailable. Please try again.",
        ) from exc

    results = []
    for place in places:
        try:
            results.append(
                {
                    "name": place["display_name"],
                    "latitude": float(place["lat"]),
                    "longitude": float(place["lon"]),
                }
            )
        except (KeyError, TypeError, ValueError):
            continue
    return {"results": results}


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    request_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.mobile_number == request_data.mobile_number).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="An account with this mobile number already exists.")

    user = User(
        mobile_number=request_data.mobile_number,
        location=request_data.location,
        latitude=request_data.latitude,
        longitude=request_data.longitude,
        password_hash=hash_password(request_data.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this mobile number already exists.") from exc
    db.refresh(user)

    response = Response(
        content=AuthResponse(user=UserResponse.model_validate(user)).model_dump_json(),
        media_type="application/json",
        status_code=status.HTTP_201_CREATED,
    )
    set_auth_cookie(response, user.id)
    return response


@router.post("/login", response_model=AuthResponse)
def login(
    request_data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.mobile_number == request_data.mobile_number).first()
    if (
        user is None
        or (user.is_demo and not settings.DEMO_LOGIN_ENABLED)
        or not verify_password(request_data.password, user.password_hash)
    ):
        raise HTTPException(status_code=401, detail="Mobile number or password is incorrect.")

    response = Response(
        content=AuthResponse(user=UserResponse.model_validate(user)).model_dump_json(),
        media_type="application/json",
    )
    set_auth_cookie(response, user.id)
    return response


@router.get("/me", response_model=UserResponse)
def current_user(user: User = Depends(get_current_user)):
    return user


@router.put("/me/location", response_model=UserResponse)
def update_current_user_location(
    location_data: LocationUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.location = location_data.location
    user.latitude = location_data.latitude
    user.longitude = location_data.longitude
    db.commit()
    db.refresh(user)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.ENVIRONMENT.lower() in {"production", "prod"},
        samesite="lax",
    )
    return response