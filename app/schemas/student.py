<<<<<<< HEAD
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StudentBase(BaseModel):
    name: str
    department: str
    batch: str
    year: Optional[str] = "1st Year"
    semester: Optional[str] = "Semester 1"
    section: Optional[str] = "A"
    gender: Optional[str] = "Male"
    admissionType: Optional[str] = "Regular"
    attendance: Optional[int] = 0
    feeStatus: Optional[str] = "Pending"
    status: Optional[str] = "Active"
    
    phone: Optional[str] = None
    email: Optional[str] = None
    dob: Optional[str] = None
    bloodGroup: Optional[str] = None
    address: Optional[str] = None
    
    father: Optional[str] = None
    mother: Optional[str] = None
    guardianPhone: Optional[str] = None
    
=======
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


def _normalize_legacy_numeric_strings(value: Any) -> Any:
    if isinstance(value, (int, float)):
        return str(value)
    return value


def _validate_parent_guardian_details(values: dict[str, Any]) -> dict[str, Any]:
    if values.get("applicationStatus") == "Draft":
        return values

    information_type = values.get("parentGuardianType")
    required_fields: tuple[str, ...] = ()
    if information_type in {"Parents Available", "Both Parents and Guardian Available"}:
        required_fields = ("father", "fatherPhone", "mother")
    elif information_type == "Guardian Available":
        required_fields = ("guardianName", "relationship", "guardianPhone")
    elif information_type == "Not Available / Special Case":
        required_fields = ("specialReason", "emergencyMobile")

    missing = [field for field in required_fields if not str(values.get(field) or "").strip()]
    if missing:
        labels = {
            "father": "father's name",
            "fatherPhone": "father's mobile number",
            "mother": "mother's name",
            "guardianName": "guardian name",
            "relationship": "guardian relationship",
            "guardianPhone": "guardian mobile number",
            "specialReason": "special-case reason",
            "emergencyMobile": "alternative emergency contact",
        }
        raise ValueError("Required parent/guardian information is missing: " + ", ".join(labels[field] for field in missing))
    return values


def _validate_student_core_fields(values: dict[str, Any]) -> dict[str, Any]:
    if values.get("applicationStatus") != "Draft":
        missing = [
            field
            for field in ("name", "department", "batch")
            if not str(values.get(field) or "").strip()
        ]
        if missing:
            raise ValueError("Required student fields are missing: " + ", ".join(missing))
    return values


def _validate_submission_acknowledgements(values: dict[str, Any]) -> dict[str, Any]:
    if values.get("applicationStatus") == "Submitted":
        missing = [
            label
            for field, label in (
                ("termsAccepted", "terms"),
                ("privacyAccepted", "privacy policy"),
            )
            if values.get(field) is not True
        ]
        if missing:
            raise ValueError("Submission requires acceptance of the " + " and ".join(missing) + ".")
    return values


