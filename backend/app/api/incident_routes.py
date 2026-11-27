"""Authenticated community incident reporting and media endpoints."""

import uuid
import math
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.incident import IncidentAttachment, IncidentReport
from backend.app.models.user import User
from backend.app.schemas.incident import IncidentAttachmentResponse, IncidentReportResponse
from backend.app.security import get_current_user

router = APIRouter(prefix="/incidents", tags=["Community Incident Reports"])

MAX_ATTACHMENTS = 5
MAX_ATTACHMENT_SIZE = 20 * 1024 * 1024
MAX_REPORT_SIZE = 40 * 1024 * 1024
LOCAL_INCIDENT_RADIUS_KM = 50
ALLOWED_MEDIA = {
    "image/jpeg": (".jpg", lambda data: data.startswith(b"\xff\xd8\xff")),
    "image/png": (".png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/gif": (".gif", lambda data: data.startswith((b"GIF87a", b"GIF89a"))),
    "image/webp": (".webp", lambda data: data[:4] == b"RIFF" and data[8:12] == b"WEBP"),
    "video/mp4": (".mp4", lambda data: len(data) >= 12 and data[4:8] == b"ftyp"),
    "video/quicktime": (".mov", lambda data: len(data) >= 12 and data[4:8] == b"ftyp"),
    "video/webm": (".webm", lambda data: data.startswith(b"\x1a\x45\xdf\xa3")),
    "audio/mp4": (".m4a", lambda data: len(data) >= 12 and data[4:8] == b"ftyp"),
    "audio/mpeg": (".mp3", lambda data: data.startswith(b"ID3") or data[:1] == b"\xff"),
    "audio/ogg": (".ogg", lambda data: data.startswith(b"OggS")),
    "audio/webm": (".webm", lambda data: data.startswith(b"\x1a\x45\xdf\xa3")),
}
EVENT_TYPES = {"flood", "landslide", "wildfire", "cyclone", "heatwave", "drought", "infrastructure", "other"}
EVENT_TIMINGS = {"before", "during", "after"}


def serialize_report(report: IncidentReport) -> IncidentReportResponse:
    return IncidentReportResponse(
        id=report.id,
        reporter_mobile=report.reporter_mobile,
        event_type=report.event_type,
        event_timing=report.event_timing,
        description=report.description,
        location=report.location,
        latitude=report.latitude,
        longitude=report.longitude,
        created_at=report.created_at,
        attachments=[
            IncidentAttachmentResponse(
                id=attachment.id,
                name=attachment.original_name,
                media_type=attachment.media_type,
                size_bytes=attachment.size_bytes,
                url=f"/api/incidents/{report.id}/attachments/{attachment.id}",
            )
            for attachment in report.attachments
        ],
    )


@router.get("", response_model=list[IncidentReportResponse])
def list_incident_reports(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.latitude is None or user.longitude is None:
        return []

    latitude_delta = LOCAL_INCIDENT_RADIUS_KM / 111.0
    longitude_delta = LOCAL_INCIDENT_RADIUS_KM / max(
        111.0 * math.cos(math.radians(user.latitude)), 0.01
    )
    candidates = (
        db.query(IncidentReport)
        .filter(
            IncidentReport.latitude.between(user.latitude - latitude_delta, user.latitude + latitude_delta),
            IncidentReport.longitude.between(user.longitude - longitude_delta, user.longitude + longitude_delta),
        )
        .order_by(desc(IncidentReport.created_at))
        .limit(500)
        .all()
    )

    local_reports = []
    for report in candidates:
        latitude_delta_radians = math.radians(report.latitude - user.latitude)
        longitude_delta_radians = math.radians(report.longitude - user.longitude)
        haversine = (
            math.sin(latitude_delta_radians / 2) ** 2
            + math.cos(math.radians(user.latitude))
            * math.cos(math.radians(report.latitude))
            * math.sin(longitude_delta_radians / 2) ** 2
        )
        distance_km = 6371.0 * 2 * math.asin(math.sqrt(min(1.0, haversine)))
        if distance_km <= LOCAL_INCIDENT_RADIUS_KM:
            local_reports.append(serialize_report(report))
            if len(local_reports) == limit:
                break
    return local_reports


@router.post("", response_model=IncidentReportResponse, status_code=status.HTTP_201_CREATED)
async def create_incident_report(
    event_type: str = Form(...),
    event_timing: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    files: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if event_type not in EVENT_TYPES:
        raise HTTPException(status_code=422, detail="Select a valid incident type.")
    if event_timing not in EVENT_TIMINGS:
        raise HTTPException(status_code=422, detail="Select when the incident occurred.")
    description = description.strip()
    location = location.strip()
    if not 5 <= len(description) <= 2000:
        raise HTTPException(status_code=422, detail="Description must be between 5 and 2,000 characters.")
    if not 2 <= len(location) <= 160:
        raise HTTPException(status_code=422, detail="Select a valid incident location.")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise HTTPException(status_code=422, detail="Incident coordinates are outside valid map bounds.")
    if len(files) > MAX_ATTACHMENTS:
        raise HTTPException(status_code=413, detail=f"Attach no more than {MAX_ATTACHMENTS} photos or videos.")

    staged_uploads = []
    total_size = 0
    for upload in files:
        media_type = (upload.content_type or "").split(";", 1)[0].lower()
        media_spec = ALLOWED_MEDIA.get(media_type)
        if media_spec is None:
            raise HTTPException(
                status_code=415,
                detail="Use JPG, PNG, GIF, WebP, MP4, MOV, WebM, M4A, MP3, or OGG files.",
            )
        content = await upload.read(MAX_ATTACHMENT_SIZE + 1)
        total_size += len(content)
        if len(content) > MAX_ATTACHMENT_SIZE or total_size > MAX_REPORT_SIZE:
            raise HTTPException(status_code=413, detail="Media is too large. Each file is limited to 20 MB and total upload to 40 MB.")
        if not media_spec[1](content):
            raise HTTPException(status_code=415, detail="An attachment does not match its declared image or video type.")
        stored_name = f"{uuid.uuid4().hex}{media_spec[0]}"
        original_name = Path(upload.filename or "incident-media").name[:255]
        staged_uploads.append((content, stored_name, original_name, media_type))

    report = IncidentReport(
        reporter_id=user.id,
        reporter_mobile=user.mobile_number,
        event_type=event_type,
        event_timing=event_timing,
        description=description,
        location=location,
        latitude=latitude,
        longitude=longitude,
    )
    db.add(report)
    saved_paths = []
    try:
        db.flush()
        settings.INCIDENT_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        for content, stored_name, original_name, media_type in staged_uploads:
            file_path = settings.INCIDENT_MEDIA_DIR / stored_name
            file_path.write_bytes(content)
            saved_paths.append(file_path)
            db.add(
                IncidentAttachment(
                    report_id=report.id,
                    stored_name=stored_name,
                    original_name=original_name,
                    media_type=media_type,
                    size_bytes=len(content),
                )
            )
        db.commit()
        db.refresh(report)
    except Exception as exc:
        db.rollback()
        for file_path in saved_paths:
            file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Unable to save the incident report.") from exc

    return serialize_report(report)


@router.get("/{report_id}/attachments/{attachment_id}")
def get_incident_attachment(
    report_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    attachment = db.query(IncidentAttachment).filter_by(id=attachment_id, report_id=report_id).first()
    if attachment is None:
        raise HTTPException(status_code=404, detail="Incident attachment not found.")
    file_path = settings.INCIDENT_MEDIA_DIR / attachment.stored_name
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Incident media file is missing.")
    return FileResponse(
        file_path,
        media_type=attachment.media_type,
        headers={"Content-Disposition": "inline", "Cache-Control": "private, no-store"},
    )