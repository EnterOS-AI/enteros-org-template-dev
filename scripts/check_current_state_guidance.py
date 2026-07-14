#!/usr/bin/env python3
"""Reject operational guidance that is known to be retired or unsafe."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
TEXT_SUFFIXES = {".md", ".yaml", ".yml"}
SKIP_DIRS = {".git", ".molecule-ci-canonical", "__pycache__", "node_modules"}

FORBIDDEN = {
    "suspended GitHub-org installer": re.compile(r"github://Molecule-AI", re.IGNORECASE),
    "userinfo embedded in a Git URL": re.compile(
        r"https?://[^/\s@]+@git\.moleculesai\.app",
        re.IGNORECASE,
    ),
    "legacy GH_TOKEN name": re.compile(r"\bGH_TOKEN\b"),
    "unavailable tea CLI instruction": re.compile(r"\btea\b"),
    "credential-bearing API header": re.compile(
        r"Authorization:\s*token\s+\$\{GITEA_TOKEN\}", re.IGNORECASE
    ),
    "unversioned local Python command": re.compile(
        r"(?<![\w-])python\s+(?:-c|-m|-|[A-Za-z0-9_./])"
    ),
    "unavailable jq command": re.compile(r"\bjq\b"),
    "non-fast-forward-safe Git pull": re.compile(r"\bgit\s+pull\s+(?!--ff-only\b)"),
    "legacy GH issue/PR instruction": re.compile(
        r"\bGH (?:Discussions?|Issues?|PRs?|review|merged)\b", re.IGNORECASE
    ),
    "legacy GitHub issue/PR instruction": re.compile(
        r"\bGitHub (?:Issues?|PRs?|pull requests?|App identity|App installation token)\b",
        re.IGNORECASE,
    ),
    "retired public monorepo": re.compile(r"\bmolecule-monorepo\b", re.IGNORECASE),
    "noncanonical Gitea organization slug": re.compile(r"Molecule-AI/"),
    "retired cloud-service claim": re.compile(
        r"\b(?:Vercel|Railway|GHCR|Upptime|FLY_API_TOKEN|VERCEL_TOKEN)\b",
        re.IGNORECASE,
    ),
    "retired AWS ECR image claim": re.compile(r"\bAWS ECR\b", re.IGNORECASE),
    "stale fixed repository count": re.compile(r"\b40\+\s+repos\b", re.IGNORECASE),
    "single-page repository inventory": re.compile(r"[?&]limit=60\b"),
    "nonexistent fixed CLAUDE.md path": re.compile(
        r"/workspace/(?:repos/molecule-core|repo)/CLAUDE\.md"
    ),
    "obsolete universal staging policy": re.compile(
        r"(?:## Staging-First Workflow|All feature branches target `staging`|"
        r"Branch from `staging`)",
        re.IGNORECASE,
    ),
    "obsolete Gitea 1.22.6 rationale": re.compile(r"Gitea 1\.22\.6", re.IGNORECASE),
    "obsolete GitHub Actions workflow path": re.compile(r"\.github/workflows"),
    "retired public content path": re.compile(
        r"\bdocs/(?:blog|marketing|community)/", re.IGNORECASE
    ),
    "retired core-monolith path": re.compile(
        r"\b(?:workspace-template/builtin_tools|org-templates/molecule-dev|"
        r"workspace-template/agents_md\.py)\b",
        re.IGNORECASE,
    ),
    "retired monolith directory shorthand": re.compile(
        r"\b(?:plugins|workspace-template)/", re.IGNORECASE
    ),
    "unconfigured Slack instruction": re.compile(r"\bSlack\b", re.IGNORECASE),
    "unconfigured named channel": re.compile(r"#(?:ceo-feed|ops|engineering)\b"),
    "hard-coded platform service URL": re.compile(
        r"http://(?:host\.docker\.internal|platform):8080", re.IGNORECASE
    ),
    "unconfigured molecule-hitl tool": re.compile(r"\bmolecule-hitl\b"),
}
UNDELIVERED_ROLE = re.compile(
    r"\b(?:technical-writer|documentation-specialist|"
    r"app-docs-lead|research-analyst)\b",
    re.IGNORECASE,
)
HISTORICAL_COMMENT = re.compile(
    r"\b(?:former|historical|legacy|moved|orphan(?:ed)?|removed|retired)\b",
    re.IGNORECASE,
)


def is_clearly_historical_comment(line: str) -> bool:
    return line.lstrip().startswith("#") and HISTORICAL_COMMENT.search(line) is not None


def iter_guidance_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.resolve() != SELF
        and (path.suffix in TEXT_SUFFIXES or path.name.endswith(".env.example"))
        and not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
    )


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path in iter_guidance_files(root):
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            findings.append(f"{relative}:0:unreadable guidance file")
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            if UNDELIVERED_ROLE.search(line) and not is_clearly_historical_comment(line):
                findings.append(
                    f"{relative}:{line_number}:undelivered active role name"
                )
            for label, pattern in FORBIDDEN.items():
                if pattern.search(line):
                    findings.append(f"{relative}:{line_number}:{label}")
    return findings


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    findings = scan(args.root.resolve())

    if findings:
        print("Current-state guidance check failed:", file=sys.stderr)
        print("\n".join(f"  {finding}" for finding in findings), file=sys.stderr)
        return 1

    print("Current-state guidance check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
