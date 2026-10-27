from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    category = Column(String(50), default="General")  # General, Examination, Event, Holiday, Urgent
    priority = Column(String(50), default="Normal")  # Normal, High
    audienceType = Column(String(50), default="Entire College")  # Entire College, Department, Batch, Section
    audienceValue = Column(String(100), nullable=True)  # e.g. CSE, 2023 - 2027, A
    content = Column(Text, nullable=False)
    publishOption = Column(String(50), default="Publish Now")
    scheduleDate = Column(String(100), nullable=True)
    attachmentUrl = Column(String(255), nullable=True)
    publishedBy = Column(String(100), default="Admin")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
