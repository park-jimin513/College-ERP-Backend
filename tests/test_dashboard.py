import unittest
from unittest.mock import Mock, patch

from app.routers import dashboard


class DashboardDraftTests(unittest.TestCase):
    @patch("app.routers.dashboard.mongo_collection")
    def test_student_count_excludes_saved_drafts(self, get_collection: Mock) -> None:
        students = Mock()
        students.count_documents.side_effect = [8, 2]
        teaching = Mock()
        teaching.count_documents.return_value = 3
        non_teaching = Mock()
        non_teaching.count_documents.return_value = 2
        departments = Mock()
        departments.count_documents.return_value = 4
        fees = Mock()
        fees.find.return_value = []
        get_collection.side_effect = [students, teaching, non_teaching, departments, fees]

        result = dashboard.get_dashboard_stats(Mock())

        self.assertEqual(result.totalStudents, 6)
        self.assertEqual(result.stats[0].value, "6")

    @patch("app.routers.dashboard.list_documents")
    def test_drafts_are_not_reported_as_new_student_activity(self, list_records: Mock) -> None:
        list_records.side_effect = [
            [],
            [
                {"name": "Incomplete", "applicationStatus": "Draft"},
                {"name": "Complete", "department": "CSE", "applicationStatus": "Submitted"},
            ],
        ]

        activity = dashboard.get_recent_activity(Mock())

        self.assertEqual(activity[0].title, "New student registered")
        self.assertIn("Complete was added", activity[0].detail)


if __name__ == "__main__":
    unittest.main()