class StudentBase(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    batch: Optional[str] = None
    year: Optional[str] = "1st Year"
    semester: Optional[str] = "Semester 1"
    section: Optional[str] = "A"
    gender: Optional[str] = None
    admissionType: Optional[str] = "Regular"
    attendance: Optional[int] = 0
    feeStatus: Optional[str] = "Pending"
    feePlan: Optional[str] = None
    feeDueDate: Optional[str] = None
    status: Optional[str] = "Active"
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    dob: Optional[str] = None
    bloodGroup: Optional[str] = None
    address: Optional[str] = None
    permanentAddress: Optional[str] = None
    currentAddress: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    pinCode: Optional[str] = None
    currentState: Optional[str] = None
    currentDistrict: Optional[str] = None
    currentPin: Optional[str] = None
    nationality: Optional[str] = None
    emergencyMobile: Optional[str] = None
    parentGuardianType: Optional[str] = None
    parentEmail: Optional[EmailStr] = None
    father: Optional[str] = None
    fatherPhone: Optional[str] = None
    mother: Optional[str] = None
    motherPhone: Optional[str] = None
    guardianName: Optional[str] = None
    relationship: Optional[str] = None
    guardianPhone: Optional[str] = None
    guardianEmail: Optional[EmailStr] = None
    guardianAddress: Optional[str] = None
    occupation: Optional[str] = None
    specialReason: Optional[str] = None
    program: Optional[str] = None
    branch: Optional[str] = None
    studentId: Optional[str] = None
    admissionNo: Optional[str] = None
    admissionDate: Optional[str] = None
    admissionYear: Optional[str] = None
    academicYear: Optional[str] = None
    batchStartYear: Optional[int] = None
    batchDuration: Optional[int] = None
    registrationNumber: Optional[str] = None
    quota: Optional[str] = None
    entranceExam: Optional[str] = None
    rank: Optional[str] = None
    previousInstitution: Optional[str] = None
    regulation: Optional[str] = None
    classAdvisor: Optional[str] = None
    feeActivationDate: Optional[str] = None
    hostelNeeded: Optional[str] = None
    hostelName: Optional[str] = None
    hostelBlock: Optional[str] = None
    roomType: Optional[str] = None
    hostelJoinDate: Optional[str] = None
    hostelPlan: Optional[str] = None
    hostelStatus: Optional[str] = None
    transportNeeded: Optional[str] = None
    transportRoute: Optional[str] = None
    pickupPoint: Optional[str] = None
    dropPoint: Optional[str] = None
    busNumber: Optional[str] = None
    transportJoinDate: Optional[str] = None
    transportPlan: Optional[str] = None
    transportStatus: Optional[str] = None
    handledBy: Optional[str] = None
    admissionFaculty: Optional[str] = None
    referralType: Optional[str] = None
    referredBy: Optional[str] = None
    referralContact: Optional[str] = None
    referralRemarks: Optional[str] = None
    applicationStatus: Optional[str] = None
    termsAccepted: Optional[bool] = None
    privacyAccepted: Optional[bool] = None
    termsPolicyVersion: Optional[str] = None
    privacyPolicyVersion: Optional[str] = None
    documents: Any = Field(default_factory=dict)
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    totalFee: Optional[str] = "₹0"
    paidFee: Optional[str] = "₹0"
    pendingFee: Optional[str] = "₹0"
    cgpa: Optional[str] = "0.0"

<<<<<<< HEAD
=======
    model_config = ConfigDict(from_attributes=True)

    @field_validator("totalFee", "paidFee", "pendingFee", "cgpa", mode="before")
    @classmethod
    def accept_legacy_numeric_values(cls, value: Any) -> Any:
        return _normalize_legacy_numeric_strings(value)

    @field_validator("email", "parentEmail", "guardianEmail", mode="before")
    @classmethod
    def normalize_blank_emails(cls, value: Any) -> Any:
        return None if value == "" else value

>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9

class StudentCreate(StudentBase):
    id: Optional[str] = None

<<<<<<< HEAD
=======
    @model_validator(mode="before")
    @classmethod
    def validate_parent_guardian_details(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return _validate_submission_acknowledgements(
                _validate_student_core_fields(_validate_parent_guardian_details(value))
            )
        return value

>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    batch: Optional[str] = None
    year: Optional[str] = None
    semester: Optional[str] = None
    section: Optional[str] = None
    gender: Optional[str] = None
    admissionType: Optional[str] = None
    attendance: Optional[int] = None
    feeStatus: Optional[str] = None
<<<<<<< HEAD
    status: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    dob: Optional[str] = None
    bloodGroup: Optional[str] = None
    address: Optional[str] = None
    father: Optional[str] = None
    mother: Optional[str] = None
    guardianPhone: Optional[str] = None
=======
    feePlan: Optional[str] = None
    feeDueDate: Optional[str] = None
    status: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    dob: Optional[str] = None
    bloodGroup: Optional[str] = None
    address: Optional[str] = None
    permanentAddress: Optional[str] = None
    currentAddress: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    pinCode: Optional[str] = None
    currentState: Optional[str] = None
    currentDistrict: Optional[str] = None
    currentPin: Optional[str] = None
    nationality: Optional[str] = None
    emergencyMobile: Optional[str] = None
    parentGuardianType: Optional[str] = None
    parentEmail: Optional[EmailStr] = None
    father: Optional[str] = None
    fatherPhone: Optional[str] = None
    mother: Optional[str] = None
    motherPhone: Optional[str] = None
    guardianName: Optional[str] = None
    relationship: Optional[str] = None
    guardianPhone: Optional[str] = None
    guardianEmail: Optional[EmailStr] = None
    guardianAddress: Optional[str] = None
    occupation: Optional[str] = None
    specialReason: Optional[str] = None
    program: Optional[str] = None
    branch: Optional[str] = None
    studentId: Optional[str] = None
    admissionNo: Optional[str] = None
    admissionDate: Optional[str] = None
    admissionYear: Optional[str] = None
    academicYear: Optional[str] = None
    batchStartYear: Optional[int] = None
    batchDuration: Optional[int] = None
    registrationNumber: Optional[str] = None
    quota: Optional[str] = None
    entranceExam: Optional[str] = None
    rank: Optional[str] = None
    previousInstitution: Optional[str] = None
    regulation: Optional[str] = None
    classAdvisor: Optional[str] = None
    feeActivationDate: Optional[str] = None
    hostelNeeded: Optional[str] = None
    hostelName: Optional[str] = None
    hostelBlock: Optional[str] = None
    roomType: Optional[str] = None
    hostelJoinDate: Optional[str] = None
    hostelPlan: Optional[str] = None
    hostelStatus: Optional[str] = None
    transportNeeded: Optional[str] = None
    transportRoute: Optional[str] = None
    pickupPoint: Optional[str] = None
    dropPoint: Optional[str] = None
    busNumber: Optional[str] = None
    transportJoinDate: Optional[str] = None
    transportPlan: Optional[str] = None
    transportStatus: Optional[str] = None
    handledBy: Optional[str] = None
    admissionFaculty: Optional[str] = None
    referralType: Optional[str] = None
    referredBy: Optional[str] = None
    referralContact: Optional[str] = None
    referralRemarks: Optional[str] = None
    applicationStatus: Optional[str] = None
    termsAccepted: Optional[bool] = None
    privacyAccepted: Optional[bool] = None
    termsPolicyVersion: Optional[str] = None
    privacyPolicyVersion: Optional[str] = None
    documents: Optional[Any] = None
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
    totalFee: Optional[str] = None
    paidFee: Optional[str] = None
    pendingFee: Optional[str] = None
    cgpa: Optional[str] = None

<<<<<<< HEAD
=======
    @field_validator("totalFee", "paidFee", "pendingFee", "cgpa", mode="before")
    @classmethod
    def accept_legacy_numeric_values(cls, value: Any) -> Any:
        return _normalize_legacy_numeric_strings(value)

    @field_validator("email", "parentEmail", "guardianEmail", mode="before")
    @classmethod
    def normalize_blank_emails(cls, value: Any) -> Any:
        return None if value == "" else value

    @model_validator(mode="before")
    @classmethod
    def validate_parent_guardian_details(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return _validate_submission_acknowledgements(_validate_parent_guardian_details(value))
        return value

>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9

class StudentResponse(StudentBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
<<<<<<< HEAD

    model_config = ConfigDict(from_attributes=True)
=======
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
