"""Incident report response schemas."""

import datetime

from pydantic import BaseModel


class IncidentAttachmentResponse(BaseModel):
    id: int
    name: str
    media_type: str
    size_bytes: int
    url: str


class IncidentReportResponse(BaseModel):
    id: int
    reporter_mobile: str
    event_type: str
    event_timing: str
    description: str
    location: str
    latitude: float
    longitude: float
    created_at: datetime.datetime
    attachments: list[IncidentAttachmentResponse]