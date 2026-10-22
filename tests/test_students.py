import io
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from starlette.datastructures import Headers
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.core import mongo as mongo_core
from app.routers import students as student_routes
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate


class StudentPersistenceTests(unittest.TestCase):
    @patch("app.core.mongo.mongo_collection")
    def test_insert_document_requires_database_acknowledgement(
        self, get_collection: Mock
    ) -> None:
        get_collection.return_value.insert_one.return_value.acknowledged = False

        with self.assertRaisesRegex(RuntimeError, "did not acknowledge"):
            mongo_core.insert_document(
                Mock(),
                "students",
                {"id": "STU2001", "name": "Persistence Test"},
            )

    @patch("app.core.mongo.mongo_collection")
    def test_insert_document_returns_record_after_acknowledged_insert(
        self, get_collection: Mock
    ) -> None:
        get_collection.return_value.insert_one.return_value.acknowledged = True

        record = mongo_core.insert_document(
            Mock(),
            "students",
            {"id": "STU2002", "name": "Persistence Test"},
        )

        get_collection.return_value.insert_one.assert_called_once()
        self.assertEqual(record["id"], "STU2002")
        self.assertNotIn("_id", record)


class StudentSchemaTests(unittest.TestCase):
    def test_admission_fields_are_retained_on_create_and_update(self) -> None:
        fields = {
            "name": "Asha Student",
            "department": "Computer Science & Engineering",
            "batch": "2025 - 2028",
            "branch": "Computer Science & Engineering",
            "program": "B.Tech",
            "permanentAddress": "Permanent address",
            "currentAddress": "Current address",
            "fatherPhone": "9000000001",
            "motherPhone": "9000000002",
            "guardianName": "Guardian",
            "relationship": "Aunt",
            "admissionNo": "ADM-2025-15",
            "admissionDate": "2025-06-01",
            "academicYear": "2025-2026",
            "quota": "General",
            "entranceExam": "State Entrance Test",
            "rank": "1250",
            "previousInstitution": "Example School",
            "classAdvisor": "Dr. Example",
            "documents": {"photo": {"fileId": str(ObjectId()), "filename": "photo.png"}},
        }

        created = StudentCreate(**fields).model_dump()
        updated = StudentUpdate(**fields).model_dump(exclude_unset=True)

        for field, value in fields.items():
            self.assertEqual(created[field], value)
            self.assertEqual(updated[field], value)

    def test_response_accepts_legacy_document_values(self) -> None:
        response = StudentResponse(
            id="STU1001",
            name="Legacy Student",
            department="Information Technology",
            batch="2024 - 2027",
            documents=["Aadhaar Card", "10th Certificate"],
        )

        self.assertEqual(response.documents, ["Aadhaar Card", "10th Certificate"])

    def test_guardian_only_admission_requires_guardian_contact(self) -> None:
        with self.assertRaises(ValidationError):
            StudentCreate(
                name="Guardian Student",
                department="CSE",
                batch="2026 - 2030",
                parentGuardianType="Guardian Available",
            )

        student = StudentCreate(
            name="Guardian Student",
            department="CSE",
            batch="2026 - 2030",
            parentGuardianType="Guardian Available",
            guardianName="Guardian",
            relationship="Aunt",
            guardianPhone="9876543210",
        )
        self.assertEqual(student.guardianName, "Guardian")

    def test_special_case_admission_requires_reason_and_emergency_contact(self) -> None:
        with self.assertRaises(ValidationError):
            StudentCreate(
                name="Special Case Student",
                department="CSE",
                batch="2026 - 2030",
                parentGuardianType="Not Available / Special Case",
                specialReason="",
            )

    def test_submitted_application_requires_terms_and_privacy_acceptance(self) -> None:
        fields = {
            "name": "Submitted Student",
            "department": "CSE",
            "batch": "2026 - 2030",
            "applicationStatus": "Submitted",
            "termsAccepted": True,
        }
        with self.assertRaises(ValidationError):
            StudentCreate(**fields)

        with self.assertRaises(ValidationError):
            StudentUpdate(**fields)

        submitted = StudentCreate(**{**fields, "privacyAccepted": True})
        self.assertEqual(submitted.applicationStatus, "Submitted")

    def test_partial_draft_can_be_created_without_required_admission_fields(self) -> None:
        draft = StudentCreate(applicationStatus="Draft")
        editable_draft = StudentUpdate(
            applicationStatus="Draft",
            parentGuardianType="Guardian Available",
        )

        self.assertEqual(draft.applicationStatus, "Draft")
        self.assertIsNone(draft.name)
        self.assertIsNone(draft.department)
        self.assertIsNone(draft.batch)
        self.assertEqual(editable_draft.parentGuardianType, "Guardian Available")

        with self.assertRaises(ValidationError):
            StudentCreate()

    @patch("app.routers.students.insert_document")
    @patch("app.routers.students.get_document", return_value=None)
    @patch("app.routers.students.generate_next_student_id", return_value="STU1002")
    def test_create_persists_generated_student_id_and_admission_fields(
        self,
        generate_id: Mock,
        get_document: Mock,
        insert_document: Mock,
    ) -> None:
        payload = StudentCreate(
            name="Asha Student",
            department="Computer Science & Engineering",
            batch="2025 - 2028",
            admissionDate="2025-06-01",
            permanentAddress="Permanent address",
            currentAddress="Current address",
        )
        insert_document.side_effect = lambda db, collection, data: data

        result = student_routes.create_student(payload, Mock())

        stored_record = insert_document.call_args.args[2]
        self.assertEqual(stored_record["id"], "STU1002")
        self.assertEqual(stored_record["studentId"], "STU1002")
        self.assertEqual(stored_record["admissionDate"], "2025-06-01")
        self.assertEqual(stored_record["currentAddress"], "Current address")
        self.assertEqual(result["id"], "STU1002")

    @patch("app.routers.students.insert_document")
    @patch("app.routers.students.get_document", return_value=None)
    @patch("app.routers.students.generate_next_student_id", return_value="STU1004")
    def test_partial_draft_is_persisted_without_completing_admission_fields(
        self,
        generate_id: Mock,
        get_document: Mock,
        insert_document: Mock,
    ) -> None:
        payload = StudentCreate(applicationStatus="Draft")
        insert_document.side_effect = lambda db, collection, data: data

        result = student_routes.create_student(payload, Mock())

        stored_record = insert_document.call_args.args[2]
        self.assertEqual(stored_record["applicationStatus"], "Draft")
        self.assertEqual(stored_record["id"], "STU1004")
        self.assertIsNone(stored_record["name"])
        self.assertEqual(result["applicationStatus"], "Draft")

    @patch("app.routers.students.insert_document")
    @patch("app.routers.students.get_document", return_value=None)
    @patch("app.routers.students.generate_next_student_id", return_value="STU1003")
    def test_student_create_api_returns_saved_record(
        self,
        generate_id: Mock,
        get_document: Mock,
        insert_document: Mock,
    ) -> None:
        app = FastAPI()
        app.include_router(student_routes.router, prefix="/api")
        app.dependency_overrides[student_routes.get_db] = lambda: Mock()
        insert_document.side_effect = lambda db, collection, data: data
        payload = {
            "name": "API Test Student",
            "department": "Computer Science & Engineering",
            "branch": "Computer Science & Engineering",
            "program": "B.Tech",
            "batch": "2026 - 2030",
            "permanentAddress": "Address for API test",
            "currentAddress": "Current address for API test",
        }

        with TestClient(app) as client:
            response = client.post("/api/students", json=payload)

        self.assertEqual(response.status_code, 201, response.text)
        saved = response.json()
        self.assertEqual(saved["id"], "STU1003")
        self.assertEqual(saved["studentId"], "STU1003")
        self.assertEqual(saved["branch"], payload["branch"])
        self.assertEqual(saved["currentAddress"], payload["currentAddress"])
        self.assertEqual(insert_document.call_args.args[1], "students")


