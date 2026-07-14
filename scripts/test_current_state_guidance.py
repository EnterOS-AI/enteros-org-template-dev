from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from scripts import check_current_state_guidance


class CurrentStateGuidanceTests(unittest.TestCase):
    def run_check(self, root: Path) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = check_current_state_guidance.main(["--root", str(root)])
        return result, output.getvalue()

    def test_rejects_token_bearing_clone_url_without_disclosing_it(self) -> None:
        secret = "token-" + "A" * 48
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt = root / "role" / "initial-prompt.md"
            prompt.parent.mkdir(parents=True)
            prompt.write_text(
                "git clone https://x-access-token:"
                + secret
                + "@git.moleculesai.app/molecule-ai/internal.git\n",
                encoding="utf-8",
            )

            result, output = self.run_check(root)

        self.assertEqual(result, 1)
        self.assertIn("role/initial-prompt.md:1:userinfo embedded in a Git URL", output)
        self.assertNotIn(secret, output)
        self.assertNotIn(secret[:40], output)

    def test_rejects_unversioned_python_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            schedule = root / "role" / "schedules" / "audit.md"
            schedule.parent.mkdir(parents=True)
            schedule.write_text("Run: python -m unittest\n", encoding="utf-8")

            result, output = self.run_check(root)

        self.assertEqual(result, 1)
        self.assertIn(
            "role/schedules/audit.md:1:unversioned local Python command",
            output,
        )

    def test_accepts_credential_free_clone_and_python3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt = root / "role" / "initial-prompt.md"
            prompt.parent.mkdir(parents=True)
            prompt.write_text(
                "git clone https://git.moleculesai.app/molecule-ai/internal.git\n"
                "python3 -m unittest\n",
                encoding="utf-8",
            )

            result, output = self.run_check(root)

        self.assertEqual(result, 0)
        self.assertIn("Current-state guidance check passed", output)

    def test_rejects_undelivered_role_names_in_active_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt = root / "role" / "system-prompt.md"
            prompt.parent.mkdir(parents=True)
            prompt.write_text(
                "Route technical-writer work to app-docs-lead.\n"
                "Ask research-analyst for a brief.\n",
                encoding="utf-8",
            )

            result, output = self.run_check(root)

        self.assertEqual(result, 1)
        self.assertIn("role/system-prompt.md:1:undelivered active role name", output)
        self.assertIn("role/system-prompt.md:2:undelivered active role name", output)

    def test_allows_undelivered_role_name_in_historical_comment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            team = root / "teams" / "pm.yaml"
            team.parent.mkdir(parents=True)
            team.write_text(
                "# documentation-specialist moved into the external dev tree.\n",
                encoding="utf-8",
            )

            result, output = self.run_check(root)

        self.assertEqual(result, 0)
        self.assertIn("Current-state guidance check passed", output)


if __name__ == "__main__":
    unittest.main()
