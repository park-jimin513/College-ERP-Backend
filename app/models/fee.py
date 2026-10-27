from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.core.database import Base


class FeeRecord(Base):
    __tablename__ = "fee_records"

    id = Column(String(50), primary_key=True, index=True)  # student ID or record ID
    name = Column(String(150), nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    feeType = Column(String(50), default="Tuition")  # Tuition, Hostel, Transport, Exam Fee
    totalFee = Column(String(50), default="₹0")
    paid = Column(String(50), default="₹0")
    pending = Column(String(50), default="₹0")
    dueDate = Column(String(50), nullable=True)
    status = Column(String(50), default="Pending")  # Paid, Partial, Overdue
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
