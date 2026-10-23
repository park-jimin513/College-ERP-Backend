import json
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.routers.auth import (
    OTP_MAX_ATTEMPTS,
    EmailProviderDeliveryError,
    _hash_otp,
    _send_otp_email,
    get_current_user,
    login,
    reset_password,
    send_otp,
    signup,
    verify_otp,
)
from app.schemas.user import OTPRequest, OTPVerify, PasswordResetConfirm, UserCreate, UserLogin


class FakeUsers:
    def __init__(self, *users: dict) -> None:
        self.users = [dict(user) for user in users]

    @staticmethod
    def _matches(document: dict, filters: dict) -> bool:
        for field, expected in filters.items():
            if field == "$or":
                if not any(FakeUsers._matches(document, item) for item in expected):
                    return False
                continue

            actual = document.get(field)
            if isinstance(expected, dict):
                if "$gt" in expected and (actual is None or actual <= expected["$gt"]):
                    return False
                if "$lt" in expected and (actual is None or actual >= expected["$lt"]):
                    return False
                if "$lte" in expected and (actual is not None and actual > expected["$lte"]):
                    return False
                if "$exists" in expected and (field in document) != expected["$exists"]:
                    return False
                if "$ne" in expected and actual == expected["$ne"]:
                    return False
            elif field == "email":
                if str(actual).casefold() != str(expected).casefold():
                    return False
            elif actual != expected:
                return False
        return True

    def find_one(self, filters: dict, **_kwargs):
        return next((user for user in self.users if self._matches(user, filters)), None)

    def update_one(self, filters: dict, update: dict):
        user = next((item for item in self.users if self._matches(item, filters)), None)
        if user is None:
            return SimpleNamespace(matched_count=0, modified_count=0)

        for field, value in update.get("$set", {}).items():
            user[field] = value
        for field, increment in update.get("$inc", {}).items():
            user[field] = (user.get(field) or 0) + increment
        return SimpleNamespace(matched_count=1, modified_count=1)

    def insert_one(self, user: dict):
        self.users.append(dict(user))

    def delete_one(self, filters: dict):
        user = next((item for item in self.users if self._matches(item, filters)), None)
        if user is not None:
            self.users.remove(user)
        return SimpleNamespace(deleted_count=int(user is not None))


def make_user(**updates) -> dict:
    user = {
        "_id": "user-1",
        "id": 1,
        "name": "Example User",
        "email": "example@example.com",
        "role": "admin",
        "is_active": True,
        "is_verified": False,
        "otp_code": None,
        "otp_expires_at": None,
        "otp_attempts": 0,
        "otp_last_sent_at": None,
        "failed_attempts": 0,
        "locked_until": None,
        "created_at": datetime.now(timezone.utc),
    }
    user.update(updates)
    return user


class AuthEmailOtpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.users = FakeUsers(make_user())
        self.db = Mock()
        self.collection_patch = patch(
            "app.routers.auth.mongo_collection",
            return_value=self.users,
        )
        self.collection_patch.start()
        self.addCleanup(self.collection_patch.stop)

    def store_otp(self, otp: str, expires_at: datetime, attempts: int = 0) -> None:
        with patch("app.routers.auth.settings.SECRET_KEY", "test-secret"):
            digest = _hash_otp("example@example.com", otp)
        self.users.users[0].update(
            otp_code=digest,
            otp_expires_at=expires_at,
            otp_attempts=attempts,
        )

    @patch("app.routers.auth._find_user")
    @patch("app.routers.auth.jwt.decode", return_value={"sub": "registered@example.com"})
    def test_current_user_returns_only_the_authenticated_users_registration_details(
        self,
        _decode_token: Mock,
        find_user: Mock,
    ) -> None:
        find_user.return_value = {
            "id": 12,
            "name": "Registered User",
            "email": "registered@example.com",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }

        response = get_current_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token"),
            self.db,
        )

        self.assertEqual(response.name, "Registered User")
        self.assertEqual(response.email, "registered@example.com")
        find_user.assert_called_once()

    def test_current_user_rejects_missing_bearer_token(self) -> None:
        with self.assertRaises(HTTPException) as error:
            get_current_user(None, self.db)

        self.assertEqual(error.exception.status_code, 401)

    @patch("app.routers.auth._send_otp_email")
    @patch("app.routers.auth.secrets.randbelow", return_value=23456)
    def test_send_otp_uses_mocked_provider_and_stores_only_a_digest(
        self,
        _randbelow: Mock,
        send_email: Mock,
    ) -> None:
        with patch("app.routers.auth.settings.SECRET_KEY", "test-secret"):
            response = send_otp(OTPRequest(email="example@example.com"), self.db)
            expected_digest = _hash_otp("example@example.com", "123456")

        user = self.users.users[0]
        self.assertTrue(response.otp_required)
        self.assertEqual(user["otp_code"], expected_digest)
        self.assertNotEqual(user["otp_code"], "123456")
        self.assertEqual(user["otp_attempts"], 0)
        self.assertIsNotNone(user["otp_last_sent_at"])
        send_email.assert_called_once_with("example@example.com", "123456")

    @patch("app.routers.auth.urlopen")
    def test_resend_provider_uses_https_api_without_sending_a_real_email(
        self,
        urlopen: Mock,
    ) -> None:
        response = Mock()
        response.status = 200
        urlopen.return_value.__enter__.return_value = response

        with (
            patch("app.routers.auth.settings.EMAIL_PROVIDER", "resend"),
            patch("app.routers.auth.settings.EMAIL_API_KEY", "test-api-key"),
            patch("app.routers.auth.settings.EMAIL_FROM", "College ERP <otp@example.com>"),
        ):
            _send_otp_email("recipient@example.com", "123456")

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.resend.com/emails")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-api-key")
        self.assertEqual(
            json.loads(request.data),
            {
                "from": "College ERP <otp@example.com>",
                "to": ["recipient@example.com"],
                "subject": "College ERP OTP Verification",
                "text": "Your College ERP verification code is 123456. It expires in 15 minutes.",
            },
        )
        urlopen.assert_called_once()

    @patch("app.routers.auth.urlopen")
    def test_resend_http_failure_is_reported_without_provider_response_body(
        self,
        urlopen: Mock,
    ) -> None:
        from urllib.error import HTTPError

        urlopen.side_effect = HTTPError(
            "https://api.resend.com/emails",
            429,
            "rate limited",
            {},
            None,
        )
        with (
            patch("app.routers.auth.settings.EMAIL_PROVIDER", "resend"),
            patch("app.routers.auth.settings.EMAIL_API_KEY", "test-api-key"),
            patch("app.routers.auth.settings.EMAIL_FROM", "otp@example.com"),
        ):
            with self.assertRaises(EmailProviderDeliveryError) as error:
                _send_otp_email("recipient@example.com", "123456")

        self.assertEqual(error.exception.status_code, 429)
        self.assertNotIn("test-api-key", str(error.exception))

    @patch("app.routers.auth.smtplib.SMTP")
    def test_existing_gmail_smtp_configuration_remains_explicitly_supported(
        self,
        smtp_factory: Mock,
    ) -> None:
        smtp = smtp_factory.return_value.__enter__.return_value
        with (
            patch("app.routers.auth.settings.EMAIL_PROVIDER", "smtp"),
            patch("app.routers.auth.settings.EMAIL_USER", "sender@example.com"),
            patch("app.routers.auth.settings.EMAIL_PASS", "test-app-password"),
        ):
            _send_otp_email("recipient@example.com", "123456")

        smtp_factory.assert_called_once_with(
            "smtp.gmail.com",
            587,
            timeout=15,
        )
        smtp.starttls.assert_called_once()
        smtp.login.assert_called_once_with("sender@example.com", "test-app-password")
        smtp.send_message.assert_called_once()

    @patch("app.routers.auth.urlopen")
    def test_missing_provider_configuration_returns_safe_503_and_invalidates_code(
        self,
        urlopen: Mock,
    ) -> None:
        with (
            patch("app.routers.auth.settings.EMAIL_PROVIDER", "resend"),
            patch("app.routers.auth.settings.EMAIL_API_KEY", None),
            patch("app.routers.auth.settings.EMAIL_FROM", None),
            self.assertLogs("app.routers.auth", level="ERROR") as captured_logs,
        ):
            with self.assertRaises(HTTPException) as error:
                send_otp(OTPRequest(email="example@example.com"), self.db)

        self.assertEqual(error.exception.status_code, 503)
        self.assertNotIn("API key", error.exception.detail)
        self.assertIn("EMAIL_API_KEY", "\n".join(captured_logs.output))
        self.assertNotIn("123456", "\n".join(captured_logs.output))
        self.assertIsNone(self.users.users[0]["otp_code"])
        self.assertIsNone(self.users.users[0]["otp_expires_at"])
        urlopen.assert_not_called()

    @patch("app.routers.auth._send_otp_email")
    def test_provider_failure_returns_safe_503_and_invalidates_code(
        self,
        send_email: Mock,
    ) -> None:
        send_email.side_effect = EmailProviderDeliveryError(status_code=401)

        with self.assertLogs("app.routers.auth", level="ERROR") as captured_logs:
            with self.assertRaises(HTTPException) as error:
                send_otp(OTPRequest(email="example@example.com"), self.db)

        self.assertEqual(error.exception.status_code, 503)
        self.assertNotIn("401", error.exception.detail)
        self.assertIn("HTTP status=401", "\n".join(captured_logs.output))
        self.assertIsNone(self.users.users[0]["otp_code"])

    def test_unknown_email_gets_same_generic_send_response(self) -> None:
        self.users.users.clear()

        response = send_otp(OTPRequest(email="unknown@example.com"), self.db)

        self.assertEqual(response.message, "If an account exists for this email, a verification code will be sent.")
        self.assertTrue(response.otp_required)

    @patch("app.routers.auth._send_otp_email")
    def test_resend_is_throttled_without_sending_another_email(
        self,
        send_email: Mock,
    ) -> None:
        self.users.users[0]["otp_last_sent_at"] = datetime.now(timezone.utc)

        response = send_otp(OTPRequest(email="example@example.com"), self.db)

        self.assertTrue(response.otp_required)
        send_email.assert_not_called()

    def test_expired_otp_is_rejected(self) -> None:
        self.store_otp("123456", datetime.now(timezone.utc) - timedelta(seconds=1))

        with self.assertRaises(HTTPException) as error:
            verify_otp(OTPVerify(email="example@example.com", otp="123456"), self.db)

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(error.exception.detail, "Invalid or expired OTP code.")
        self.assertFalse(self.users.users[0]["is_verified"])

    def test_invalid_otp_increments_attempt_count(self) -> None:
        self.store_otp("123456", datetime.now(timezone.utc) + timedelta(minutes=5))

        with self.assertRaises(HTTPException) as error:
            verify_otp(OTPVerify(email="example@example.com", otp="000000"), self.db)

        self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(self.users.users[0]["otp_attempts"], 1)

    def test_otp_attempt_limit_blocks_further_guesses_and_correct_code(self) -> None:
        self.store_otp("123456", datetime.now(timezone.utc) + timedelta(minutes=5))

        for _ in range(OTP_MAX_ATTEMPTS):
            with self.assertRaises(HTTPException):
                verify_otp(OTPVerify(email="example@example.com", otp="000000"), self.db)

        with self.assertRaises(HTTPException):
            verify_otp(OTPVerify(email="example@example.com", otp="123456"), self.db)

        self.assertEqual(self.users.users[0]["otp_attempts"], OTP_MAX_ATTEMPTS)
        self.assertFalse(self.users.users[0]["is_verified"])

    def test_verification_consumes_otp_exactly_once(self) -> None:
        self.store_otp("123456", datetime.now(timezone.utc) + timedelta(minutes=5))

        with patch("app.routers.auth.settings.SECRET_KEY", "test-secret"):
            response = verify_otp(
                OTPVerify(email="example@example.com", otp="123456"),
                self.db,
            )
            with self.assertRaises(HTTPException):
                verify_otp(
                    OTPVerify(email="example@example.com", otp="123456"),
                    self.db,
                )

        self.assertEqual(response.status, "success")
        self.assertTrue(self.users.users[0]["is_verified"])
        self.assertIsNone(self.users.users[0]["otp_code"])

    @patch("app.routers.auth.get_password_hash", return_value="new-hash")
    def test_password_reset_consumes_otp_and_updates_password_atomically(
        self,
        _hash_password: Mock,
    ) -> None:
        self.store_otp("123456", datetime.now(timezone.utc) + timedelta(minutes=5))

        with patch("app.routers.auth.settings.SECRET_KEY", "test-secret"):
            response = reset_password(
                PasswordResetConfirm(
                    email="example@example.com",
                    otp="123456",
                    newPassword="new-password",
                ),
                self.db,
            )

        self.assertEqual(response.status, "success")
        self.assertEqual(self.users.users[0]["hashed_password"], "new-hash")
        self.assertIsNone(self.users.users[0]["otp_code"])

    @patch("app.routers.auth.get_password_hash")
    def test_password_reset_validates_otp_before_password_policy(
        self,
        hash_password: Mock,
    ) -> None:
        self.store_otp("123456", datetime.now(timezone.utc) + timedelta(minutes=5))

        with self.assertRaises(HTTPException) as error:
            reset_password(
                PasswordResetConfirm(
                    email="example@example.com",
                    otp="000000",
                    newPassword="short",
                ),
                self.db,
            )

        self.assertEqual(error.exception.detail, "Invalid or expired OTP code.")
        hash_password.assert_not_called()

    @patch("app.routers.auth._send_otp_email")
    @patch("app.routers.auth.get_password_hash", return_value="hashed-password")
    @patch("app.routers.auth.next_sequence", return_value=42)
    def test_signup_creates_unverified_user_and_sends_otp(
        self,
        _next_sequence: Mock,
        _hash_password: Mock,
        send_email: Mock,
    ) -> None:
        self.users.users.clear()

        response = signup(
            UserCreate(
                name="Example User",
                email="example@example.com",
                password="example-password",
            ),
            self.db,
        )

        created_user = self.users.users[0]
        self.assertFalse(created_user["is_verified"])
        self.assertTrue(response.otp_required)
        self.assertIsNone(response.demo_otp)
        send_email.assert_called_once()

    def test_unverified_user_cannot_log_in(self) -> None:
        self.users.users[0]["is_verified"] = False

        with patch("app.routers.auth.verify_password", return_value=True):
            with self.assertRaises(HTTPException) as error:
                login(
                    UserLogin(email="example@example.com", password="password"),
                    self.db,
                )

        self.assertEqual(error.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
