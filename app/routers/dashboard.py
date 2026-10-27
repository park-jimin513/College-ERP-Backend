from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.student import Student
from app.models.staff import TeachingStaff, NonTeachingStaff
from app.models.academic import Department
from app.models.fee import FeeRecord
from app.models.notice import Notice
from app.schemas.dashboard import DashboardStatsResponse, StatCardItem, ActivityItem

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
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

    stats = [
        StatCardItem(
            label="Total Students",
            value=f"{total_students:,}",
            trend="+8.2%",
            trendLabel="from last month",
            tone="blue",
            trendTone="success"
        ),
        StatCardItem(
            label="Teaching Staff",
            value=f"{total_teaching:,}",
            trend="+3.4%",
            trendLabel="from last month",
            tone="green",
            trendTone="success"
        ),
        StatCardItem(
            label="Pending Fees",
            value=f"₹{pending_in_lakhs:.2f} L",
            trend="12.5%",
            trendLabel="from last month",
            tone="orange",
            trendTone="danger"
        ),
        StatCardItem(
            label="Departments",
            value=str(total_departments or 5),
            trendLabel="Active departments",
            tone="purple",
            trendTone="success-plain"
        )
    ]

    return DashboardStatsResponse(
        stats=stats,
        totalStudents=total_students,
        totalTeachingStaff=total_teaching,
        totalNonTeachingStaff=total_non_teaching,
        totalDepartments=total_departments or 5,
        pendingFeeTotal=pending_total
    )


@router.get("/recent-activity", response_model=List[ActivityItem])
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

    return activity[:5]
