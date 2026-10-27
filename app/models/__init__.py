from app.core.database import Base
from app.models.user import User
from app.models.student import Student
from app.models.staff import TeachingStaff, NonTeachingStaff
from app.models.academic import Department, Course, AcademicProgram
from app.models.fee import FeeRecord
from app.models.attendance import AttendanceRecord
from app.models.examination import Examination, ExamResult
from app.models.timetable import TimetableSlot
from app.models.library import Book
from app.models.hostel import HostelRoom
from app.models.transport import TransportVehicle
from app.models.document import Document
from app.models.notice import Notice

__all__ = [
    "Base",
    "User",
    "Student",
    "TeachingStaff",
    "NonTeachingStaff",
    "Department",
    "Course",
    "AcademicProgram",
    "FeeRecord",
    "AttendanceRecord",
    "Examination",
    "ExamResult",
    "TimetableSlot",
    "Book",
    "HostelRoom",
    "TransportVehicle",
    "Document",
    "Notice",
]
