import contextlib
import io
import os
import unittest
from unittest.mock import Mock, patch

from pymongo.errors import ServerSelectionTimeoutError

from app.core import mongo as mongo_core
from app.core.database import get_db
from app.core.mongo import _connection_error_help, check_mongodb_connection, ensure_indexes
from app.seed import seed_database


class MongoStartupTests(unittest.TestCase):
    @patch("app.core.mongo.mongo_db")
    def test_ensure_indexes_creates_case_insensitive_unique_email_index(
        self, database: Mock
    ) -> None:
        users = database.__getitem__.return_value
        users.aggregate.return_value = []

        ensure_indexes()

        users.create_index.assert_called_once()
        self.assertEqual(users.create_index.call_args.args[0], "email")
        self.assertTrue(users.create_index.call_args.kwargs["unique"])
        self.assertEqual(
            users.create_index.call_args.kwargs["name"],
            "email_case_insensitive_unique",
        )
        self.assertEqual(
            users.create_index.call_args.kwargs["collation"].document,
            {"locale": "en", "strength": 2},
        )

    @patch("app.core.mongo.mongo_db")
    def test_duplicate_emails_are_reported_masked_before_index_creation(
        self, database: Mock
    ) -> None:
        users = database.__getitem__.return_value
        users.aggregate.return_value = [
            {"_id": "admin@college.edu", "count": 2}
        ]

        with self.assertRaisesRegex(RuntimeError, r"a\*\*\*@college\.edu"):
            ensure_indexes()

        users.create_index.assert_not_called()

    @patch("app.seed.ensure_indexes")
    @patch(
        "app.seed.check_mongodb_connection",
        side_effect=RuntimeError("MongoDB unavailable"),
    )
    def test_seed_checks_connection_before_creating_indexes(
        self, check_connection: Mock, create_indexes: Mock
    ) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "MongoDB unavailable"):
                seed_database()

        check_connection.assert_called_once_with()
        create_indexes.assert_not_called()

    @patch("app.seed.mongo_collection")
    @patch("app.seed.ensure_indexes")
    @patch("app.seed.check_mongodb_connection")
    def test_seed_requires_admin_password_from_environment(
        self,
        check_connection: Mock,
        create_indexes: Mock,
        get_collection: Mock,
    ) -> None:
        users = get_collection.return_value
        users.find_one.return_value = None

        with patch.dict(os.environ, {"SEED_ADMIN_PASSWORD": ""}):
            with self.assertRaisesRegex(RuntimeError, "SEED_ADMIN_PASSWORD"):
                seed_database()

        users.insert_one.assert_not_called()

    def test_tls_handshake_failure_has_actionable_safe_guidance(self) -> None:
        message = _connection_error_help(
            ServerSelectionTimeoutError("SSL handshake failed")
        )

        self.assertIn("TLS negotiation failed", message)
        self.assertIn("Network Access", message)

    @patch("app.core.mongo.mongo_db")
    @patch("app.core.mongo.client")
    def test_mongodb_connection_failure_does_not_silently_fall_back(
        self,
        client: Mock,
        database: Mock,
    ) -> None:
        client.admin.command.side_effect = ServerSelectionTimeoutError("unavailable")

        with self.assertRaisesRegex(RuntimeError, "MongoDB ping failed"):
            check_mongodb_connection()

        client.admin.command.assert_called_once_with("ping")
        self.assertIs(mongo_core.mongo_db, database)

    @patch("app.core.mongo.mongo_db", None)
    def test_database_dependency_reads_database_after_connection_check(self) -> None:
        database = Mock()
        mongo_core.mongo_db = database

        self.assertIs(next(get_db()), database)


if __name__ == "__main__":
    unittest.main()
