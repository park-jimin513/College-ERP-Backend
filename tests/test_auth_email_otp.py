import unittest
from datetime import datetime, timedelta, timezone
from smtplib import SMTPException
from unittest.mock import Mock, patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.routers.auth import get_current_user, login, send_otp, signup, verify_otp
from app.schemas.user import OTPRequest, OTPVerify, UserCreate, UserLogin


class AuthEmailOtpTests(unittest.TestCase):
    @patch("app.routers.auth._find_user")
    @patch("app.routers.auth.jwt.decode", return_value={"sub": "registered@example.com"})
    def test_current_user_returns_only_the_authenticated_users_registration_details(
        self,
        decode_token: Mock,
        find_user: Mock,
    ) -> None:
        registered_user = {
            "id": 12,
            "name": "Registered User",
            "email": "registered@example.com",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }
        find_user.return_value = registered_user

        response = get_current_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token"),
            Mock(),
        )

        self.assertEqual(response.name, "Registered User")
        self.assertEqual(response.email, "registered@example.com")
        decode_token.assert_called_once()
        find_user.assert_called_once()

    def test_current_user_rejects_missing_bearer_token(self) -> None:
        with self.assertRaises(HTTPException) as error:
            get_current_user(None, Mock())

        self.assertEqual(error.exception.status_code, 401)

    @patch("app.routers.auth._send_otp_email")
    @patch("app.routers.auth.get_password_hash", return_value="hashed-password")
    @patch("app.routers.auth.next_sequence", return_value=42)
    @patch("app.routers.auth.mongo_collection")
    def test_signup_creates_unverified_user_and_sends_otp(
        self,
        get_collection: Mock,
        next_sequence: Mock,
        hash_password: Mock,
        send_email: Mock,
    ) -> None:
        users = Mock()
        users.find_one.return_value = None
        get_collection.return_value = users

        response = signup(
            UserCreate(
                name="Example User",
                email="example@example.com",
                password="secure-password",
            ),
            Mock(),
        )

        created_user = users.insert_one.call_args.args[0]
        self.assertFalse(created_user["is_verified"])
        self.assertTrue(response.otp_required)
        self.assertIsNone(response.demo_otp)
        send_email.assert_called_once()
        self.assertEqual(send_email.call_args.args[0], "example@example.com")

    @patch(
        "app.routers.auth._send_otp_email",
        side_effect=SMTPException("delivery failed"),
    )
    @patch("app.routers.auth.mongo_collection")
    def test_failed_delivery_invalidates_otp_and_does_not_return_code(
        self,
        get_collection: Mock,
        send_email: Mock,
    ) -> None:
        users = Mock()
        users.find_one.return_value = {"_id": "user-1", "email": "example@example.com"}
        get_collection.return_value = users

        with self.assertRaises(HTTPException) as error:
            send_otp(OTPRequest(email="example@example.com"), Mock())

        self.assertEqual(error.exception.status_code, 503)
        invalidation = users.update_one.call_args_list[-1].args[1]["$set"]
        self.assertIsNone(invalidation["otp_code"])
        self.assertIsNone(invalidation["otp_expires_at"])
        send_email.assert_called_once()
        users.delete_one.assert_not_called()

    @patch("app.routers.auth.mongo_collection")
    def test_verifying_otp_marks_the_user_verified(
        self,
        get_collection: Mock,
    ) -> None:
        users = Mock()
        users.find_one.return_value = {
            "_id": "user-1",
            "email": "example@example.com",
            "otp_code": "123456",
            "otp_expires_at": datetime.now(timezone.utc) + timedelta(minutes=5),
        }
        get_collection.return_value = users

        response = verify_otp(
            OTPVerify(email="example@example.com", otp="123456"),
            Mock(),
        )

        update = users.update_one.call_args.args[1]["$set"]
        self.assertTrue(update["is_verified"])
        self.assertIsNone(update["otp_code"])
        self.assertEqual(response.status, "success")

    @patch("app.routers.auth.mongo_collection")
    def test_unverified_user_cannot_log_in(
        self,
        get_collection: Mock,
    ) -> None:
        users = Mock()
        users.find_one.return_value = {
            "_id": "user-1",
            "email": "example@example.com",
            "is_active": True,
            "is_verified": False,
        }
        get_collection.return_value = users

        with self.assertRaises(HTTPException) as error:
            login(
                UserLogin(email="example@example.com", password="secure-password"),
                Mock(),
            )

        self.assertEqual(error.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
