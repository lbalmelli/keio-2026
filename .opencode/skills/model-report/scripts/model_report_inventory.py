#!/usr/bin/env python3
"""Constrained, source-only SysML inventory for model-report.

This is deliberately not a full SysML parser. It recognizes the declaration
forms used in course models, balances scopes, ignores ordinary comments and
strings, and associates only explicit ``doc /* ... */`` blocks with elements.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


TOKEN_RE = re.compile(
    r"(?P<space>\s+)"
    r"|(?P<linecomment>//[^\n]*)"
    r"|(?P<blockcomment>/\*.*?\*/)"
    r"|(?P<string>\"(?:\\.|[^\"\\])*\")"
    r"|(?P<id>[A-Za-z_$][\w$]*)"
    r"|(?P<symbol>::|\*\*|->|\|>|[^\s])",
    re.DOTALL,
)

ASPECT_KINDS = {
    "requirements": {"requirement"},
    "structure": {"part", "port", "connection", "interface", "item", "attribute"},
    "behavior": {"action", "state", "transition", "flow", "succession", "event"},
}
DECLARATION_KINDS = set().union(*ASPECT_KINDS.values()) | {"package", "view", "dependency"}


@dataclass(frozen=True)
class Token:
    value: str
    line: int
    offset: int
    block_comment: bool = False
    string: bool = False


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    for match in TOKEN_RE.finditer(text):
        kind = match.lastgroup
        if kind in {"space", "linecomment"}:
            continue
        prefix = text[: match.start()]
        tokens.append(Token(match.group(), prefix.count("\n") + 1, match.start(), kind == "blockcomment", kind == "string"))
    return tokens


def inventory_text(text: str, source: str = "<memory>") -> dict:
    tokens = tokenize(text)
    declarations: list[dict] = []
    package_stack: list[tuple[str, int]] = []
    brace_stack: list[tuple[str | None, int]] = []

    # Pair scopes before inspecting declarations.
    matching: dict[int, int] = {}
    stack: list[int] = []
    for i, token in enumerate(tokens):
        if token.value == "{":
            stack.append(i)
        elif token.value == "}" and stack:
            left = stack.pop()
            matching[left] = i

    # Explicit imports are reported as evidence for agent-led dependency resolution.
    imports: list[dict] = []
    for i, token in enumerate(tokens):
        if token.value == "import" and i + 1 < len(tokens):
            end = i + 1
            while end < len(tokens) and tokens[end].value != ";":
                end += 1
            imports.append({"line": token.line, "text": "".join(t.value for t in tokens[i + 1 : end])})

    for i, token in enumerate(tokens):
        if token.value not in DECLARATION_KINDS:
            continue
        kind = token.value
        name_i = i + 1
        if kind in {"part", "requirement", "action", "attribute", "port", "item", "state", "connection", "flow", "interface"} and name_i < len(tokens) and tokens[name_i].value in {"def", "usage"}:
            name_i += 1
        if name_i >= len(tokens) or not re.match(r"^[A-Za-z_$][\w$]*$", tokens[name_i].value):
            continue
        name = tokens[name_i].value
        # The preceding package scopes determine a qualified name. Their spans are balanced.
        containers = []
        for prior in declarations:
            if prior["kind"] == "package" and prior.get("_open", -1) < i < prior.get("_close", -1):
                containers.append(prior["qualified_name"])
        qname = "::".join([*containers, name]) if containers else name
        open_i = next((j for j in range(name_i + 1, min(len(tokens), name_i + 16)) if tokens[j].value in {"{", ";"}), None)
        close_i = matching.get(open_i, open_i) if open_i is not None else name_i

        doc_blocks: list[str] = []
        exposes: list[str] = []
        # Only doc blocks in this declaration's own balanced body are associated.
        if open_i is not None and tokens[open_i].value == "{" and close_i is not None:
            depth = 0
            for j in range(open_i + 1, close_i):
                if tokens[j].value == "{":
                    depth += 1
                elif tokens[j].value == "}":
                    depth -= 1
                if depth == 0 and tokens[j].value == "doc" and j + 1 < close_i and tokens[j + 1].block_comment:
                    raw = tokens[j + 1].value[2:-2].strip()
                    doc_blocks.append(" ".join(raw.split()))
                if kind == "view" and depth == 0 and tokens[j].value == "expose":
                    k = j + 1
                    expose = []
                    while k < close_i and tokens[k].value != ";":
                        expose.append(tokens[k].value)
                        k += 1
                    exposes.append("".join(expose))
        line_end = tokens[close_i].line if close_i is not None else token.line
        item = {
            "qualified_name": qname,
            "kind": kind,
            "source": source,
            "line": token.line,
            "end_line": line_end,
            "doc": doc_blocks,
        }
        if kind == "view":
            item["exposes"] = exposes
        if kind == "dependency":
            end = next((j for j in range(name_i + 1, len(tokens)) if tokens[j].value == ";"), len(tokens))
            clause = " ".join(t.value for t in tokens[name_i + 1 : end])
            item["relationship"] = clause
        item["_open"] = open_i if open_i is not None and tokens[open_i].value == "{" else -1
        item["_close"] = close_i if open_i is not None and tokens[open_i].value == "{" else -1
        declarations.append(item)

    # Package declarations establish containment, but are not evidence for aspects.
    aspects = {
        aspect: any(d["kind"] in kinds for d in declarations)
        for aspect, kinds in ASPECT_KINDS.items()
    }
    for declaration in declarations:
        declaration.pop("_open", None)
        declaration.pop("_close", None)
        if declaration["kind"] in set().union(*ASPECT_KINDS.values()) and not declaration["doc"]:
            declaration["documentation_status"] = "undocumented"
        elif declaration["doc"]:
            declaration["documentation_status"] = "documented"
    return {"source": source, "aspects": aspects, "imports": imports, "declarations": declarations}


def discover_models(root: Path) -> list[Path]:
    """List ordinary model files under root; do not follow symlinks or hidden dirs."""
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"model workspace is not a directory: {root}")
    paths: list[Path] = []
    for path in root.rglob("*.sysml"):
        relative = path.relative_to(root)
        if path.is_symlink() or any(part.startswith(".") for part in relative.parts):
            continue
        if path.is_file():
            paths.append(path)
    return sorted(paths, key=lambda p: p.relative_to(root).as_posix().casefold())


def inspect_files(paths: list[Path]) -> dict:
    return {"files": [inventory_text(path.read_text(encoding="utf-8"), str(path)) for path in paths]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="confirmed .sysml source files to inventory")
    args = parser.parse_args(argv)
    files = []
    for raw in args.paths:
        path = Path(raw)
        if path.suffix != ".sysml" or not path.is_file():
            parser.error(f"not an existing .sysml file: {raw}")
        files.append(path)
    print(json.dumps(inspect_files(files), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
