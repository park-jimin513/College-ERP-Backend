<<<<<<< HEAD
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.timetable import TimetableSlot
=======
from typing import Dict, List

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.core.database import get_db
from app.core.mongo import mongo_collection
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
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
<<<<<<< HEAD
    "Mechanical": "Block C - 301"
=======
    "Mechanical": "Block C - 301",
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
}


@router.get("", response_model=TimetableGridResponse)
def get_timetable(
    department: str = Query("CSE", description="Department code"),
    section: str = Query("A", description="Section (A or B)"),
<<<<<<< HEAD
    db: Session = Depends(get_db)
=======
    db: Database = Depends(get_db),
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
):
    subjects = SUBJECT_POOL.get(department, SUBJECT_POOL["CSE"])
    faculty = FACULTY_POOL.get(department, FACULTY_POOL["CSE"])
    room = ROOM_POOL.get(department, ROOM_POOL["CSE"])
<<<<<<< HEAD

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
=======
    slots = {
        (slot["day"], slot["periodIndex"]): slot
        for slot in mongo_collection("timetable_slots", db).find(
            {"department": department, "section": section}
        )
    }

    grid: Dict[str, List[TimetablePeriodItem]] = {}
    for day_index, day in enumerate(DAYS):
        day_slots: List[TimetablePeriodItem] = []
        for period_index, _ in enumerate(PERIODS):
            db_slot = slots.get((day, period_index))
            if db_slot:
                day_slots.append(
                    TimetablePeriodItem(
                        subject=db_slot["subject"],
                        faculty=db_slot.get("faculty") or faculty,
                        room=db_slot.get("room") or room,
                    )
                )
                continue

            offset = 2 if section == "B" else 0
            subject = subjects[(day_index + period_index + offset) % len(subjects)]
            is_lab = subject == "Lab"
            day_slots.append(
                TimetablePeriodItem(
                    subject=subject,
                    faculty=f"{faculty} + Lab Assistant" if is_lab else faculty,
                    room=f"{room} Lab" if is_lab else room,
                )
            )
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
        grid[day] = day_slots

    return TimetableGridResponse(
        department=department,
        section=section,
        days=DAYS,
        periods=PERIODS,
<<<<<<< HEAD
        grid=grid
=======
        grid=grid,
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    )
