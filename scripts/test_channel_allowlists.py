from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from scripts import check_channel_allowlists


class ChannelAllowlistTests(unittest.TestCase):
    def run_check(self, yaml_text: str) -> tuple[int, str]:
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "role" / "workspace.yaml"
            config.parent.mkdir(parents=True)
            config.write_text(yaml_text, encoding="utf-8")
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                result = check_channel_allowlists.main(["--root", str(root)])
        return result, output.getvalue()

    def test_rejects_enabled_channel_without_allowlist(self) -> None:
        result, output = self.run_check("channels:\n  - type: telegram\n")

        self.assertEqual(result, 1)
        self.assertIn("enabled_without_literal_allowed_users", output)

    def test_rejects_enabled_channel_with_empty_allowlist(self) -> None:
        result, _ = self.run_check(
            "channels:\n  - type: discord\n    allowed_users: []\n    enabled: true\n"
        )

        self.assertEqual(result, 1)

    def test_rejects_environment_reference_in_allowlist(self) -> None:
        result, output = self.run_check(
            "channels:\n"
            "  - type: telegram\n"
            "    allowed_users: ['${TELEGRAM_USER_ID}']\n"
            "    enabled: true\n"
        )

        self.assertEqual(result, 1)
        self.assertNotIn("TELEGRAM_USER_ID", output)

    def test_accepts_disabled_channel_without_allowlist(self) -> None:
        result, output = self.run_check(
            "channels:\n  - type: telegram\n    enabled: false\n"
        )

        self.assertEqual(result, 0)
        self.assertIn("Channel allowlist check passed", output)

    def test_accepts_enabled_channel_with_literal_allowlist(self) -> None:
        result, output = self.run_check(
            "channels:\n"
            "  - type: discord\n"
            "    allowed_users: ['123456789']\n"
            "    enabled: true\n"
        )

        self.assertEqual(result, 0)
        self.assertIn("Channel allowlist check passed", output)

    def test_ignores_non_channel_category_named_channels(self) -> None:
        result, output = self.run_check(
            "defaults:\n  category_routing:\n    channels: [DevOps Engineer]\n"
        )

        self.assertEqual(result, 0)
        self.assertIn("Channel allowlist check passed", output)

    def test_ignores_non_template_workflow_yaml(self) -> None:
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".gitea" / "workflows" / "ci.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("run: ${{ not-template-yaml }}\n", encoding="utf-8")
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                result = check_channel_allowlists.main(["--root", str(root)])

        self.assertEqual(result, 0)
        self.assertIn("Channel allowlist check passed", output.getvalue())


if __name__ == "__main__":
    unittest.main()
