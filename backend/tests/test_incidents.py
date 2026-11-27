"""Incident report and uploaded media API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import main
from backend.app.api import auth_routes
from backend.app.config import settings
from backend.app.database import get_db


@pytest.fixture
def incident_client(tmp_path, monkeypatch):
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'incident-test.db'}",
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
    monkeypatch.setattr(settings, "INCIDENT_MEDIA_DIR", tmp_path / "incident_uploads")
    main.app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(main.app) as client:
            yield client, tmp_path / "incident_uploads"
    finally:
        main.app.dependency_overrides.pop(get_db, None)
        test_engine.dispose()


def sign_in_demo(client):
    response = client.post(
        "/api/auth/login",
        json={"mobile_number": "9999999999", "password": "Rescue@2026!"},
    )
    if response.status_code == 200:
        client.put(
            "/api/auth/me/location",
            json={"location": "Hyderabad, Telangana, India", "latitude": 17.385, "longitude": 78.4867},
        )
    return response


def incident_form_data():
    return {
        "event_type": "flood",
        "event_timing": "during",
        "description": "Flood water is crossing the access road.",
        "location": "Hyderabad, Telangana, India",
        "latitude": "17.385",
        "longitude": "78.4867",
    }


def test_incident_report_saves_reporter_and_private_photo_video_audio(incident_client):
    client, media_directory = incident_client
    assert sign_in_demo(client).status_code == 200

    photo = b"\x89PNG\r\n\x1a\n" + b"fake png bytes"
    video = b"\x00\x00\x00\x18ftypmp42" + b"fake mp4 bytes"
    voice_note = b"\x1a\x45\xdf\xa3" + b"fake webm audio bytes"
    response = client.post(
        "/api/incidents",
        data=incident_form_data(),
        files=[
            ("files", ("road.jpg.png", photo, "image/png")),
            ("files", ("flood.mp4", video, "video/mp4")),
            ("files", ("voice-note.webm", voice_note, "audio/webm")),
        ],
    )

    assert response.status_code == 201
    report = response.json()
    assert report["reporter_mobile"] == "9999999999"
    assert report["event_type"] == "flood"
    assert report["event_timing"] == "during"
    assert report["location"] == "Hyderabad, Telangana, India"
    assert len(report["attachments"]) == 3
    assert report["attachments"][2]["media_type"] == "audio/webm"
    assert len(list(media_directory.iterdir())) == 3

    feed_response = client.get("/api/incidents")
    assert feed_response.status_code == 200
    assert feed_response.json()[0]["id"] == report["id"]

    outside_report_data = incident_form_data()
    outside_report_data.update({
        "location": "Kochi, Kerala, India",
        "latitude": "9.9312",
        "longitude": "76.2673",
    })
    outside_response = client.post("/api/incidents", data=outside_report_data)
    assert outside_response.status_code == 201
    assert [item["id"] for item in client.get("/api/incidents").json()] == [report["id"]]

    media_response = client.get(report["attachments"][0]["url"])
    assert media_response.status_code == 200
    assert media_response.content == photo

    audio_response = client.get(report["attachments"][2]["url"])
    assert audio_response.status_code == 200
    assert audio_response.headers["content-type"] == "audio/webm"
    assert audio_response.content == voice_note


def test_incident_reports_and_media_require_login(incident_client):
    client, _ = incident_client

    assert client.get("/api/incidents").status_code == 401
    assert client.post("/api/incidents", data=incident_form_data()).status_code == 401
    assert client.get("/api/incidents/1/attachments/1").status_code == 401


def test_incident_upload_rejects_unapproved_or_mismatched_media(incident_client):
    client, media_directory = incident_client
    assert sign_in_demo(client).status_code == 200

    response = client.post(
        "/api/incidents",
        data=incident_form_data(),
        files=[("files", ("script.png", b"not an image", "image/png"))],
    )

    assert response.status_code == 415
    assert not media_directory.exists()