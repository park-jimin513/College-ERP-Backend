from typing import List
<<<<<<< HEAD
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.student import Student
from app.models.staff import TeachingStaff, NonTeachingStaff
from app.models.academic import Department
from app.models.fee import FeeRecord
from app.models.notice import Notice
from app.schemas.dashboard import DashboardStatsResponse, StatCardItem, ActivityItem
=======

from fastapi import APIRouter, Depends
from pymongo.database import Database

from app.core.database import get_db
from app.core.mongo import list_documents, mongo_collection
from app.schemas.dashboard import ActivityItem, DashboardStatsResponse, StatCardItem
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
<<<<<<< HEAD
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_students = db.query(Student).count()
    total_teaching = db.query(TeachingStaff).count()
    total_non_teaching = db.query(NonTeachingStaff).count()
    total_departments = db.query(Department).filter(Department.status == "Active").count()
    
    fee_records = db.query(FeeRecord).all()
    pending_total = 0.0
    for r in fee_records:
        cleaned = str(r.pending).replace("₹", "").replace(",", "").strip()
        try:
            pending_total += float(cleaned)
        except ValueError:
            pass

    pending_in_lakhs = (pending_total / 100000.0)

=======
def get_dashboard_stats(db: Database = Depends(get_db)):
    students_collection = mongo_collection("students", db)
    total_students = (
        students_collection.count_documents({})
        - students_collection.count_documents({"applicationStatus": "Draft"})
    )
    total_teaching = mongo_collection("teaching_staff", db).count_documents({})
    total_non_teaching = mongo_collection("non_teaching_staff", db).count_documents({})
    total_departments = mongo_collection("departments", db).count_documents({"status": "Active"})

    pending_total = 0.0
    for record in mongo_collection("fee_records", db).find({}, {"pending": 1}):
        cleaned = str(record.get("pending", 0)).replace("₹", "").replace(",", "").strip()
        try:
            pending_total += float(cleaned)
        except ValueError:
            continue

    pending_in_lakhs = pending_total / 100000.0
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    stats = [
        StatCardItem(
            label="Total Students",
            value=f"{total_students:,}",
            trend="+8.2%",
            trendLabel="from last month",
            tone="blue",
<<<<<<< HEAD
            trendTone="success"
=======
            trendTone="success",
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
        ),
        StatCardItem(
            label="Teaching Staff",
            value=f"{total_teaching:,}",
            trend="+3.4%",
            trendLabel="from last month",
            tone="green",
<<<<<<< HEAD
            trendTone="success"
=======
            trendTone="success",
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
        ),
        StatCardItem(
            label="Pending Fees",
            value=f"₹{pending_in_lakhs:.2f} L",
            trend="12.5%",
            trendLabel="from last month",
            tone="orange",
<<<<<<< HEAD
            trendTone="danger"
=======
            trendTone="danger",
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
        ),
        StatCardItem(
            label="Departments",
            value=str(total_departments or 5),
            trendLabel="Active departments",
            tone="purple",
<<<<<<< HEAD
            trendTone="success-plain"
        )
    ]

=======
            trendTone="success-plain",
        ),
    ]
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return DashboardStatsResponse(
        stats=stats,
        totalStudents=total_students,
        totalTeachingStaff=total_teaching,
        totalNonTeachingStaff=total_non_teaching,
        totalDepartments=total_departments or 5,
<<<<<<< HEAD
        pendingFeeTotal=pending_total
=======
        pendingFeeTotal=pending_total,
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    )


@router.get("/recent-activity", response_model=List[ActivityItem])
<<<<<<< HEAD
def get_recent_activity(db: Session = Depends(get_db)):
    # Pull latest notices and students as dynamic activity
    recent_notices = db.query(Notice).order_by(Notice.created_at.desc()).limit(2).all()
    recent_students = db.query(Student).order_by(Student.created_at.desc()).limit(2).all()

    activity = []

    if recent_students:
        for s in recent_students:
            activity.append(ActivityItem(
                title="New student registered",
                detail=f"{s.name} was added to {s.department} - {s.section}",
                time="10 minutes ago",
                tone="blue"
            ))

    activity.append(ActivityItem(
        title="Fee payment received",
        detail="₹25,000 received from student STU1024",
        time="30 minutes ago",
        tone="green"
    ))

    activity.append(ActivityItem(
        title="Attendance marked",
        detail="CSE - A attendance was submitted",
        time="1 hour ago",
        tone="orange"
    ))

    if recent_notices:
        for n in recent_notices:
            activity.append(ActivityItem(
                title="New notice published",
                detail=n.title,
                time="2 hours ago",
                tone="purple"
            ))

    activity.append(ActivityItem(
        title="Document verified",
        detail="Student document verification completed",
        time="3 hours ago",
        tone="blue"
    ))

=======
def get_recent_activity(db: Database = Depends(get_db)):
    recent_notices = list_documents(
        db, "notices", sort_by="created_at", descending=True, limit=2
    )
    recent_students = [
        student
        for student in list_documents(
            db,
            "students",
            filters={"applicationStatus": {"$ne": "Draft"}},
            sort_by="created_at",
            descending=True,
            limit=2,
        )
        if student.get("applicationStatus") != "Draft"
    ]

    activity = [
        ActivityItem(
            title="New student registered",
            detail=f"{student['name']} was added to {student['department']} - {student.get('section', 'A')}",
            time="10 minutes ago",
            tone="blue",
        )
        for student in recent_students
    ]
    activity.extend(
        [
            ActivityItem(
                title="Fee payment received",
                detail="₹25,000 received from student STU1024",
                time="30 minutes ago",
                tone="green",
            ),
            ActivityItem(
                title="Attendance marked",
                detail="CSE - A attendance was submitted",
                time="1 hour ago",
                tone="orange",
            ),
        ]
    )
    activity.extend(
        ActivityItem(
            title="New notice published",
            detail=notice["title"],
            time="2 hours ago",
            tone="purple",
        )
        for notice in recent_notices
    )
    activity.append(
        ActivityItem(
            title="Document verified",
            detail="Student document verification completed",
            time="3 hours ago",
            tone="blue",
        )
    )
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    return activity[:5]