class StudentDocumentUploadTests(unittest.IsolatedAsyncioTestCase):
    @patch("app.routers.students.GridFSBucket")
    @patch("app.routers.students.mongo_collection")
    @patch("app.routers.students.get_document")
    async def test_document_is_saved_in_gridfs_and_metadata_on_student(
        self,
        get_document: Mock,
        get_collection: Mock,
        gridfs_bucket: Mock,
    ) -> None:
        student = {
            "id": "STU1001",
            "name": "Asha Student",
            "department": "CSE",
            "batch": "2025 - 2028",
            "documents": {},
        }
        file_id = ObjectId()
        updated = {
            **student,
            "documents": {
                "idProof": {
                    "fileId": str(file_id),
                    "filename": "identity.pdf",
                    "contentType": "application/pdf",
                    "size": 8,
                }
            },
        }
        get_document.side_effect = [student, updated]
        bucket = Mock()
        bucket.upload_from_stream.return_value = file_id
        gridfs_bucket.return_value = bucket
        collection = Mock()
        get_collection.return_value = collection
        upload = StarletteUploadFile(
            filename="identity.pdf",
            file=io.BytesIO(b"%PDF-1.7"),
            headers=Headers({"content-type": "application/pdf"}),
        )

        result = await student_routes.upload_student_document(
            "STU1001",
            "idProof",
            upload,
            Mock(),
        )

        bucket.upload_from_stream.assert_called_once()
        self.assertEqual(bucket.upload_from_stream.call_args.args[1].read(), b"%PDF-1.7")
        saved_metadata = collection.update_one.call_args.args[1]["$set"]["documents.idProof"]
        self.assertEqual(
            {key: value for key, value in saved_metadata.items() if key != "uploadedAt"},
            updated["documents"]["idProof"],
        )
        self.assertIsInstance(datetime.fromisoformat(saved_metadata["uploadedAt"]), datetime)
        self.assertEqual(result["documents"], updated["documents"])

    @patch("app.routers.students.GridFSBucket")
    @patch("app.routers.students.get_document", return_value={"id": "STU1001"})
    async def test_unsupported_document_type_is_rejected(
        self,
        get_document: Mock,
        gridfs_bucket: Mock,
    ) -> None:
        upload = StarletteUploadFile(
            filename="identity.pdf",
            file=io.BytesIO(b"%PDF-1.7"),
            headers=Headers({"content-type": "application/pdf"}),
        )

        with self.assertRaises(HTTPException) as error:
            await student_routes.upload_student_document(
                "STU1001",
                "unsupported",
                upload,
                Mock(),
            )

        self.assertEqual(error.exception.status_code, 400)
        gridfs_bucket.assert_not_called()

    @patch("app.routers.students.GridFSBucket")
    @patch("app.routers.students.get_document", return_value={"id": "STU1001"})
    async def test_document_content_must_match_declared_mime_type(
        self,
        get_document: Mock,
        gridfs_bucket: Mock,
    ) -> None:
        upload = StarletteUploadFile(
            filename="identity.pdf",
            file=io.BytesIO(b"not a PDF"),
            headers=Headers({"content-type": "application/pdf"}),
        )

        with self.assertRaises(HTTPException) as error:
            await student_routes.upload_student_document(
                "STU1001",
                "idProof",
                upload,
                Mock(),
            )

        self.assertEqual(error.exception.status_code, 415)
        gridfs_bucket.assert_not_called()


class StudentDocumentDeleteTests(unittest.TestCase):
    @patch("app.routers.students.GridFSBucket")
    @patch("app.routers.students.mongo_collection")
    @patch("app.routers.students.get_document")
    def test_delete_removes_gridfs_file_and_document_metadata(
        self,
        get_document: Mock,
        get_collection: Mock,
        gridfs_bucket: Mock,
    ) -> None:
        file_id = ObjectId()
        existing = {
            "id": "STU1001",
            "documents": {"idProof": {"fileId": str(file_id), "filename": "identity.pdf"}},
        }
        updated = {"id": "STU1001", "documents": {}}
        get_document.side_effect = [existing, updated]
        bucket = Mock()
        gridfs_bucket.return_value = bucket
        collection = Mock()
        collection.update_one.return_value.matched_count = 1
        get_collection.return_value = collection

        result = student_routes.delete_student_document("STU1001", "idProof", Mock())

        bucket.delete.assert_called_once_with(file_id)
        self.assertEqual(
            collection.update_one.call_args.args[1]["$unset"],
            {"documents.idProof": ""},
        )
        self.assertEqual(result["documents"], {})


if __name__ == "__main__":
    unittest.main()
