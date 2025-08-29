from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db import Base


class ModerationRequest(Base):
    __tablename__ = "moderation_requests"


    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=False)
    content_type = Column(String, nullable=False) # "text" | "image"
    content_hash = Column(String, nullable=False)
    status = Column(String, nullable=False, default="processed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    results = relationship("ModerationResult", back_populates="request", cascade="all, delete-orphan")
    notifications = relationship("NotificationLog", back_populates="request", cascade="all, delete-orphan")


class ModerationResult(Base):
    __tablename__ = "moderation_results"


    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"), nullable=False)
    classification = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text)
    llm_response = Column(Text)


    request = relationship("ModerationRequest", back_populates="results")


class NotificationLog(Base):
    __tablename__ = "notification_logs"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"), nullable=False)
    channel = Column(String, nullable=False) # "slack" | "email"
    status = Column(String, nullable=False) # "sent" | "failed"
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    request = relationship("ModerationRequest", back_populates="notifications")
