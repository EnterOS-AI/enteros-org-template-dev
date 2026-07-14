#!/usr/bin/env python3
"""Compatibility entry point for the repository's non-disclosing scanner."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.check_no_secrets import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
