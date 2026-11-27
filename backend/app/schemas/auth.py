"""Authentication request and response schemas."""

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    mobile_number: str = Field(min_length=10, max_length=32)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("mobile_number")
    @classmethod
    def normalize_mobile_number(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if not 10 <= len(digits) <= 15:
            raise ValueError("Enter a valid mobile number with 10 to 15 digits.")
        return digits


class RegisterRequest(LoginRequest):
    location: str = Field(min_length=2, max_length=160)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("location")
    @classmethod
    def normalize_location(cls, value: str) -> str:
        location = value.strip()
        if len(location) < 2:
            raise ValueError("Enter a location with at least 2 characters.")
        return location


class LocationUpdateRequest(BaseModel):
    location: str = Field(min_length=2, max_length=160)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    @field_validator("location")
    @classmethod
    def normalize_location(cls, value: str) -> str:
        location = value.strip()
        if len(location) < 2:
            raise ValueError("Select a valid location.")
        return location


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mobile_number: str
    location: str
    latitude: float | None = None
    longitude: float | None = None
    is_demo: bool


class AuthResponse(BaseModel):
    user: UserResponse