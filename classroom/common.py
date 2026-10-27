"""Shared validation and immutable workspace inventory for the Classroom Bridge."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path, PurePosixPath

CATEGORIES = ('models', 'notebooks', 'reports')
DENY_SUFFIXES = ('.chat', '.env', '.zip', '.tar', '.gz', '.7z', '.rar', '.tgz', '.bz2', '.xz', '.zst', '.pem', '.key')
SENSITIVE_PREFIXES = ('credential','secret','token','api_key','apikey','id_rsa','id_ed25519','auth.json','opencode.json')
DENY_NAMES = {'.git', '.ipynb_checkpoints', '__pycache__', 'node_modules', 'samples'}


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(canonical_json(value)).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    p = PurePosixPath(relative)
    if p.is_absolute() or not p.parts or p.parts[0] not in CATEGORIES or any(x in ('..', '.') or x.startswith('.') or x in DENY_NAMES for x in p.parts):
        raise ValueError('disallowed path')
    if p.suffix.lower() in DENY_SUFFIXES or p.name.startswith('.env') or any(p.name.lower().startswith(prefix) for prefix in SENSITIVE_PREFIXES):
        raise ValueError('disallowed file')
    target = root.joinpath(*p.parts)
    if target.is_symlink() or any(parent.is_symlink() for parent in list(target.parents)[:-1] if parent != root.parent):
        raise ValueError('symlink')
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('path escape')
    return target


def inventory(root: Path, categories=CATEGORIES, selected=None, max_file=50*1024*1024, max_total=500*1024*1024):
    if not set(categories).issubset(CATEGORIES):
        raise ValueError('category')
    selected = set(selected) if selected is not None else None
    entries = []
    for category in categories:
        base = root / category
        if not base.exists():
            continue
        for folder, dirs, files in os.walk(base, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith('.') and d not in DENY_NAMES and not (Path(folder)/d).is_symlink())
            for name in sorted(files):
                relative = (Path(folder)/name).relative_to(root).as_posix()
                if selected is not None and relative not in selected:
                    continue
                try:
                    path = safe_path(root, relative)
                except ValueError:
                    continue
                if not path.is_file() or path.is_symlink():
                    continue
                stat = path.stat()
                if stat.st_size > max_file:
                    raise ValueError(f'file too large: {relative}')
                h = hashlib.sha256()
                with path.open('rb') as stream:
                    for block in iter(lambda: stream.read(1024*1024), b''):
                        h.update(block)
                entries.append({'path': relative, 'type': 'file', 'size': stat.st_size, 'sha256': h.hexdigest()})
    entries.sort(key=lambda x: x['path'])
    if selected is not None and selected != {e['path'] for e in entries}:
        raise ValueError('selected file unavailable or disallowed')
    if sum(e['size'] for e in entries) > max_total:
        raise ValueError('workspace too large')
    return entries
