from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(50), primary_key=True, index=True)  # e.g. DOC-5001
    name = Column(String(150), nullable=False, index=True)
    owner = Column(String(150), nullable=False, index=True)
    ownerType = Column(String(50), default="Student")  # Student, Staff
    category = Column(String(50), default="Academic")  # Identity, Academic, Admission, Transfer, HR
    uploadedOn = Column(String(50), nullable=True)
    status = Column(String(50), default="Pending")  # Verified, Pending, Rejected
    fileUrl = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
