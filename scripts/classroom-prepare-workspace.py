#!/usr/bin/env python3
"""Create standard student workspace folders before Jupyter startup."""

from __future__ import annotations

import os
from pathlib import Path


def main() -> int:
    workspace = Path(os.environ.get("JUPYTER_WORKSPACE", "./workspace")).expanduser()
    for name in ("models", "notebooks", "samples", "reports"):
        (workspace / name).mkdir(parents=True, exist_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
