from __future__ import annotations

import re
import subprocess
import unittest
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADVERTISED = re.compile(r"\b(?:copy[- ]?paste|executable)\b", re.IGNORECASE)
FENCE = re.compile(r"^```(?:bash|sh|shell)\s*$", re.IGNORECASE)
PLACEHOLDER = re.compile(r"<[A-Za-z][^>\n]*>")


@dataclass(frozen=True)
class ShellBlock:
    path: Path
    line: int
    body: str


def advertised_shell_blocks(path: Path) -> list[ShellBlock]:
    lines = path.read_text(encoding="utf-8").splitlines()
    heading = ""
    blocks: list[ShellBlock] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        if line.startswith("#"):
            heading = line
        if not FENCE.fullmatch(line):
            index += 1
            continue

        start = index + 1
        context = "\n".join((heading, *lines[max(0, index - 3) : index]))
        index += 1
        body: list[str] = []
        while index < len(lines) and lines[index] != "```":
            body.append(lines[index])
            index += 1
        if ADVERTISED.search(context):
            blocks.append(ShellBlock(path.relative_to(ROOT), start + 1, "\n".join(body) + "\n"))
        index += 1

    return blocks


class ExecutableShellBlockTests(unittest.TestCase):
    def test_advertised_shell_blocks_are_executable(self) -> None:
        expected_paths = {
            Path("SHARED_RULES.md"),
            Path("community-manager/system-prompt.md"),
            Path("competitive-intelligence") / "system-prompt.md",
            Path("content-marketer/system-prompt.md"),
            Path("market-analyst/system-prompt.md"),
            Path("marketing-lead/system-prompt.md"),
            Path("product-marketing-manager") / "system-prompt.md",
            Path("research-lead/system-prompt.md"),
            Path("social-media-brand/system-prompt.md"),
        }
        blocks = [
            block
            for path in ROOT.rglob("*.md")
            if ".git" not in path.parts
            for block in advertised_shell_blocks(path)
        ]
        discovered_paths = {block.path for block in blocks}
        self.assertEqual(
            expected_paths - discovered_paths,
            set(),
            "all nine reviewed copy-paste blocks must remain covered",
        )

        errors: list[str] = []
        for block in blocks:
            placeholders = PLACEHOLDER.findall(block.body)
            if placeholders:
                errors.append(
                    f"{block.path}:{block.line}: literal placeholders: "
                    + ", ".join(sorted(set(placeholders)))
                )
            result = subprocess.run(
                ["bash", "-n"],
                input=block.body,
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode:
                errors.append(f"{block.path}:{block.line}: {result.stderr.strip()}")

        self.assertEqual(errors, [], "\n" + "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
