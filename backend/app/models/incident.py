"""Community-submitted disaster and safety reports."""

import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.app.database import Base


class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reporter_mobile = Column(String(15), nullable=False)
    event_type = Column(String(40), nullable=False, index=True)
    event_timing = Column(String(16), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(160), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True
    )
    attachments = relationship(
        "IncidentAttachment",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="IncidentAttachment.id",
    )


class IncidentAttachment(Base):
    __tablename__ = "incident_attachments"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("incident_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    stored_name = Column(String(64), nullable=False, unique=True)
    original_name = Column(String(255), nullable=False)
    media_type = Column(String(80), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    report = relationship("IncidentReport", back_populates="attachments")