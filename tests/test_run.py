import os
import runpy
import unittest
from pathlib import Path
from unittest.mock import patch


RUN_SCRIPT = Path(__file__).resolve().parents[1] / "run.py"


class RunTests(unittest.TestCase):
    @patch("app.seed.seed_database")
    @patch("uvicorn.run")
    def test_uses_render_port_without_seeding_by_default(
        self, run_server, seed_database
    ) -> None:
        with patch.dict(os.environ, {"PORT": "10000", "SEED_DATABASE": "false"}):
            runpy.run_path(str(RUN_SCRIPT), run_name="__main__")

        run_server.assert_called_once_with(
            "app.main:app", host="0.0.0.0", port=10000, reload=False
        )
        seed_database.assert_not_called()

    @patch("app.seed.seed_database")
    @patch("uvicorn.run")
    def test_defaults_to_port_8000(self, run_server, seed_database) -> None:
        with patch.dict(os.environ, {"SEED_DATABASE": ""}):
            os.environ.pop("PORT", None)
            runpy.run_path(str(RUN_SCRIPT), run_name="__main__")

        run_server.assert_called_once_with(
            "app.main:app", host="0.0.0.0", port=8000, reload=False
        )
        seed_database.assert_not_called()


if __name__ == "__main__":
    unittest.main()
