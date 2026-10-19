import unittest

from fastapi.testclient import TestClient

from app.main import app


class CorsTests(unittest.TestCase):
    def test_vite_origins_receive_cors_preflight_headers(self) -> None:
        client = TestClient(app)
        for origin in (
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ):
            with self.subTest(origin=origin):
                response = client.options(
                    "/api/teaching-staff",
                    headers={
                        "Origin": origin,
                        "Access-Control-Request-Method": "GET",
                    },
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.headers["access-control-allow-origin"],
                    origin,
                )

    def test_unconfigured_origin_does_not_receive_cors_permission(self) -> None:
        client = TestClient(app)
        response = client.options(
            "/api/teaching-staff",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertNotIn("access-control-allow-origin", response.headers)


if __name__ == "__main__":
    unittest.main()
