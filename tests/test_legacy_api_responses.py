import unittest

from app.schemas.fee import FeeRecordResponse
from app.schemas.staff import NonTeachingStaffResponse
from app.schemas.student import StudentResponse, StudentUpdate


class LegacyApiResponseTests(unittest.TestCase):
    def test_student_response_coerces_existing_numeric_fee_values(self) -> None:
        student = StudentResponse(
            id="STU1001",
            name="Student",
            department="CSE",
            batch="2025 - 2028",
            totalFee=120000,
            paidFee=0,
            pendingFee=120000,
            cgpa=8.25,
        )

        self.assertEqual(student.totalFee, "120000")
        self.assertEqual(student.paidFee, "0")
        self.assertEqual(student.pendingFee, "120000")
        self.assertEqual(student.cgpa, "8.25")

    def test_student_update_accepts_numeric_legacy_fee_values(self) -> None:
        update = StudentUpdate(totalFee=120000, paidFee=0, pendingFee=120000)

        self.assertEqual(update.totalFee, "120000")
        self.assertEqual(update.paidFee, "0")
        self.assertEqual(update.pendingFee, "120000")

    def test_non_teaching_response_accepts_records_without_area(self) -> None:
        staff = NonTeachingStaffResponse(
            id="NTS3001",
            name="Staff Member",
        )

        self.assertIsNone(staff.area)

    def test_fee_response_uses_legacy_student_name(self) -> None:
        record = FeeRecordResponse(
            id="STU1001",
            studentName="Student",
            department="CSE",
        )

        self.assertEqual(record.name, "Student")

    def test_fee_response_falls_back_to_student_id_when_name_is_missing(self) -> None:
        record = FeeRecordResponse(
            id="STU1001",
            studentId="STU1001",
            department="CSE",
        )

        self.assertEqual(record.name, "STU1001")


if __name__ == "__main__":
    unittest.main()
