"""Authentication API and credential storage tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import main
from backend.app.api import auth_routes
from backend.app.config import settings
from backend.app.database import Base, get_db
from backend.app.models.user import User


@pytest.fixture
def auth_client(tmp_path, monkeypatch):
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'auth-test.db'}",
        connect_args={"check_same_thread": False},
    )
    test_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = test_session_local()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(main, "engine", test_engine)
    monkeypatch.setattr(auth_routes, "SessionLocal", test_session_local)
    main.app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(main.app) as client:
            yield client, test_session_local
    finally:
        main.app.dependency_overrides.pop(get_db, None)
        test_engine.dispose()


def test_register_hashes_password_and_rejects_duplicate_mobile(auth_client):
    client, test_session_local = auth_client
    payload = {
        "mobile_number": "+91 98765-43210",
        "location": "Kochi, Kerala, India",
        "latitude": 9.9312,
        "longitude": 76.2673,
        "password": "StrongPass123!",
    }

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 201
    assert response.json()["user"]["mobile_number"] == "919876543210"
    assert "password" not in response.json()
    assert "httponly" in response.headers["set-cookie"].lower()
    with test_session_local() as db:
        user = db.query(User).filter_by(mobile_number="919876543210").one()
        assert user.password_hash.startswith("pbkdf2_sha256$")
        assert user.password_hash != payload["password"]
        assert user.latitude == 9.9312
        assert user.longitude == 76.2673

    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_register_requires_coordinates_from_a_selected_place(auth_client):
    client, _ = auth_client

    response = client.post(
        "/api/auth/register",
        json={
            "mobile_number": "9876543211",
            "location": "Hyderabad, Telangana, India",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 422


def test_location_search_returns_geocoded_places(auth_client, monkeypatch):
    client, _ = auth_client

    class GeocoderResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return [
                {
                    "display_name": "Hyderabad, Telangana, India",
                    "lat": "17.3850",
                    "lon": "78.4867",
                }
            ]

    def fake_get(url, *, params, headers, timeout):
        assert url == "https://nominatim.openstreetmap.org/search"
        assert params["q"] == "Hyderabad"
        assert "User-Agent" in headers
        assert timeout > 0
        return GeocoderResponse()

    monkeypatch.setattr(auth_routes.requests, "get", fake_get)

    response = client.get("/api/auth/locations/search", params={"q": "Hyderabad"})

    assert response.status_code == 200
    assert response.json()["results"] == [
        {
            "name": "Hyderabad, Telangana, India",
            "latitude": 17.385,
            "longitude": 78.4867,
        }
    ]


def test_login_and_logout_control_dashboard_session(auth_client):
    client, _ = auth_client
    client.post(
        "/api/auth/register",
        json={
            "mobile_number": "9876543210",
            "location": "Aluva, Kerala, India",
            "latitude": 10.1076,
            "longitude": 76.3516,
            "password": "StrongPass123!",
        },
    )
    client.post("/api/auth/logout")

    assert client.get("/", follow_redirects=False).headers["location"] == "/login"
    assert client.post(
        "/api/auth/login",
        json={"mobile_number": "9876543210", "password": "incorrect"},
    ).status_code == 401

    login_response = client.post(
        "/api/auth/login",
        json={"mobile_number": "9876543210", "password": "StrongPass123!"},
    )
    assert login_response.status_code == 200
    assert client.get("/api/auth/me").json()["location"] == "Aluva, Kerala, India"
    assert client.get("/api/auth/me").json()["latitude"] == 10.1076
    assert client.get("/api/auth/me").json()["longitude"] == 76.3516
    assert client.get("/").status_code == 200

    update_response = client.put(
        "/api/auth/me/location",
        json={
            "location": "Hyderabad, Telangana, India",
            "latitude": 17.385,
            "longitude": 78.4867,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["location"] == "Hyderabad, Telangana, India"
    assert update_response.json()["latitude"] == 17.385
    assert client.get("/api/auth/me").json()["longitude"] == 78.4867

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/", follow_redirects=False).headers["location"] == "/login"


def test_location_update_requires_login(auth_client):
    client, _ = auth_client

    response = client.put(
        "/api/auth/me/location",
        json={
            "location": "Hyderabad, Telangana, India",
            "latitude": 17.385,
            "longitude": 78.4867,
        },
    )

    assert response.status_code == 401


def test_demo_emergency_credentials_are_seeded(auth_client):
    client, _ = auth_client

    response = client.post(
        "/api/auth/login",
        json={
            "mobile_number": auth_routes.DEMO_MOBILE_NUMBER,
            "password": auth_routes.DEMO_PASSWORD,
        },
    )

    assert response.status_code == 200
    assert response.json()["user"]["is_demo"] is True
    assert client.get("/api/auth/me").status_code == 200


def test_demo_account_is_unavailable_when_demo_mode_is_disabled(auth_client, monkeypatch):
    client, _ = auth_client
    login_response = client.post(
        "/api/auth/login",
        json={
            "mobile_number": auth_routes.DEMO_MOBILE_NUMBER,
            "password": auth_routes.DEMO_PASSWORD,
        },
    )
    assert login_response.status_code == 200

    monkeypatch.setattr(settings, "DEMO_LOGIN_ENABLED", False)

    assert client.get("/api/auth/demo-credentials").status_code == 404
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/", follow_redirects=False).headers["location"] == "/login"