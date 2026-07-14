from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import check_no_secrets


class SecretScannerTests(unittest.TestCase):
    def run_scan(self, root: Path) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = check_no_secrets.main(["--root", str(root)])
        return result, output.getvalue()

    def test_reports_rule_and_location_without_disclosing_match(self) -> None:
        secret = "sk-ant-" + "A" * 60
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".gitea" / "workflows" / "ci.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(f"token: '{secret}'\n", encoding="utf-8")

            result, output = self.run_scan(root)

        self.assertEqual(result, 1)
        self.assertIn(".gitea/workflows/ci.yml:1:anthropic_api_key", output)
        self.assertNotIn(secret, output)
        self.assertNotIn(secret[:40], output)

    def test_scans_compound_env_example_names(self) -> None:
        secret = "ghp_" + "B" * 36
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_example = root / "role" / "service.env.example"
            env_example.parent.mkdir(parents=True)
            env_example.write_text(f"SCM_TOKEN={secret}\n", encoding="utf-8")

            result, output = self.run_scan(root)

        self.assertEqual(result, 1)
        self.assertIn("role/service.env.example:1:github_token", output)
        self.assertNotIn(secret, output)

    def test_scans_active_scripts(self) -> None:
        secret = "Bearer " + "C" * 32
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "scripts" / "deploy.sh"
            script.parent.mkdir(parents=True)
            script.write_text(f"header='{secret}'\n", encoding="utf-8")

            result, output = self.run_scan(root)

        self.assertEqual(result, 1)
        self.assertIn("scripts/deploy.sh:1:bearer_token", output)
        self.assertNotIn(secret, output)

    def test_compatibility_entry_point_is_non_disclosing(self) -> None:
        secret = "sk-ant-" + "D" * 60
        entry_point = (
            Path(__file__).resolve().parents[1]
            / ".molecule-ci"
            / "scripts"
            / "check-secrets.py"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".gitea" / "workflows" / "ci.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(f"token: '{secret}'\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(entry_point), "--root", str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

        output = completed.stdout + completed.stderr
        self.assertEqual(completed.returncode, 1)
        self.assertIn(".gitea/workflows/ci.yml:1:anthropic_api_key", output)
        self.assertNotIn(secret, output)
        self.assertNotIn(secret[:40], output)

    def test_documented_placeholders_are_not_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_example = root / "role" / ".env.example"
            env_example.parent.mkdir(parents=True)
            env_example.write_text(
                "CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...\n",
                encoding="utf-8",
            )

            result, output = self.run_scan(root)

        self.assertEqual(result, 0)
        self.assertIn("No secrets detected", output)


if __name__ == "__main__":
    unittest.main()
