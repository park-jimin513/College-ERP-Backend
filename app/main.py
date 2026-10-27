<<<<<<< HEAD
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base

# Import all models to ensure metadata registration
import app.models

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)
=======
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.mongo import check_mongodb_connection, ensure_indexes


@asynccontextmanager
async def lifespan(_app: FastAPI):
    check_mongodb_connection()
    ensure_indexes()
    print(f"[MongoDB] Connected to database '{settings.DATABASE_NAME}'.")
    yield

>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Comprehensive, modular REST API backend for the College ERP platform.",
    docs_url="/docs",
    redoc_url="/redoc",
<<<<<<< HEAD
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Setup for React / Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
=======
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)


# CORS Setup for React / Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include all modular routers
from app.routers import (
    auth,
    dashboard,
    students,
    teaching_staff,
    non_teaching_staff,
    departments,
    courses,
    academics,
    attendance,
    examinations,
    results,
    timetable,
    fees,
    documents,
    library,
    hostel,
    transport,
    notices,
)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(students.router, prefix=settings.API_V1_STR)
app.include_router(teaching_staff.router, prefix=settings.API_V1_STR)
app.include_router(non_teaching_staff.router, prefix=settings.API_V1_STR)
app.include_router(departments.router, prefix=settings.API_V1_STR)
app.include_router(courses.router, prefix=settings.API_V1_STR)
app.include_router(academics.router, prefix=settings.API_V1_STR)
app.include_router(attendance.router, prefix=settings.API_V1_STR)
app.include_router(examinations.router, prefix=settings.API_V1_STR)
app.include_router(results.router, prefix=settings.API_V1_STR)
app.include_router(timetable.router, prefix=settings.API_V1_STR)
app.include_router(fees.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(library.router, prefix=settings.API_V1_STR)
app.include_router(hostel.router, prefix=settings.API_V1_STR)
app.include_router(transport.router, prefix=settings.API_V1_STR)
app.include_router(notices.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }


@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
