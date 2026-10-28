#!/usr/bin/env python3
"""Choose a stable, isolated Compose project name for a Classroom test instance."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


def project_name(directory: Path, port: int) -> str:
    base = re.sub(r"[^a-z0-9_-]+", "", directory.name.lower()).lstrip("-_")
    if not base:
        base = "classroom"
    if port == 8888:
        # Keep the historical Compose project and named volumes for the default instance.
        return base[:63]
    path_hash = hashlib.sha256(str(directory.resolve()).encode()).hexdigest()[:10]
    suffix = f"-student-{port}-{path_hash}"
    return base[: 63 - len(suffix)] + suffix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("--directory", type=Path, default=Path.cwd())
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    print(project_name(args.directory, args.port))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
