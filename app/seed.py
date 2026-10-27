from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.student import Student
from app.models.staff import TeachingStaff, NonTeachingStaff
from app.models.academic import Department, Course, AcademicProgram
from app.models.fee import FeeRecord
from app.models.attendance import AttendanceRecord
from app.models.examination import Examination, ExamResult
from app.models.library import Book
from app.models.hostel import HostelRoom
from app.models.transport import TransportVehicle
from app.models.document import Document
from app.models.notice import Notice


def seed_database():
    print("[+] Initializing and seeding College ERP Database...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Admin User
    admin = db.query(User).filter(User.email == "admin@college.edu").first()
    if not admin:
        admin = User(
            name="Administrator",
            email="admin@college.edu",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        print("  * Created default admin: admin@college.edu / admin123")

    # 2. Students
    if db.query(Student).count() == 0:
        students_data = [
            {
                "id": "STU1024",
                "name": "Rahul Sharma",
                "department": "CSE",
                "batch": "2023 - 2027",
                "year": "2nd Year",
                "semester": "Semester 3",
                "section": "A",
                "gender": "Male",
                "admissionType": "Regular",
                "attendance": 92,
                "feeStatus": "Paid",
                "status": "Active",
                "phone": "+91 98450 12345",
                "email": "rahul.sharma@college.edu",
                "dob": "14 Mar 2006",
                "bloodGroup": "O+",
                "address": "Banjara Hills, Hyderabad, Telangana",
                "father": "Suresh Sharma",
                "mother": "Anita Sharma",
                "guardianPhone": "+91 98450 54321",
                "totalFee": "₹1,20,000",
                "paidFee": "₹1,20,000",
                "pendingFee": "₹0",
                "cgpa": "8.6",
            },
            {
                "id": "STU1025",
                "name": "Ananya Reddy",
                "department": "CSE-AI",
                "batch": "2023 - 2027",
                "year": "2nd Year",
                "semester": "Semester 3",
                "section": "A",
                "gender": "Female",
                "admissionType": "Regular",
                "attendance": 88,
                "feeStatus": "Pending",
                "status": "Active",
                "phone": "+91 91234 56780",
                "email": "ananya.reddy@college.edu",
                "dob": "02 Jul 2006",
                "bloodGroup": "A+",
                "address": "Madhapur, Hyderabad, Telangana",
                "father": "Krishna Reddy",
                "mother": "Lakshmi Reddy",
                "guardianPhone": "+91 91234 09876",
                "totalFee": "₹1,35,000",
                "paidFee": "₹90,000",
                "pendingFee": "₹45,000",
                "cgpa": "9.1",
            },
            {
                "id": "STU1026",
                "name": "Mohammed Faizan",
                "department": "ECE",
                "batch": "2022 - 2026",
                "year": "3rd Year",
                "semester": "Semester 5",
                "section": "B",
                "gender": "Male",
                "admissionType": "Lateral Entry",
                "attendance": 76,
                "feeStatus": "Overdue",
                "status": "Active",
                "phone": "+91 90003 11223",
                "email": "faizan.m@college.edu",
                "dob": "19 Nov 2005",
                "bloodGroup": "B+",
                "address": "Tolichowki, Hyderabad, Telangana",
                "father": "Abdul Rahman",
                "mother": "Sameena Begum",
                "guardianPhone": "+91 90003 33445",
                "totalFee": "₹1,10,000",
                "paidFee": "₹55,000",
                "pendingFee": "₹55,000",
                "cgpa": "7.4",
            },
            {
                "id": "STU1027",
                "name": "Priya Nair",
                "department": "Civil",
                "batch": "2024 - 2028",
                "year": "1st Year",
                "semester": "Semester 1",
                "section": "A",
                "gender": "Female",
                "admissionType": "Regular",
                "attendance": 95,
                "feeStatus": "Paid",
                "status": "Active",
                "phone": "+91 88990 22334",
                "email": "priya.nair@college.edu",
                "dob": "27 Jan 2007",
                "bloodGroup": "AB+",
                "address": "Kukatpally, Hyderabad, Telangana",
                "father": "Ramesh Nair",
                "mother": "Sheela Nair",
                "guardianPhone": "+91 88990 44556",
                "totalFee": "₹95,000",
                "paidFee": "₹95,000",
                "pendingFee": "₹0",
                "cgpa": "9.4",
            },
            {
                "id": "STU1028",
                "name": "Arjun Verma",
                "department": "Mechanical",
                "batch": "2022 - 2026",
                "year": "3rd Year",
                "semester": "Semester 5",
                "section": "A",
                "gender": "Male",
                "admissionType": "Regular",
                "attendance": 81,
                "feeStatus": "Pending",
                "status": "Active",
                "phone": "+91 99887 65432",
                "email": "arjun.verma@college.edu",
                "dob": "05 Sep 2005",
                "bloodGroup": "O-",
                "address": "Secunderabad, Telangana",
                "father": "Vinod Verma",
                "mother": "Kavita Verma",
                "guardianPhone": "+91 99887 12300",
                "totalFee": "₹1,05,000",
                "paidFee": "₹70,000",
                "pendingFee": "₹35,000",
                "cgpa": "7.9",
            },
            {
                "id": "STU1029",
                "name": "Sneha Iyer",
                "department": "CSE",
                "batch": "2023 - 2027",
                "year": "2nd Year",
                "semester": "Semester 3",
                "section": "B",
                "gender": "Female",
                "admissionType": "Regular",
                "attendance": 90,
                "feeStatus": "Paid",
                "status": "Suspended",
                "phone": "+91 97865 43210",
                "email": "sneha.iyer@college.edu",
                "dob": "11 Apr 2006",
                "bloodGroup": "A-",
                "address": "Gachibowli, Hyderabad, Telangana",
                "father": "Ganesh Iyer",
                "mother": "Radha Iyer",
                "guardianPhone": "+91 97865 09988",
                "totalFee": "₹1,20,000",
                "paidFee": "₹1,20,000",
                "pendingFee": "₹0",
                "cgpa": "8.8",
            },
            {
                "id": "STU1030",
                "name": "Karthik Rao",
                "department": "CSE-AI",
                "batch": "2024 - 2028",
                "year": "1st Year",
                "semester": "Semester 1",
                "section": "B",
                "gender": "Male",
                "admissionType": "Regular",
                "attendance": 84,
                "feeStatus": "Paid",
                "status": "Active",
                "phone": "+91 96654 78901",
                "email": "karthik.rao@college.edu",
                "dob": "30 Dec 2007",
                "bloodGroup": "B-",
                "address": "Miyapur, Hyderabad, Telangana",
                "father": "Srinivas Rao",
                "mother": "Padma Rao",
                "guardianPhone": "+91 96654 11223",
                "totalFee": "₹1,35,000",
                "paidFee": "₹1,35,000",
                "pendingFee": "₹0",
                "cgpa": "8.2",
            },
            {
                "id": "STU1031",
                "name": "Divya Menon",
                "department": "ECE",
                "batch": "2023 - 2027",
                "year": "2nd Year",
                "semester": "Semester 3",
                "section": "A",
                "gender": "Female",
                "admissionType": "Regular",
                "attendance": 79,
                "feeStatus": "Overdue",
                "status": "Active",
                "phone": "+91 95432 10987",
                "email": "divya.menon@college.edu",
                "dob": "23 Jun 2006",
                "bloodGroup": "O+",
                "address": "Ameerpet, Hyderabad, Telangana",
                "father": "Ravi Menon",
                "mother": "Geetha Menon",
                "guardianPhone": "+91 95432 65478",
                "totalFee": "₹1,15,000",
                "paidFee": "₹50,000",
                "pendingFee": "₹65,000",
                "cgpa": "7.6",
            },
            {
                "id": "STU1032",
                "name": "Vikram Singh",
                "department": "Civil",
                "batch": "2022 - 2026",
                "year": "3rd Year",
                "semester": "Semester 5",
                "section": "B",
                "gender": "Male",
                "admissionType": "Regular",
                "attendance": 87,
                "feeStatus": "Paid",
                "status": "Active",
                "phone": "+91 94321 09876",
                "email": "vikram.singh@college.edu",
                "dob": "08 Feb 2005",
                "bloodGroup": "AB-",
                "address": "Begumpet, Hyderabad, Telangana",
                "father": "Harpreet Singh",
                "mother": "Jasleen Kaur",
                "guardianPhone": "+91 94321 55667",
                "totalFee": "₹1,05,000",
                "paidFee": "₹1,05,000",
                "pendingFee": "₹0",
                "cgpa": "8.0",
            },
            {
                "id": "STU1033",
                "name": "Fathima Zohra",
                "department": "CSE",
                "batch": "2024 - 2028",
                "year": "1st Year",
                "semester": "Semester 1",
                "section": "A",
                "gender": "Female",
                "admissionType": "Lateral Entry",
                "attendance": 93,
                "feeStatus": "Pending",
                "status": "Active",
                "phone": "+91 93210 98765",
                "email": "fathima.z@college.edu",
                "dob": "15 Aug 2007",
                "bloodGroup": "A+",
                "address": "Mehdipatnam, Hyderabad, Telangana",
                "father": "Ibrahim Ali",
                "mother": "Nargis Begum",
                "guardianPhone": "+91 93210 44332",
                "totalFee": "₹1,20,000",
                "paidFee": "₹80,000",
                "pendingFee": "₹40,000",
                "cgpa": "9.0",
            },
            {
                "id": "STU1034",
                "name": "Aditya Kulkarni",
                "department": "Mechanical",
                "batch": "2023 - 2027",
                "year": "2nd Year",
                "semester": "Semester 3",
                "section": "A",
                "gender": "Male",
                "admissionType": "Regular",
                "attendance": 71,
                "feeStatus": "Overdue",
                "status": "Inactive",
                "phone": "+91 92109 87654",
                "email": "aditya.k@college.edu",
                "dob": "01 May 2006",
                "bloodGroup": "B+",
                "address": "LB Nagar, Hyderabad, Telangana",
                "father": "Prakash Kulkarni",
                "mother": "Sunita Kulkarni",
                "guardianPhone": "+91 92109 22110",
                "totalFee": "₹1,05,000",
                "paidFee": "₹40,000",
                "pendingFee": "₹65,000",
                "cgpa": "6.9",
            },
            {
                "id": "STU1035",
                "name": "Meera Pillai",
                "department": "CSE-AI",
                "batch": "2022 - 2026",
                "year": "3rd Year",
                "semester": "Semester 5",
                "section": "A",
                "gender": "Female",
                "admissionType": "Regular",
                "attendance": 96,
                "feeStatus": "Paid",
                "status": "Active",
                "phone": "+91 91098 76543",
                "email": "meera.pillai@college.edu",
                "dob": "20 Oct 2005",
                "bloodGroup": "O+",
                "address": "Jubilee Hills, Hyderabad, Telangana",
                "father": "Suresh Pillai",
                "mother": "Latha Pillai",
                "guardianPhone": "+91 91098 33221",
                "totalFee": "₹1,35,000",
                "paidFee": "₹1,35,000",
                "pendingFee": "₹0",
                "cgpa": "9.5",
            },
        ]
        for s in students_data:
            db.add(Student(**s))
        print(f"  * Seeded {len(students_data)} Students")

    # 3. Teaching Staff
    if db.query(TeachingStaff).count() == 0:
        teaching_staff_data = [
            {
                "id": "EMP2001",
                "name": "Dr. Kavitha Kumar",
                "department": "CSE",
                "designation": "HOD",
                "employmentType": "Permanent",
                "status": "Active",
                "qualification": "Ph.D in Computer Science",
                "specialization": "Data Structures & Algorithms",
                "experience": "14 years",
                "joiningDate": "02 Jun 2012",
                "subjects": "Data Structures, Design & Analysis of Algorithms",
                "classes": "CSE - 2nd Year A, B",
                "workload": "16 hrs / week",
                "phone": "+91 90001 22334",
                "email": "kavitha.kumar@college.edu",
            },
            {
                "id": "EMP2002",
                "name": "Prof. Suresh Iyer",
                "department": "ECE",
                "designation": "Professor",
                "employmentType": "Permanent",
                "status": "Active",
                "qualification": "Ph.D in Electronics",
                "specialization": "VLSI Design",
                "experience": "18 years",
                "joiningDate": "11 Jul 2008",
                "subjects": "VLSI Design, Digital Electronics",
                "classes": "ECE - 3rd Year A",
                "workload": "14 hrs / week",
                "phone": "+91 90002 33445",
                "email": "suresh.iyer@college.edu",
            },
            {
                "id": "EMP2003",
                "name": "Dr. Ramesh Naidu",
                "department": "Mechanical",
                "designation": "Associate Professor",
                "employmentType": "Permanent",
                "status": "On Leave",
                "qualification": "Ph.D in Thermal Engineering",
                "specialization": "Thermodynamics",
                "experience": "11 years",
                "joiningDate": "19 Jan 2015",
                "subjects": "Thermodynamics, Fluid Mechanics",
                "classes": "Mechanical - 3rd Year A, B",
                "workload": "12 hrs / week",
                "phone": "+91 90003 44556",
                "email": "ramesh.naidu@college.edu",
            },
            {
                "id": "EMP2004",
                "name": "Ms. Priyanka Das",
                "department": "CSE-AI",
                "designation": "Assistant Professor",
                "employmentType": "Permanent",
                "status": "Active",
                "qualification": "M.Tech in AI & ML",
                "specialization": "Machine Learning",
                "experience": "5 years",
                "joiningDate": "03 Aug 2021",
                "subjects": "Machine Learning, Neural Networks",
                "classes": "CSE-AI - 1st Year A",
                "workload": "18 hrs / week",
                "phone": "+91 90004 55667",
                "email": "priyanka.das@college.edu",
            },
            {
                "id": "EMP2005",
                "name": "Mr. Anil Kapoor",
                "department": "Civil",
                "designation": "Assistant Professor",
                "employmentType": "Contract",
                "status": "Active",
                "qualification": "M.Tech in Structural Engineering",
                "specialization": "Structural Analysis",
                "experience": "4 years",
                "joiningDate": "14 Dec 2021",
                "subjects": "Structural Analysis, Surveying",
                "classes": "Civil - 3rd Year A",
                "workload": "16 hrs / week",
                "phone": "+91 90005 66778",
                "email": "anil.kapoor@college.edu",
            },
            {
                "id": "EMP2006",
                "name": "Dr. Neha Joshi",
                "department": "ECE",
                "designation": "Professor",
                "employmentType": "Permanent",
                "status": "Active",
                "qualification": "Ph.D in Communication Systems",
                "specialization": "Signal Processing",
                "experience": "16 years",
                "joiningDate": "25 Apr 2010",
                "subjects": "Signal Processing, Communication Systems",
                "classes": "ECE - 2nd Year A, B",
                "workload": "14 hrs / week",
                "phone": "+91 90006 77889",
                "email": "neha.joshi@college.edu",
            },
            {
                "id": "EMP2007",
                "name": "Mr. Rajiv Menon",
                "department": "CSE",
                "designation": "Assistant Professor",
                "employmentType": "Visiting",
                "status": "Inactive",
                "qualification": "M.Tech in Computer Science",
                "specialization": "Database Systems",
                "experience": "7 years",
                "joiningDate": "09 Sep 2019",
                "subjects": "Database Management Systems",
                "classes": "CSE - 2nd Year C",
                "workload": "8 hrs / week",
                "phone": "+91 90007 88990",
                "email": "rajiv.menon@college.edu",
            },
        ]
        for t in teaching_staff_data:
            db.add(TeachingStaff(**t))
        print(f"  * Seeded {len(teaching_staff_data)} Teaching Staff")

    # 4. Non-Teaching Staff
    if db.query(NonTeachingStaff).count() == 0:
        non_teaching_data = [
            {
                "id": "NTS3001",
                "name": "Ramu Yadav",
                "area": "Security",
                "designation": "Security Guard",
                "employmentType": "Permanent",
                "status": "Active",
                "joiningDate": "10 Mar 2016",
                "shift": "Day Shift (8 AM – 4 PM)",
                "phone": "+91 88001 22334",
                "email": "ramu.yadav@college.edu",
                "address": "Uppal, Hyderabad, Telangana",
            },
            {
                "id": "NTS3002",
                "name": "Lakshmi Devi",
                "area": "Administration",
                "designation": "Office Assistant",
                "employmentType": "Permanent",
                "status": "Active",
                "joiningDate": "05 Jun 2014",
                "shift": "Day Shift (9 AM – 5 PM)",
                "phone": "+91 88002 33445",
                "email": "lakshmi.devi@college.edu",
                "address": "Dilsukhnagar, Hyderabad, Telangana",
            },
            {
                "id": "NTS3003",
                "name": "Mahesh Chandra",
                "area": "Transport",
                "designation": "Driver",
                "employmentType": "Contract",
                "status": "Active",
                "joiningDate": "21 Nov 2019",
                "shift": "Morning & Evening Trips",
                "phone": "+91 88003 44556",
                "email": "mahesh.c@college.edu",
                "address": "LB Nagar, Hyderabad, Telangana",
            },
            {
                "id": "NTS3004",
                "name": "Sunita Rani",
                "area": "Library",
                "designation": "Lab Assistant",
                "employmentType": "Permanent",
                "status": "On Leave",
                "joiningDate": "02 Feb 2018",
                "shift": "Day Shift (9 AM – 5 PM)",
                "phone": "+91 88004 55667",
                "email": "sunita.rani@college.edu",
                "address": "Malakpet, Hyderabad, Telangana",
            },
            {
                "id": "NTS3005",
                "name": "Ganesh Prasad",
                "area": "Maintenance",
                "designation": "Technician",
                "employmentType": "Permanent",
                "status": "Active",
                "joiningDate": "17 Aug 2017",
                "shift": "Day Shift (8 AM – 4 PM)",
                "phone": "+91 88005 66778",
                "email": "ganesh.prasad@college.edu",
                "address": "Nacharam, Hyderabad, Telangana",
            },
            {
                "id": "NTS3006",
                "name": "Anjali Verma",
                "area": "Administration",
                "designation": "Accountant",
                "employmentType": "Permanent",
                "status": "Active",
                "joiningDate": "09 Jan 2020",
                "shift": "Day Shift (9 AM – 5 PM)",
                "phone": "+91 88006 77889",
                "email": "anjali.verma@college.edu",
                "address": "Kothapet, Hyderabad, Telangana",
            },
        ]
        for n in non_teaching_data:
            db.add(NonTeachingStaff(**n))
        print(f"  * Seeded {len(non_teaching_data)} Non-Teaching Staff")

    # 5. Departments
    if db.query(Department).count() == 0:
        departments_data = [
            {
                "id": "DEP-CSE",
                "name": "Computer Science & Engineering",
                "code": "CSE",
                "hod": "Dr. Kavitha Kumar",
                "status": "Active",
                "faculty": 42,
                "students": 1240,
                "programs": "B.Tech, M.Tech",
                "established": "1998",
                "phone": "+91 40 2345 6001",
                "email": "cse@collegeinstitute.edu",
            },
            {
                "id": "DEP-CSEAI",
                "name": "Computer Science & Engineering (AI)",
                "code": "CSE-AI",
                "hod": "Dr. Vishnu Prasad",
                "status": "Active",
                "faculty": 24,
                "students": 680,
                "programs": "B.Tech",
                "established": "2020",
                "phone": "+91 40 2345 6002",
                "email": "cse-ai@collegeinstitute.edu",
            },
            {
                "id": "DEP-ECE",
                "name": "Electronics & Communication Engineering",
                "code": "ECE",
                "hod": "Dr. Neha Joshi",
                "status": "Active",
                "faculty": 30,
                "students": 760,
                "programs": "B.Tech, M.Tech",
                "established": "1995",
                "phone": "+91 40 2345 6003",
                "email": "ece@collegeinstitute.edu",
            },
            {
                "id": "DEP-CIVIL",
                "name": "Civil Engineering",
                "code": "Civil",
                "hod": "Dr. Ramesh Naidu",
                "status": "Active",
                "faculty": 22,
                "students": 520,
                "programs": "B.Tech",
                "established": "1992",
                "phone": "+91 40 2345 6004",
                "email": "civil@collegeinstitute.edu",
            },
            {
                "id": "DEP-MECH",
                "name": "Mechanical Engineering",
                "code": "Mechanical",
                "hod": "Dr. Suresh Iyer",
                "status": "Active",
                "faculty": 26,
                "students": 480,
                "programs": "B.Tech, M.Tech",
                "established": "1990",
                "phone": "+91 40 2345 6005",
                "email": "mech@collegeinstitute.edu",
            },
        ]
        for d in departments_data:
            db.add(Department(**d))
        print(f"  * Seeded {len(departments_data)} Departments")

    # 6. Academic Programs
    if db.query(AcademicProgram).count() == 0:
        programs_data = [
            {
                "id": "PRG-BTCSE",
                "name": "B.Tech Computer Science & Engineering",
                "department": "CSE",
                "level": "Undergraduate",
                "duration": "4 Years",
                "regulation": "R-2023",
                "status": "Active",
                "intake": 180,
                "currentStudents": 720,
                "semesters": 8,
            },
            {
                "id": "PRG-BTCSEAI",
                "name": "B.Tech CSE (Artificial Intelligence)",
                "department": "CSE-AI",
                "level": "Undergraduate",
                "duration": "4 Years",
                "regulation": "R-2023",
                "status": "Active",
                "intake": 120,
                "currentStudents": 480,
                "semesters": 8,
            },
            {
                "id": "PRG-BTECE",
                "name": "B.Tech Electronics & Communication",
                "department": "ECE",
                "level": "Undergraduate",
                "duration": "4 Years",
                "regulation": "R-2022",
                "status": "Active",
                "intake": 120,
                "currentStudents": 460,
                "semesters": 8,
            },
        ]
        for p in programs_data:
            db.add(AcademicProgram(**p))
        print(f"  * Seeded {len(programs_data)} Academic Programs")

    # 7. Courses
    if db.query(Course).count() == 0:
        courses_data = [
            {"id": "CS101", "name": "Programming for Problem Solving", "department": "CSE", "year": "1st Year", "semester": "1-1", "type": "Core", "credits": 4, "hours": "3 Theory + 2 Lab", "faculty": "Dr. Kavitha Kumar", "status": "Active"},
            {"id": "CS102", "name": "Engineering Mathematics - I", "department": "CSE", "year": "1st Year", "semester": "1-1", "type": "Core", "credits": 4, "hours": "4 Theory", "faculty": "Dr. Rajesh Kumar", "status": "Active"},
            {"id": "CS201", "name": "Data Structures & Algorithms", "department": "CSE", "year": "2nd Year", "semester": "2-1", "type": "Core", "credits": 4, "hours": "3 Theory + 2 Lab", "faculty": "Dr. Kavitha Kumar", "status": "Active"},
            {"id": "CS202", "name": "Database Management Systems", "department": "CSE", "year": "2nd Year", "semester": "2-1", "type": "Core", "credits": 3, "hours": "3 Theory", "faculty": "Mr. Rajiv Menon", "status": "Active"},
            {"id": "AI201", "name": "Machine Learning Fundamentals", "department": "CSE-AI", "year": "2nd Year", "semester": "2-1", "type": "Core", "credits": 4, "hours": "3 Theory + 2 Lab", "faculty": "Ms. Priyanka Das", "status": "Active"},
            {"id": "EC201", "name": "Digital Electronics", "department": "ECE", "year": "2nd Year", "semester": "2-1", "type": "Core", "credits": 3, "hours": "3 Theory", "faculty": "Prof. Suresh Iyer", "status": "Active"},
            {"id": "ME201", "name": "Thermodynamics", "department": "Mechanical", "year": "2nd Year", "semester": "2-1", "type": "Core", "credits": 4, "hours": "3 Theory", "faculty": "Dr. Ramesh Naidu", "status": "Active"},
        ]
        for c in courses_data:
            db.add(Course(**c))
        print(f"  * Seeded {len(courses_data)} Courses")

    # 8. Fees
    if db.query(FeeRecord).count() == 0:
        fee_records_data = [
            {"id": "STU1024", "name": "Rahul Sharma", "department": "CSE", "feeType": "Tuition", "totalFee": "₹1,20,000", "paid": "₹1,20,000", "pending": "₹0", "dueDate": "10 Jul 2026", "status": "Paid"},
            {"id": "STU1025", "name": "Ananya Reddy", "department": "CSE-AI", "feeType": "Tuition", "totalFee": "₹1,35,000", "paid": "₹90,000", "pending": "₹45,000", "dueDate": "30 Aug 2026", "status": "Partial"},
            {"id": "STU1026", "name": "Mohammed Faizan", "department": "ECE", "feeType": "Tuition", "totalFee": "₹1,10,000", "paid": "₹55,000", "pending": "₹55,000", "dueDate": "15 Jul 2026", "status": "Overdue"},
            {"id": "STU1028", "name": "Arjun Verma", "department": "Mechanical", "feeType": "Hostel", "totalFee": "₹65,000", "paid": "₹30,000", "pending": "₹35,000", "dueDate": "20 Aug 2026", "status": "Partial"},
            {"id": "STU1031", "name": "Divya Menon", "department": "ECE", "feeType": "Tuition", "totalFee": "₹1,15,000", "paid": "₹50,000", "pending": "₹65,000", "dueDate": "05 Jul 2026", "status": "Overdue"},
            {"id": "STU1033", "name": "Fathima Zohra", "department": "CSE", "feeType": "Tuition", "totalFee": "₹1,20,000", "paid": "₹80,000", "pending": "₹40,000", "dueDate": "25 Aug 2026", "status": "Partial"},
            {"id": "STU1034", "name": "Aditya Kulkarni", "department": "Mechanical", "feeType": "Transport", "totalFee": "₹18,000", "paid": "₹0", "pending": "₹18,000", "dueDate": "01 Jun 2026", "status": "Overdue"},
            {"id": "STU1035", "name": "Meera Pillai", "department": "CSE-AI", "feeType": "Tuition", "totalFee": "₹1,35,000", "paid": "₹1,35,000", "pending": "₹0", "dueDate": "10 Jul 2026", "status": "Paid"},
        ]
        for f in fee_records_data:
            db.add(FeeRecord(**f))
        print(f"  * Seeded {len(fee_records_data)} Fee Records")

    # 9. Attendance
    if db.query(AttendanceRecord).count() == 0:
        att_data = [
            {"id": "ATT-STU1024", "studentId": "STU1024", "name": "Rahul Sharma", "department": "CSE", "section": "A", "subject": "Data Structures", "conducted": 60, "attended": 55, "attendance": 92, "status": "Good"},
            {"id": "ATT-STU1025", "studentId": "STU1025", "name": "Ananya Reddy", "department": "CSE-AI", "section": "A", "subject": "Machine Learning", "conducted": 58, "attended": 51, "attendance": 88, "status": "Good"},
            {"id": "ATT-STU1026", "studentId": "STU1026", "name": "Mohammed Faizan", "department": "ECE", "section": "B", "subject": "Digital Electronics", "conducted": 62, "attended": 47, "attendance": 76, "status": "Warning"},
            {"id": "ATT-STU1027", "studentId": "STU1027", "name": "Priya Nair", "department": "Civil", "section": "A", "subject": "Surveying", "conducted": 55, "attended": 52, "attendance": 95, "status": "Good"},
            {"id": "ATT-STU1028", "studentId": "STU1028", "name": "Arjun Verma", "department": "Mechanical", "section": "A", "subject": "Thermodynamics", "conducted": 60, "attended": 49, "attendance": 82, "status": "Warning"},
        ]
        for a in att_data:
            db.add(AttendanceRecord(**a))
        print(f"  * Seeded {len(att_data)} Attendance Records")

    # 10. Examinations
    if db.query(Examination).count() == 0:
        exams_data = [
            {"id": "EXM-901", "name": "Internal Assessment I", "department": "CSE", "semester": "Semester 3", "type": "Internal", "startDate": "18 Aug 2026", "endDate": "22 Aug 2026", "status": "Completed", "subjects": "Data Structures, DBMS, OS", "rooms": "Block A - 101, 102", "invigilators": "Dr. Kavitha Kumar, Mr. Rajiv Menon"},
            {"id": "EXM-902", "name": "Semester End Examinations", "department": "CSE", "semester": "Semester 3", "type": "Semester End", "startDate": "01 Dec 2026", "endDate": "15 Dec 2026", "status": "Scheduled", "subjects": "All Semester 3 Subjects", "rooms": "Main Block - Exam Hall 1, 2", "invigilators": "To be assigned"},
            {"id": "EXM-903", "name": "Internal Assessment II", "department": "ECE", "semester": "Semester 5", "type": "Internal", "startDate": "25 Aug 2026", "endDate": "28 Aug 2026", "status": "Ongoing", "subjects": "Signal Processing, VLSI Design", "rooms": "Block B - 201", "invigilators": "Dr. Neha Joshi, Prof. Suresh Iyer"},
        ]
        for ex in exams_data:
            db.add(Examination(**ex))
        print(f"  * Seeded {len(exams_data)} Examinations")

    # 11. Results
    if db.query(ExamResult).count() == 0:
        results_data = [
            {"id": "STU1024", "name": "Rahul Sharma", "department": "CSE", "semester": "Semester 3", "sgpa": "8.7", "cgpa": "8.6", "backlogs": 0, "result": "Pass"},
            {"id": "STU1025", "name": "Ananya Reddy", "department": "CSE-AI", "semester": "Semester 3", "sgpa": "9.2", "cgpa": "9.1", "backlogs": 0, "result": "Pass"},
            {"id": "STU1026", "name": "Mohammed Faizan", "department": "ECE", "semester": "Semester 5", "sgpa": "6.8", "cgpa": "7.4", "backlogs": 1, "result": "Backlog"},
            {"id": "STU1027", "name": "Priya Nair", "department": "Civil", "semester": "Semester 1", "sgpa": "9.4", "cgpa": "9.4", "backlogs": 0, "result": "Pass"},
        ]
        for r in results_data:
            db.add(ExamResult(**r))
        print(f"  * Seeded {len(results_data)} Results")

    # 12. Library Books
    if db.query(Book).count() == 0:
        books_data = [
            {"id": "LIB-1001", "title": "Introduction to Algorithms", "author": "Cormen, Leiserson, Rivest", "category": "Computer Science", "copies": 6, "available": 4, "issuedTo": "—", "dueDate": "—", "status": "Available"},
            {"id": "LIB-1002", "title": "Digital Design", "author": "M. Morris Mano", "category": "Electronics", "copies": 4, "available": 0, "issuedTo": "Mohammed Faizan", "dueDate": "20 Aug 2026", "status": "Issued"},
            {"id": "LIB-1003", "title": "Fluid Mechanics and Hydraulics", "author": "R.K. Bansal", "category": "Mechanical", "copies": 3, "available": 1, "issuedTo": "Arjun Verma", "dueDate": "02 Aug 2026", "status": "Overdue"},
            {"id": "LIB-1004", "title": "Deep Learning", "author": "Ian Goodfellow", "category": "Computer Science", "copies": 3, "available": 0, "issuedTo": "Ananya Reddy", "dueDate": "25 Aug 2026", "status": "Issued"},
        ]
        for b in books_data:
            db.add(Book(**b))
        print(f"  * Seeded {len(books_data)} Library Books")

    # 13. Hostel Rooms
    if db.query(HostelRoom).count() == 0:
        rooms_data = [
            {"id": "RM-A101", "room": "A-101", "block": "Block A (Boys)", "floor": "1st Floor", "capacity": 3, "occupied": 3, "occupants": "Rahul Sharma, Arjun Verma, Karthik Rao", "status": "Occupied"},
            {"id": "RM-A102", "room": "A-102", "block": "Block A (Boys)", "floor": "1st Floor", "capacity": 3, "occupied": 1, "occupants": "Mohammed Faizan", "status": "Partially Filled"},
            {"id": "RM-B201", "room": "B-201", "block": "Block B (Girls)", "floor": "2nd Floor", "capacity": 2, "occupied": 2, "occupants": "Ananya Reddy, Priya Nair", "status": "Occupied"},
        ]
        for rm in rooms_data:
            db.add(HostelRoom(**rm))
        print(f"  * Seeded {len(rooms_data)} Hostel Rooms")

    # 14. Transport Vehicles
    if db.query(TransportVehicle).count() == 0:
        transport_data = [
            {"id": "VEH-01", "vehicle": "TS 09 EA 1234", "route": "Route 1 - Ameerpet", "driver": "Mahesh Chandra", "capacity": 45, "occupied": 38, "status": "Active", "fitnessExpiry": "14 Feb 2027", "insuranceExpiry": "20 Mar 2027"},
            {"id": "VEH-02", "vehicle": "TS 09 EA 5678", "route": "Route 2 - Kukatpally", "driver": "Ramu Yadav", "capacity": 45, "occupied": 41, "status": "Active", "fitnessExpiry": "02 Jun 2027", "insuranceExpiry": "11 Jul 2027"},
        ]
        for v in transport_data:
            db.add(TransportVehicle(**v))
        print(f"  * Seeded {len(transport_data)} Transport Vehicles")

    # 15. Documents
    if db.query(Document).count() == 0:
        docs_data = [
            {"id": "DOC-5001", "name": "Aadhaar Card", "owner": "Rahul Sharma", "ownerType": "Student", "category": "Identity", "uploadedOn": "02 Jun 2026", "status": "Verified"},
            {"id": "DOC-5002", "name": "10th Certificate", "owner": "Ananya Reddy", "ownerType": "Student", "category": "Academic", "uploadedOn": "03 Jun 2026", "status": "Verified"},
            {"id": "DOC-5003", "name": "Transfer Certificate", "owner": "Mohammed Faizan", "ownerType": "Student", "category": "Transfer", "uploadedOn": "10 Jun 2026", "status": "Pending"},
        ]
        for dc in docs_data:
            db.add(Document(**dc))
        print(f"  * Seeded {len(docs_data)} Documents")

    # 16. Notices
    if db.query(Notice).count() == 0:
        notices_data = [
            {"title": "Internal Examination Schedule - August 2026", "category": "Examination", "priority": "High", "audienceType": "Entire College", "content": "All students and faculty are notified that the First Internal Examinations will commence from 18th August 2026.", "publishOption": "Publish Now", "publishedBy": "Admin"},
            {"title": "Campus Placement Drive: Google & Microsoft", "category": "Event", "priority": "High", "audienceType": "Department", "audienceValue": "CSE", "content": "Upcoming on-campus placement registration is now open for final year CSE & CSE-AI students.", "publishOption": "Publish Now", "publishedBy": "Placement Officer"},
        ]
        for nt in notices_data:
            db.add(Notice(**nt))
        print(f"  * Seeded {len(notices_data)} Notices")

    db.commit()
    db.close()
    print("[SUCCESS] Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
