"""Telemetry alert filtering and deduplication tests."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import main
from backend.app.api import auth_routes
from backend.app.config import settings
from backend.app.database import get_db


def make_client(tmp_path, monkeypatch):
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'telemetry-test.db'}",
        connect_args={"check_same_thread": False},
    )
    test_session = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(main, "engine", test_engine)
    monkeypatch.setattr(auth_routes, "SessionLocal", test_session)
    monkeypatch.setattr(settings, "INCIDENT_MEDIA_DIR", tmp_path / "incident_uploads")
    main.app.dependency_overrides[get_db] = override_get_db
    main.Base.metadata.create_all(bind=test_engine)
    auth_routes.seed_demo_account()

    return TestClient(main.app)


def test_local_alerts_are_deduplicated_and_location_scoped(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)

    login = client.post(
        "/api/auth/login",
        json={"mobile_number": "9999999999", "password": "Rescue@2026!"},
    )
    assert login.status_code == 200

    client.put(
        "/api/auth/me/location",
        json={"location": "Hyderabad, Telangana, India", "latitude": 17.385, "longitude": 78.4867},
    )

    response = client.get("/api/telemetry/alerts", params={"lat": 17.385, "lon": 78.4867, "radius_km": 60})
    assert response.status_code == 200

    payload = response.json()
    assert payload["location"] == {"latitude": 17.385, "longitude": 78.4867}
    assert payload["alert_count"] == len(payload["alerts"])
    assert len(payload["alerts"]) == len({(item["type"], item["source"], item["title"]) for item in payload["alerts"]})
    assert all(item["distance_km"] <= 60.0 for item in payload["alerts"])
