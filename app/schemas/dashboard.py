from typing import List, Optional
from pydantic import BaseModel


class StatCardItem(BaseModel):
    label: str
    value: str
    trend: Optional[str] = None
    trendLabel: Optional[str] = None
    tone: str
    trendTone: str


class ActivityItem(BaseModel):
    title: str
    detail: str
    time: str
    tone: str


class DashboardStatsResponse(BaseModel):
    stats: List[StatCardItem]
    totalStudents: int
    totalTeachingStaff: int
    totalNonTeachingStaff: int
    totalDepartments: int
    pendingFeeTotal: float
