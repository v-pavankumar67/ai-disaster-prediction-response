"""Registered platform users."""

import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from backend.app.database import Base


class User(Base):
    """A user account with a one-way password hash."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String(15), unique=True, nullable=False, index=True)
    location = Column(String(160), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    password_hash = Column(String(256), nullable=False)
    is_demo = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )