from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(String(50), primary_key=True, index=True)  # e.g. LIB-1001
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(150), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    copies = Column(Integer, default=1)
    available = Column(Integer, default=1)
    issuedTo = Column(String(150), default="—")
    dueDate = Column(String(50), default="—")
    status = Column(String(50), default="Available")  # Available, Issued, Overdue
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
