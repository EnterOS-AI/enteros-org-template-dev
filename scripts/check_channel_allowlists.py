#!/usr/bin/env python3
"""Reject fail-open enabled native channels in template YAML."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterator, Sequence

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".molecule-ci-canonical", "__pycache__", "node_modules"}
ENV_REF = re.compile(r"\$\{[^}]+\}")


class PermissiveLoader(yaml.SafeLoader):
    pass


def _generic_constructor(loader: PermissiveLoader, _suffix: str, node: yaml.Node):
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_scalar(node)


PermissiveLoader.add_multi_constructor("!", _generic_constructor)


def iter_yaml_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in {".yaml", ".yml"}
        and not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
        and (
            path.name in {"org.yaml", "workspace.yaml"}
            or path.relative_to(root).parts[0] == "teams"
        )
    )


def iter_channels(node: object) -> Iterator[dict[str, object]]:
    if isinstance(node, dict):
        channels = node.get("channels")
        if isinstance(channels, list):
            for channel in channels:
                if isinstance(channel, dict) and "type" in channel:
                    yield channel
        for value in node.values():
            yield from iter_channels(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_channels(value)


def has_literal_allowlist(channel: dict[str, object]) -> bool:
    allowed = channel.get("allowed_users")
    return (
        isinstance(allowed, list)
        and bool(allowed)
        and all(
            isinstance(user, str)
            and bool(user.strip())
            and ENV_REF.search(user) is None
            for user in allowed
        )
    )


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path in iter_yaml_files(root):
        relative = path.relative_to(root).as_posix()
        try:
            document = yaml.load(path.read_text(encoding="utf-8"), Loader=PermissiveLoader)
        except (OSError, UnicodeError, yaml.YAMLError):
            findings.append(f"{relative}:yaml_parse_error")
            continue

        for index, channel in enumerate(iter_channels(document), 1):
            if channel.get("enabled", True) is False:
                continue
            channel_type = channel.get("type", "unknown")
            if not has_literal_allowlist(channel):
                findings.append(
                    f"{relative}:channel[{index}]:{channel_type}:"
                    "enabled_without_literal_allowed_users"
                )
    return findings


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    findings = scan(args.root.resolve())
    if findings:
        print("Channel allowlist check failed:", file=sys.stderr)
        for finding in findings:
            print(f"  {finding}", file=sys.stderr)
        return 1

    print("Channel allowlist check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
