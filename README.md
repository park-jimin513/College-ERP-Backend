# 🎓 College ERP - Python (FastAPI) Backend

A robust, modular, high-performance REST API backend built with **FastAPI**, **SQLAlchemy ORM**, **Pydantic v2**, and **SQLite/PostgreSQL**.

---

## ⚡ Quick Start

### 1. Requirements
- Python 3.10+ (Tested on Python 3.13)
- pip package manager

### 2. Install Dependencies
Navigate to the `backend/` directory:
```bash
pip install -r requirements.txt
```

### 3. Configure Credentials
Copy `.env.example` to `.env` and set a long, random `SECRET_KEY`. The private `.env` file stores the JWT secret, database URL, and CORS settings. It is ignored by Git.

The default database is SQLite at `backend/college_erp.db`. You can replace `DATABASE_URL` in `.env` with a PostgreSQL connection string when needed.

### 4. Run the Server
```bash
python run.py
```
> The server will automatically initialize the database, seed initial demo records, and start listening on **`http://127.0.0.1:8000`**.

---

## 📖 Interactive API Documentation

Once the server is running, open:
- **Swagger UI (Interactive Playground)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔑 Default Login Credentials
- **Email**: `admin@college.edu`
- **Password**: `admin123`
- **Demo OTP**: Any 4-6 digit number (e.g. `1234`) or the OTP received from `/api/auth/send-otp`.

---

## 🗂️ Project Architecture

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py            # App settings, JWT, CORS & database configuration
│   │   ├── database.py          # SQLAlchemy engine, sessions & base model
│   │   └── security.py          # Password hashing (bcrypt) & JWT generation
│   ├── models/                  # SQLAlchemy ORM Models
│   │   ├── user.py              # User authentication & lockout tracking
│   │   ├── student.py           # Student personal, parent & academic info
│   │   ├── staff.py             # Teaching & Non-teaching staff models
│   │   ├── academic.py          # Departments, Courses, Academic Programs
│   │   ├── fee.py               # Fee payments & ledger records
│   │   ├── attendance.py        # Subject attendance percentages
│   │   ├── examination.py       # Exams and Published Results / Grades
│   │   ├── timetable.py         # Timetable schedules
│   │   ├── library.py           # Books catalog & issues
│   │   ├── hostel.py            # Hostel rooms & occupants
│   │   ├── transport.py         # Vehicles, routes & drivers
│   │   ├── document.py          # Document verification workflow
│   │   └── notice.py            # Notices & target audience announcements
│   ├── schemas/                 # Pydantic validation schemas (Request/Response)
│   ├── routers/                 # Modular API Route Controllers
│   │   ├── auth.py              # /api/auth (login, signup, OTP, password reset)
│   │   ├── dashboard.py         # /api/dashboard (stats & activity)
│   │   ├── students.py          # /api/students (CRUD, filters, search)
│   │   ├── teaching_staff.py    # /api/teaching-staff
│   │   ├── non_teaching_staff.py# /api/non-teaching-staff
│   │   ├── departments.py       # /api/departments
│   │   ├── courses.py           # /api/courses
│   │   ├── academics.py         # /api/academics/programs
│   │   ├── attendance.py        # /api/attendance
│   │   ├── examinations.py      # /api/examinations
│   │   ├── results.py           # /api/results
│   │   ├── timetable.py         # /api/timetable
│   │   ├── fees.py              # /api/fees
│   │   ├── documents.py         # /api/documents
│   │   ├── library.py           # /api/library
│   │   ├── hostel.py            # /api/hostel
│   │   ├── transport.py         # /api/transport
│   │   └── notices.py           # /api/notices
│   ├── seed.py                  # Seed script with all initial demo data
│   └── main.py                  # Central FastAPI application & CORS
├── requirements.txt
├── run.py                       # Server runner
└── README.md
```

---

## 🔌 API Endpoints Summary

| Module | Method & Endpoint | Description |
|---|---|---|
| **Health** | `GET /api/health` | Service health status |
| **Auth** | `POST /api/auth/login` | Secure email & password login |
| **Auth** | `POST /api/auth/signup` | Register new admin/user |
| **Auth** | `POST /api/auth/send-otp` | Request email OTP code |
| **Auth** | `POST /api/auth/reset-password` | Reset password with OTP |
| **Dashboard** | `GET /api/dashboard/stats` | Dynamic dashboard statistics cards |
| **Dashboard** | `GET /api/dashboard/recent-activity`| Real-time campus activities |
| **Students** | `GET /api/students` | List students with search & filters |
| **Students** | `POST /api/students` | Add new student |
| **Students** | `GET /api/students/{id}` | Get student profile details |
| **Students** | `PUT /api/students/{id}` | Update student record |
| **Students** | `DELETE /api/students/{id}` | Remove student |
| **Teaching Staff** | `GET /api/teaching-staff` | List faculty with department filter |
| **Teaching Staff** | `POST /api/teaching-staff` | Add new faculty member |
| **Non-Teaching** | `GET /api/non-teaching-staff` | List operational staff |
| **Departments** | `GET /api/departments` | List campus departments |
| **Courses** | `GET /api/courses` | Filter courses by branch, year, sem |
| **Academics** | `GET /api/academics/programs` | List degree programs (B.Tech, M.Tech) |
| **Attendance** | `GET /api/attendance` | Attendance records & shortages |
| **Examinations** | `GET /api/examinations` | Exam schedules & invigilators |
| **Results** | `GET /api/results` | Student SGPA, CGPA & Backlogs |
| **Timetable** | `GET /api/timetable` | Dynamic 6-day timetable matrix |
| **Fees** | `GET /api/fees` | Fee status, totals & pending balances |
| **Fees** | `POST /api/fees` | Record student payment / fee update |
| **Documents** | `GET /api/documents` | List uploaded verification files |
| **Documents** | `PATCH /api/documents/{id}/status` | Verify / Reject student document |
| **Library** | `GET /api/library` | Books catalog & availability status |
| **Hostel** | `GET /api/hostel` | Room allocations & occupancy |
| **Transport** | `GET /api/transport` | Vehicle routes & compliance dates |
| **Notices** | `GET /api/notices` | View published campus notices |
| **Notices** | `POST /api/notices` | Publish or schedule notice |

---

## 🔗 Connecting to the React Frontend

The backend has CORS enabled for all origins (`*`) by default, including `http://localhost:5173`.

You can consume any API endpoint using standard `fetch()` or `axios`:
```javascript
const response = await fetch('http://127.0.0.1:8000/api/students')
const students = await response.json()
```
A ready-to-use frontend API client is provided in `src/services/api.js`.
