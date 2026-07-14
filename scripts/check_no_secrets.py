#!/usr/bin/env python3
"""Find committed secret material without echoing matched values."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".json", ".md", ".py", ".sh", ".toml", ".yaml", ".yml"}
COMPOUND_TEXT_SUFFIXES = (".env.example",)
SKIP_DIRS = {
    ".git",
    ".molecule-ci-canonical",
    "__pycache__",
    "node_modules",
}

RULES = {
    "anthropic_api_key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{32,}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "openai_api_key": re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{32,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "stripe_secret_key": re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{24,}\b"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9_.-]{20,}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "quoted_high_entropy_value": re.compile(r'''["'][A-Za-z0-9/+_=.-]{40,}["']'''),
}


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    rule: str


def is_text_candidate(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name.endswith(COMPOUND_TEXT_SUFFIXES)


def iter_text_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and is_text_candidate(path)
        and not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
    )


def scan(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_text_files(root):
        relative = path.relative_to(root).as_posix()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            findings.append(Finding(relative, 0, "unreadable_text_file"))
            continue

        for line_number, line in enumerate(lines, 1):
            for rule, pattern in RULES.items():
                if pattern.search(line):
                    findings.append(Finding(relative, line_number, rule))

    return sorted(set(findings))


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    findings = scan(args.root.resolve())
    if findings:
        print("Potential secret material found:", file=sys.stderr)
        for finding in findings:
            print(
                f"  {finding.path}:{finding.line}:{finding.rule}",
                file=sys.stderr,
            )
        return 1

    print("No secrets detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
