from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.timetable import TimetableSlot
from app.schemas.timetable import TimetableGridResponse, TimetablePeriodItem

router = APIRouter(prefix="/timetable", tags=["Timetable"])

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

PERIODS = [
    "9:00 – 9:50",
    "9:50 – 10:40",
    "10:55 – 11:45",
    "11:45 – 12:35",
    "1:30 – 2:20",
    "2:20 – 3:10",
    "3:25 – 4:15",
]

SUBJECT_POOL = {
    "CSE": ["Data Structures", "DBMS", "Operating Systems", "DAA", "Computer Networks", "Lab"],
    "CSE-AI": ["Machine Learning", "Neural Networks", "Python for AI", "Statistics", "NLP", "Lab"],
    "ECE": ["Digital Electronics", "Signal Processing", "VLSI Design", "Communication Systems", "EMFT", "Lab"],
    "Civil": ["Structural Analysis", "Surveying", "Geotechnical Engg", "Concrete Technology", "Estimation", "Lab"],
    "Mechanical": ["Thermodynamics", "Fluid Mechanics", "Machine Design", "Manufacturing Tech", "CAD/CAM", "Lab"],
}

FACULTY_POOL = {
    "CSE": "Dr. Kavitha Kumar",
    "CSE-AI": "Ms. Priyanka Das",
    "ECE": "Prof. Suresh Iyer",
    "Civil": "Mr. Anil Kapoor",
    "Mechanical": "Dr. Ramesh Naidu",
}

ROOM_POOL = {
    "CSE": "Block A - 101",
    "CSE-AI": "Block B - 210",
    "ECE": "Block B - 201",
    "Civil": "Block A - 105",
    "Mechanical": "Block C - 301"
}


@router.get("", response_model=TimetableGridResponse)
def get_timetable(
    department: str = Query("CSE", description="Department code"),
    section: str = Query("A", description="Section (A or B)"),
    db: Session = Depends(get_db)
):
    subjects = SUBJECT_POOL.get(department, SUBJECT_POOL["CSE"])
    faculty = FACULTY_POOL.get(department, FACULTY_POOL["CSE"])
    room = ROOM_POOL.get(department, ROOM_POOL["CSE"])

    grid: Dict[str, List[TimetablePeriodItem]] = {}

    for day_index, day in enumerate(DAYS):
        day_slots: List[TimetablePeriodItem] = []
        for period_index, _ in enumerate(PERIODS):
            # Check if custom slot exists in DB
            db_slot = db.query(TimetableSlot).filter(
                TimetableSlot.department == department,
                TimetableSlot.section == section,
                TimetableSlot.day == day,
                TimetableSlot.periodIndex == period_index
            ).first()

            if db_slot:
                day_slots.append(TimetablePeriodItem(
                    subject=db_slot.subject,
                    faculty=db_slot.faculty or faculty,
                    room=db_slot.room or room
                ))
            else:
                offset = 2 if section == "B" else 0
                idx = (day_index + period_index + offset) % len(subjects)
                subj = subjects[idx]
                is_lab = subj == "Lab"
                day_slots.append(TimetablePeriodItem(
                    subject=subj,
                    faculty=f"{faculty} + Lab Assistant" if is_lab else faculty,
                    room=f"{room} Lab" if is_lab else room
                ))
        grid[day] = day_slots

    return TimetableGridResponse(
        department=department,
        section=section,
        days=DAYS,
        periods=PERIODS,
        grid=grid
    )
