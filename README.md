# 🎓 College ERP - Python (FastAPI) Backend

A robust, modular REST API backend built with **FastAPI**, **PyMongo**, and **Pydantic v2**.

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
Copy `.env.example` to `.env`, configure `MONGODB_URI` and `DATABASE_NAME`,
set a long, random `SECRET_KEY`, and configure the Resend email API:

- `EMAIL_PROVIDER=resend`
- `EMAIL_API_KEY`: a Resend API key with permission to send email.
- `EMAIL_FROM`: a sender address on a domain verified in Resend, for example
  `College ERP <otp@mail.example.edu>`.

Add the sender domain to Resend and publish the DNS records Resend provides
before using the address. See Resend's [domain setup guide](https://resend.com/docs/dashboard/domains/introduction)
and [send-email API reference](https://resend.com/docs/api-reference/emails/send-email).
Do not use a real credential in `.env.example` or commit the private `.env` file.
The application reads credentials from environment variables (and the private
local `.env` file during development).

For local development only, the previous Gmail SMTP path remains available by
setting `EMAIL_PROVIDER=smtp`, `EMAIL_USER`, and `EMAIL_PASS` (a Gmail App
Password). Gmail SMTP is not the production default. The Resend integration
uses HTTPS and does not require outbound SMTP ports.

All application data, including users and OTP state, is stored directly in MongoDB. The backend fails to start if MongoDB is not configured or reachable.

New accounts must verify their email address before login. Login and password
reset also require an emailed OTP, which expires after 15 minutes. OTPs are
stored as keyed hashes, consumed atomically after successful verification, and
limited to five verification attempts. A recipient can request at most one code
per minute. Send-code responses do not reveal whether an account exists. If the
email provider is not configured or unavailable, the API returns a safe 503 and
invalidates the code.

Test the MongoDB connection independently before seeding or starting the API:

```bash
python check_mongodb.py
```

The diagnostic sends an authenticated MongoDB `ping` using the configured `.env`
settings. It never prints the URI or password and provides targeted guidance for
common DNS/SRV, TLS, authentication, and network failures. The client verifies
TLS certificates using the `certifi` CA bundle; TLS verification must remain
enabled.

If Atlas reports a TLS handshake or server-selection failure, verify that the
cluster is running, the database user's credentials and roles are valid, and
your current public IP is allowed under Atlas **Network Access**. Also check
that the network allows outbound TCP port `27017` without TLS inspection.
Successful DNS resolution or TCP reachability alone does not prove the Atlas
connection works; the diagnostic must report a successful ping.

If you have records in the old `college_erp.db` SQLite file, migrate them once before starting the new backend:

```bash
python migrate_sqlite_to_mongodb.py
```

The importer opens the legacy file read-only, adds records that are missing in MongoDB, and leaves existing MongoDB records unchanged. Keep the SQLite file as a backup until you confirm the imported data.

### 4. Run the Server
```bash
python run.py
```
> The server listens on **`http://localhost:8000`** by default. It reads `PORT` when set and binds to `0.0.0.0`.
> Startup checks the connection before creating indexes or inserting seed data. If duplicate
> user emails conflict under the case-insensitive unique index, resolve the reported
> (masked) conflicts in MongoDB and rerun initialization; no user data is deleted.

Demo data is not seeded automatically. To seed it intentionally, set
`SEED_DATABASE=true` and provide `SEED_ADMIN_PASSWORD` (and optionally
`SEED_ADMIN_EMAIL`) in the environment before running `python run.py`. Never use
a shared or predictable password for the initial administrator.

## 🚀 Deploy on Render

Create a **Web Service** from the repository and use these settings:

| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python run.py` |

Add these environment variables in the Render service dashboard:

- `MONGODB_URI`: MongoDB Atlas connection URI. Restrict its database user and
  network access to the production service as appropriate.
- `SECRET_KEY`: a unique, long random signing key. Do not reuse a development key.
- `DATABASE_NAME`: production database name (optional; defaults to `college_erp`).
- `CORS_ORIGINS`: JSON array of allowed frontend origins, for example
  `["https://your-frontend.onrender.com"]`.
- `EMAIL_PROVIDER=resend`: use the HTTPS transactional email API. Render Free
  services may not use outbound SMTP ports 25, 465, or 587, so do not configure
  Gmail SMTP as the production delivery path ([Render Free instance
  limitations](https://render.com/docs/free)).
- `EMAIL_API_KEY`: the Resend API key. Store it only in the Render environment,
  never in source control or frontend `VITE_` variables.
- `EMAIL_FROM`: a sender identity on a domain verified in Resend. Complete the
  domain's DNS verification before expecting production delivery.
- `EMAIL_USER` and `EMAIL_PASS`: retained only for deployments intentionally
  using `EMAIL_PROVIDER=smtp`; do not set `EMAIL_PROVIDER=smtp` on a Render Free
  service.

Render supplies `PORT`; `run.py` uses it automatically and binds to
`0.0.0.0`. Do not enable `SEED_DATABASE` for normal production launches. If
initial records are needed, seed deliberately with a unique `SEED_ADMIN_PASSWORD`
set through the Render environment, then remove it after initialization.

After configuring the service, redeploy it and check Render logs for either the
MongoDB startup confirmation or an explicit MongoDB startup error. For an email
failure, logs identify missing environment-variable names or the provider and
HTTP status only; they never include OTPs, email-provider response bodies, API
keys, or database credentials.

---

## 📖 Interactive API Documentation

Once the server is running, open:
- **Swagger UI (Interactive Playground)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

---

## 🗂️ Project Architecture

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py            # App settings, JWT, CORS & database configuration
│   │   ├── database.py          # MongoDB request dependency
│   │   └── security.py          # Password hashing (bcrypt) & JWT generation
│   ├── seed_data.py             # Initial MongoDB demo records
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
│   ├── seed.py                  # Idempotent MongoDB seeder
│   └── main.py                  # Central FastAPI application & CORS
├── migrate_sqlite_to_mongodb.py # One-time, non-destructive legacy data importer
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
| **Students** | `POST /api/students/{id}/documents` | Upload a JPG, PNG, or PDF student document (up to 5 MB) |
| **Students** | `GET /api/students/{id}/documents/{document_type}` | Download a stored student document |
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

Student admission records persist personal, address, parent/guardian, admission,
academic-mapping, fee, and document metadata fields in MongoDB. Uploaded file
contents are stored in the `student_documents` GridFS bucket; supported document
types are `photo`, `idProof`, `tenth`, `twelfth`, `transferCert`,
`migrationCert`, `communityCert`, `incomeCert`, and `allotmentLetter`.
Incomplete admission forms can be persisted with `applicationStatus: "Draft"`
without completing required admission fields. Drafts remain in the students
collection and can be updated later; submitting changes the application status
and requires the full admission details and declaration acknowledgements.
Dashboard student counts and recent-student activity exclude draft records.

---

## 🔗 Connecting to the React Frontend

The backend allows the local Vite origins `http://localhost:5173`,
`http://127.0.0.1:5173`, `http://localhost:5174`, and `http://127.0.0.1:5174`
by default. Configure `CORS_ORIGINS` if the frontend uses a different origin,
then restart the backend.

You can consume any API endpoint using standard `fetch()` or `axios`:
```javascript
const response = await fetch('http://localhost:8000/api/students')
const students = await response.json()
```
A ready-to-use frontend API client is provided in `src/services/api.js`.
