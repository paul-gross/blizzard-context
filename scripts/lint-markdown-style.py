#!/usr/bin/env python3
"""Markdown style lint contribution for `winter lint`.

Runs the three repo-local markdown style gates — `dprint check` (format, per
`dprint.json`), `rumdl check` (structural lint, per `.rumdl.toml`), and
`vale --output=line` (prose, per `.vale.ini`) — over every scoped repo that
carries the corresponding config file, and re-emits their results as NDJSON
lint findings. A repo without any of the three configs is silently out of
scope: the configs are the opt-in, so a wider rollout needs only to commit
them.

This is a `winter lint` check (see winter-cli `configuration/lint.md`). It is
wired in via the `lint` field of this module's `winter-ext.toml`, confines
itself to `WINTER_LINT_PATHS`, and always exits 0 — a violation is a finding,
not a process failure. A missing tool binary degrades to a single `warn` per
repo rather than a `fail`, so a machine without the tools sees the gap named
without the whole lint run going red.

Env contract (from `winter lint`):
  WINTER_WORKSPACE_DIR  absolute workspace root (findings are relativized to it)
  WINTER_LINT_PATHS     newline-delimited absolute paths in scope (files or dirs)
  WINTER_LINT_SCOPE     scope kind (all/repo/env/changed) — informational

Standalone (for the test harness): pass scope paths as argv.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

DPRINT_CONFIG = "dprint.json"
RUMDL_CONFIG = ".rumdl.toml"
VALE_CONFIG = ".vale.ini"
CONFIG_MARKERS = (DPRINT_CONFIG, RUMDL_CONFIG, VALE_CONFIG)

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
# rumdl text format: <path>:<line>:<col>: [MD013] message [*]
RUMDL_LINE_RE = re.compile(r"^(?P<path>.+?):(?P<line>\d+):\d+: (?P<msg>\[MD\d+\] .*?)(?: \[\*\])?$")
# dprint check names each unformatted file as: from /abs/path:
DPRINT_FROM_RE = re.compile(r"^from (?P<path>.+):$")
# vale --output=line format: <path>:<line>:<col>:<Style.Rule>:<message>
VALE_LINE_RE = re.compile(r"^(?P<path>.+?):(?P<line>\d+):\d+:(?P<rule>[^:]+):(?P<msg>.*)$")


def emit(check: str, status: str, message: str, *, file: str | None = None, line: int | None = None, remediation: str | None = None) -> None:
    payload: dict[str, object] = {"check": check, "status": status, "message": message}
    if file is not None:
        payload["file"] = file
    if line is not None:
        payload["line"] = line
    if remediation is not None:
        payload["remediation"] = remediation
    print(json.dumps(payload))


def scope_paths() -> list[Path]:
    if len(sys.argv) > 1:
        return [Path(p) for p in sys.argv[1:]]
    raw = os.environ.get("WINTER_LINT_PATHS", "")
    return [Path(p) for p in raw.splitlines() if p.strip()]


def owning_root(md_file: Path) -> Path | None:
    """Nearest ancestor carrying any tool config — the repo the file belongs to.

    Assumes a repo's markers all sit at its one true root, as the opt-in
    convention intends; a marker committed nested under an ancestor that also
    carries markers would shadow the ancestor's coverage for files below it.
    """
    for parent in md_file.parents:
        if any((parent / marker).is_file() for marker in CONFIG_MARKERS):
            return parent
    return None


def group_scope(paths: list[Path]) -> dict[Path, list[Path] | None]:
    """Map each governed repo root to the scoped .md files under it.

    `None` means the whole repo is in scope (a directory root was handed in);
    a list means only those files are (the `changed` scope hands files).
    """
    groups: dict[Path, list[Path] | None] = {}
    for path in paths:
        if path.is_dir():
            if any((path / marker).is_file() for marker in CONFIG_MARKERS):
                groups[path.resolve()] = None
        elif path.suffix == ".md" and path.is_file():
            root = owning_root(path.resolve())
            if root is None:
                continue
            existing = groups.setdefault(root, [])
            if existing is not None:
                existing.append(path.resolve())
    return groups


def run_tool(argv: list[str], cwd: Path) -> subprocess.CompletedProcess[str] | None:
    env = dict(os.environ, NO_COLOR="1")
    try:
        return subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired):
        return None


def rel(path: Path, workspace: Path) -> str:
    try:
        return str(path.relative_to(workspace))
    except ValueError:
        return str(path)


def check_dprint(root: Path, files: list[Path] | None, workspace: Path) -> None:
    argv = ["dprint", "check", "--allow-no-files"]
    if files is not None:
        argv += [str(f.relative_to(root)) for f in files]
    proc = run_tool(argv, root)
    if proc is None:
        emit("markdown-format", "warn", f"dprint not on PATH — format check skipped for {rel(root, workspace)}", remediation="npm install -g dprint")
        return
    if proc.returncode == 0:
        return
    output = ANSI_RE.sub("", proc.stdout + proc.stderr)
    named = False
    for raw in output.splitlines():
        m = DPRINT_FROM_RE.match(raw.strip())
        if m:
            named = True
            emit("markdown-format", "fail", f"not formatted per {rel(root, workspace)}/{DPRINT_CONFIG}", file=rel(Path(m.group("path")), workspace), remediation=f"Run `dprint fmt` in {rel(root, workspace)}.")
    if not named:
        detail = output.strip().splitlines()
        emit("markdown-format", "fail", f"dprint check failed in {rel(root, workspace)}: {detail[-1] if detail else 'no output'}")


def check_rumdl(root: Path, files: list[Path] | None, workspace: Path) -> None:
    argv = ["rumdl", "check", "--color", "never", "--output-format", "text"]
    argv += ["."] if files is None else [str(f.relative_to(root)) for f in files]
    proc = run_tool(argv, root)
    if proc is None:
        emit("markdown-lint", "warn", f"rumdl not on PATH — markdown lint skipped for {rel(root, workspace)}", remediation="uv tool install rumdl")
        return
    if proc.returncode == 0:
        return
    output = ANSI_RE.sub("", proc.stdout + proc.stderr)
    named = False
    for raw in output.splitlines():
        m = RUMDL_LINE_RE.match(raw.strip())
        if m:
            named = True
            emit("markdown-lint", "fail", m.group("msg"), file=rel(root / m.group("path"), workspace), line=int(m.group("line")), remediation=f"Run `rumdl check . --fix` in {rel(root, workspace)} for the autofixable subset.")
    if not named:
        detail = output.strip().splitlines()
        emit("markdown-lint", "fail", f"rumdl check failed in {rel(root, workspace)}: {detail[-1] if detail else 'no output'}")


def check_vale(root: Path, files: list[Path] | None, workspace: Path) -> None:
    argv = ["vale", "--output=line"]
    argv += ["."] if files is None else [str(f.relative_to(root)) for f in files]
    proc = run_tool(argv, root)
    if proc is None:
        emit("markdown-prose-lint", "warn", f"vale not on PATH — process-reference check skipped for {rel(root, workspace)}", remediation="mise use -g vale")
        return
    if proc.returncode == 0:
        return
    output = ANSI_RE.sub("", proc.stdout + proc.stderr)
    named = False
    for raw in output.splitlines():
        m = VALE_LINE_RE.match(raw.strip())
        if m:
            named = True
            emit("markdown-prose-lint", "fail", f"{m.group('rule').strip()}: {m.group('msg').strip()}", file=rel(root / m.group("path"), workspace), line=int(m.group("line")), remediation="Delete the citation; if the sentence states nothing once it's gone, delete the sentence too (canon:no-process-refs's fix is deletion, not rephrasing).")
    if not named:
        detail = output.strip().splitlines()
        emit("markdown-prose-lint", "fail", f"vale check failed in {rel(root, workspace)}: {detail[-1] if detail else 'no output'}")


def main() -> int:
    workspace = Path(os.environ.get("WINTER_WORKSPACE_DIR", os.getcwd())).resolve()
    for root, files in sorted(group_scope(scope_paths()).items()):
        if (root / DPRINT_CONFIG).is_file():
            check_dprint(root, files, workspace)
        if (root / RUMDL_CONFIG).is_file():
            check_rumdl(root, files, workspace)
        if (root / VALE_CONFIG).is_file():
            check_vale(root, files, workspace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
