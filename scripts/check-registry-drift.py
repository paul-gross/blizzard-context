#!/usr/bin/env python3
"""Registry-drift check for blizzard-context's verifiability matrix.

Joins the citations in ``verification/**/*.md`` (paths, test files, tier
attributions, the e2e scenario roster, the shell-sweep spec roster, `mise
run`/`npm run` task names, and paired command text) against the real
`blizzard` and `blizzard-mock` checkouts, and sweeps the whole repo for
dangling ordinal/cardinal scenario or spec identification. Stdlib-only,
Python 3.11+.

Emits NDJSON findings on stdout, one object per line, following the
`winter lint` finding contract (`check`, `status` in {pass, warn, fail},
optional `message`/`file`/`line`/`remediation`). Exits 0 by default; with
`--gate`, exits 1 on any `fail` finding, on any registry input missing
(`blizzard.md`, `commands.md`, `e2e-scenarios.md`, or an empty
`verification/` sweep), or on any check that did not actually run to
completion against its full required inputs — an unresolved interpreter, a
marker whose `pytest --collect-only` failed, or an unreadable `mise.toml`/
`package.json` all count as *not run*, never as a silent pass. A check
degraded by a partial input never gates green just because its own findings
list came back empty.

Declared limitations (stated here rather than discovered later):

- Tier association is read from `commands.md`'s `### <method-id>` sections
  only. A test file cited in `blizzard.md`'s free-prose tier rules gets
  checks A and B1 but not B2 — associating a tier from running prose is not
  mechanizable; that half stays a `blizzard-context:manual-reference-check`
  item.
- B1 and B2 run against the **blizzard checkout only**. `blizzard-mock`
  registers a single pytest marker (`e2e`) and its `blizzard-mock:unit-test`
  method is bare `uv run pytest` by design, so "which tier does this file
  live in" has no answer there. Blizzard-mock-scoped citations get check A
  and nothing more.
- Check A answers existence, not attribution: scope sets search order, and a
  citation resolving in the sibling checkout passes.
- Angle-bracket placeholder literals and rootless wildcards are excluded
  from check A — neither has an on-disk referent.
- B2's cross-tier classifier and D2's pairing rule are documented heuristics
  with auditable output, not parsers. Their skip lists are reviewed by hand
  whenever the relevant sections are edited.
- The script proves *agreement*, never *adequacy*. A registry entry that
  describes a real test inaccurately passes every check. Prose accuracy is a
  human read.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

# --------------------------------------------------------------------------
# Finding shape
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Finding:
    check: str
    status: str
    message: str = ""
    file: str | None = None
    line: int | None = None
    remediation: str = ""

    def to_json(self) -> str:
        obj: dict[str, object] = {"check": self.check, "status": self.status}
        if self.message:
            obj["message"] = self.message
        if self.file is not None:
            obj["file"] = self.file
        if self.line is not None:
            obj["line"] = self.line
        if self.remediation:
            obj["remediation"] = self.remediation
        return json.dumps(obj)


# --------------------------------------------------------------------------
# Exemptions
# --------------------------------------------------------------------------

# D4 (blizzard#272 Phase 1). Each entry: relative-to-blizzard-checkout path ->
# one-line reason naming the tracking issue. An exempted file emits a `warn`
# in check B1, never a silent `pass`.
KNOWN_UNMARKED: dict[str, str] = {
    "tests/test_intended_migration_apply.py": (
        "carries no pytestmark and no per-test marker at all, so no tier "
        "selection collects it — fix filed as blizzard#286; sibling ordinal "
        "cleanup blizzard#285 — this exemption is deleted when #286 lands."
    ),
}

# The blizzard tier markers check B1/B2/C draw from, in the order the matrix
# lists them.
MARKERS = ("unit", "component", "service", "crash_sweep", "journey", "e2e")

# ### <method-id> sections in commands.md that are themselves a test tier —
# check B2's own-tier agreement is scoped to exactly these.
TIER_METHODS = {
    "blizzard:unit-test": "unit",
    "blizzard:component-test": "component",
    "blizzard:service-test": "service",
    "blizzard:crash-sweep": "crash_sweep",
    "blizzard:journey": "journey",
}

CANDIDATE_ROOTS = (
    "tests/",
    "src/",
    "web/",
    "scripts/",
    "contracts/",
    "openapi/",
    "packaging/",
    "blizzard/",
    "blizzard-mock/",
)

PRUNE_DIRS = frozenset({".git", ".venv", "node_modules", "__pycache__", ".mypy_cache", ".ruff_cache"})

NUMERAL_WORDS = (
    "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty",
)

UNIT_SUFFIXES = ("px", "%", "ms", "KiB", "s")

# --------------------------------------------------------------------------
# Regexes
# --------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
_HEADING_RE = re.compile(r"^(#{2,3}) (.+?)\s*$", re.MULTILINE)
_TEST_FILE_RE = re.compile(r"^(?:.*/)?test_[A-Za-z0-9_]+\.py$")
_SPEC_BARE_RE = re.compile(r"^[A-Za-z0-9_.-]+\.spec\.ts$")
_MISE_RUN_RE = re.compile(r"^mise run ([A-Za-z][A-Za-z0-9_-]*)$")
_MISE_RUN_ANY_RE = re.compile(r"\bmise run ([A-Za-z][A-Za-z0-9_-]*)\b")
_NPM_RUN_ANY_RE = re.compile(r"\bnpm run ([A-Za-z][A-Za-z0-9:_-]*)\b")
_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

_E1A_WORD_DIGIT_RE = re.compile(r"\b(?:scenarios?|specs?)\b[^.;,)\n]{0,20}?(?P<digit>[0-9])", re.IGNORECASE)
_E1A_HYPHEN_RE = re.compile(r"\bscenario-(?P<digit>[0-9]+)", re.IGNORECASE)
_NUMERAL_RE = re.compile(r"\b(" + "|".join(NUMERAL_WORDS) + r")\b", re.IGNORECASE)
_SCENARIO_SPEC_WORD_RE = re.compile(r"\b(?:scenarios?|specs?)\b", re.IGNORECASE)
_PAREN_INT_RE = re.compile(r"\((\d+)\)")

_TIER_WORD_RE = re.compile(r"\b(unit|component|service|crash[ _-]?sweep|journey)\b", re.IGNORECASE)
_TIER_MENTION_RE = re.compile(r"\btiers?\b", re.IGNORECASE)
_METHOD_ID_RE = re.compile(r"blizzard:(unit-test|component-test|service-test|crash-sweep|journey|e2e)")


def _normalize_tier_word(word: str) -> str:
    return re.sub(r"[ -]", "_", word.lower())


# --------------------------------------------------------------------------
# Small generic helpers
# --------------------------------------------------------------------------


def _relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _md_files(root: Path) -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in PRUNE_DIRS)
        for name in sorted(filenames):
            if name.endswith(".md"):
                found.append(Path(dirpath) / name)
    return found


def _safe_shlex_split(s: str) -> list[str]:
    try:
        return shlex.split(s)
    except ValueError:
        return s.split()


def _expand_braces(s: str) -> list[str]:
    m = re.search(r"\{([^{}]+)\}", s)
    if not m:
        return [s]
    options = m.group(1).split(",")
    results: list[str] = []
    for opt in options:
        results.extend(_expand_braces(s[: m.start()] + opt + s[m.end() :]))
    return results


def _iter_candidate_tokens(text: str) -> list[tuple[int, str]]:
    """(line_no, token) pairs from inline-code spans and fenced lines, tokenized on whitespace."""
    results: list[tuple[int, str]] = []
    in_fence = False
    fence_marker: tuple[str, int] | None = None
    for i, line in enumerate(text.splitlines(), start=1):
        fm = _FENCE_RE.match(line)
        if in_fence:
            assert fence_marker is not None
            if fm and fm.group(1)[0] == fence_marker[0] and len(fm.group(1)) >= fence_marker[1]:
                in_fence = False
            else:
                for tok in _safe_shlex_split(line):
                    results.append((i, tok))
            continue
        if fm:
            in_fence = True
            fence_marker = (fm.group(1)[0], len(fm.group(1)))
            continue
        for span in _CODE_SPAN_RE.finditer(line):
            for tok in _safe_shlex_split(span.group(1)):
                results.append((i, tok))
    return results


def _is_candidate_path(token: str) -> bool:
    if "<" in token or ">" in token:
        return False
    if token.startswith(CANDIDATE_ROOTS):
        return True
    if _TEST_FILE_RE.fullmatch(token):
        return True
    if _SPEC_BARE_RE.fullmatch(token) and "/" not in token:
        return True
    return False


def _sections(text: str, level_prefix: str = "###") -> list[tuple[str, int, str]]:
    """(heading, body_start_line, body_text) for every heading at the given level."""
    all_headings = list(_HEADING_RE.finditer(text))
    out: list[tuple[str, int, str]] = []
    for idx, m in enumerate(all_headings):
        if m.group(1) != level_prefix:
            continue
        start = m.end()
        end = all_headings[idx + 1].start() if idx + 1 < len(all_headings) else len(text)
        body_start_line = text.count("\n", 0, start) + 1
        out.append((m.group(2).strip(), body_start_line, text[start:end]))
    return out


# --------------------------------------------------------------------------
# Checkout resolution
# --------------------------------------------------------------------------


def _resolve_in_root(path_str: str, root: Path) -> bool:
    if "{" in path_str:
        expansions = _expand_braces(path_str)
        return all(_resolve_in_root(e, root) for e in expansions)
    if any(c in path_str for c in "*?["):
        return len(glob.glob(str(root / path_str))) > 0
    if "/" in path_str:
        return (root / path_str).exists()
    matches = glob.glob(str(root / "**" / path_str), recursive=True)
    matches = [m for m in matches if not any(part in PRUNE_DIRS for part in Path(m).parts)]
    return len(matches) > 0


def _resolve_token(token: str, checkouts: dict[str, Path]) -> bool | None:
    """True/False if resolvable at all; None if a needed checkout is unresolved."""
    for prefix, name in (("blizzard-mock/", "blizzard-mock"), ("blizzard/", "blizzard")):
        if token.startswith(prefix):
            root = checkouts.get(name)
            if root is None:
                return None
            return _resolve_in_root(token[len(prefix) :], root)
    tried_any = False
    for name in ("blizzard", "blizzard-mock"):
        root = checkouts.get(name)
        if root is None:
            continue
        tried_any = True
        if _resolve_in_root(token, root):
            return True
    return False if tried_any else None


def _resolve_test_file(token: str, blizzard_root: Path) -> Path | None:
    token = token.split("::", 1)[0]
    if token.startswith("blizzard/"):
        token = token[len("blizzard/") :]
    if "/" in token:
        candidate = blizzard_root / token
        return candidate if candidate.is_file() else None
    matches = glob.glob(str(blizzard_root / "**" / token), recursive=True)
    matches = [m for m in matches if not any(part in PRUNE_DIRS for part in Path(m).parts)]
    matches = [m for m in matches if os.path.isfile(m)]
    return Path(matches[0]) if matches else None


# --------------------------------------------------------------------------
# Check A — cited-path existence
# --------------------------------------------------------------------------


def check_A(md_files: list[tuple[str, str]], checkouts: dict[str, Path], collect_cache: dict[str, list[str] | None]) -> list[Finding]:
    findings: list[Finding] = []
    # The node-id function-half assert below draws on every marker's collected
    # nodes; a marker whose collection was attempted and failed (an explicit
    # `None` entry — distinct from a marker simply absent from a canned test
    # fixture) must not invent a fail for a function that only lives there.
    collection_degraded = any(v is None for k, v in collect_cache.items() if k in MARKERS)
    for relfile, text in md_files:
        for line_no, token in _iter_candidate_tokens(text):
            if not _is_candidate_path(token):
                continue
            path_part, sep, func_part = token.partition("::")
            resolved = _resolve_token(path_part, checkouts)
            if resolved is None:
                findings.append(
                    Finding(
                        "A",
                        "warn",
                        f"could not resolve `{token}` — an unresolvable checkout",
                        relfile,
                        line_no,
                    )
                )
                continue
            if not resolved:
                findings.append(
                    Finding(
                        "A",
                        "fail",
                        f"`{token}` does not resolve in either checkout",
                        relfile,
                        line_no,
                        "Fix or remove the citation.",
                    )
                )
                continue
            if sep and "blizzard" in checkouts:
                test_path = _resolve_test_file(path_part, checkouts["blizzard"])
                if test_path is not None and _TEST_FILE_RE.fullmatch(test_path.name):
                    all_nodes: set[str] = set()
                    for marker in MARKERS:
                        nodes = collect_cache.get(marker)
                        if nodes:
                            all_nodes.update(nodes)
                    relpath = test_path.relative_to(checkouts["blizzard"]).as_posix()
                    prefix = f"{relpath}::{func_part}"
                    if not collection_degraded and all_nodes and not any(n == prefix or n.startswith(prefix + "[") for n in all_nodes):
                        findings.append(
                            Finding(
                                "A",
                                "fail",
                                f"`{token}` — function half `{func_part}` not found among {relpath}'s collected nodes",
                                relfile,
                                line_no,
                                "Fix the function name or remove the citation.",
                            )
                        )
    return findings


# --------------------------------------------------------------------------
# Check B1 — every cited test file lives in some tier (blizzard checkout only)
# --------------------------------------------------------------------------


def check_B1(
    md_files: list[tuple[str, str]],
    blizzard_root: Path,
    collect_cache: dict[str, list[str] | None],
) -> list[Finding]:
    findings: list[Finding] = []
    seen: dict[str, tuple[str, int]] = {}
    files_for_marker: dict[str, set[str]] = {}
    for marker, nodes in collect_cache.items():
        if nodes is None:
            continue
        files_for_marker[marker] = {n.split("::", 1)[0] for n in nodes}
    # A marker whose collection was attempted and failed (an explicit `None`
    # entry — distinct from a marker simply absent from a canned test
    # fixture) must not invent a "collects 0 nodes anywhere" fail for a file
    # that only lives under the missing marker.
    collection_degraded = any(v is None for k, v in collect_cache.items() if k in MARKERS)

    for relfile, text in md_files:
        for line_no, token in _iter_candidate_tokens(text):
            path_part = token.split("::", 1)[0]
            if not _TEST_FILE_RE.fullmatch(path_part.rsplit("/", 1)[-1]):
                continue
            resolved = _resolve_test_file(path_part, blizzard_root)
            if resolved is None:
                continue
            relpath = resolved.relative_to(blizzard_root).as_posix()
            if relpath in seen:
                continue
            seen[relpath] = (relfile, line_no)

    for relpath, (relfile, line_no) in seen.items():
        if relpath.rsplit("/", 1)[-1] == "conftest.py" or not relpath.endswith(".py") or "test_" not in relpath.rsplit("/", 1)[-1]:
            continue
        if relpath in KNOWN_UNMARKED:
            findings.append(
                Finding(
                    "B1",
                    "warn",
                    f"{relpath} {KNOWN_UNMARKED[relpath]}",
                    relfile,
                    line_no,
                    "Land the tracked marker fix, then delete this KNOWN_UNMARKED entry.",
                )
            )
            continue
        collects_somewhere = any(relpath in files for files in files_for_marker.values())
        if not collects_somewhere and files_for_marker and not collection_degraded:
            findings.append(
                Finding(
                    "B1",
                    "fail",
                    f"{relpath} collects 0 nodes under any of {MARKERS}",
                    relfile,
                    line_no,
                    "Add a pytestmark or per-test marker selecting a tier.",
                )
            )
    return findings


# --------------------------------------------------------------------------
# Check B2 — own-tier agreement (commands.md ### <tier-method> sections only)
# --------------------------------------------------------------------------


# A named-tier attribution is read from a *local* window immediately before
# the citation, not the whole (often multi-hundred-character) run-on
# sentence this prose is written in — otherwise a section-lead boilerplate
# link or an unrelated citation's own tier word bleeds across.
_NAMED_TIER_WINDOW = 110

_MD_LINK_RE = re.compile(r"\[[^\]\n]*\]\([^)\n]*\)")


def _mask_markdown_links(text: str) -> str:
    """Blank out `[text](url)` spans (same length) so link boilerplate — e.g.
    the section-lead `([tiers](../blizzard.md#test-tiers))` — never reads as
    a tier attribution."""
    return _MD_LINK_RE.sub(lambda m: " " * len(m.group(0)), text)


def _named_tiers(window: str) -> set[str]:
    tiers: set[str] = set()
    if _TIER_MENTION_RE.search(window):
        for m in _TIER_WORD_RE.finditer(window):
            tiers.add(_normalize_tier_word(m.group(1)))
    if re.search(r"\be2e\b", window, re.IGNORECASE):
        tiers.add("e2e")
    for m in _METHOD_ID_RE.finditer(window):
        method = m.group(1)
        if method == "crash-sweep":
            tiers.add("crash_sweep")
        elif method in ("journey", "e2e"):
            tiers.add(method)
        else:
            tiers.add(method.split("-")[0])
    return tiers


def check_B2(
    commands_relfile: str,
    commands_text: str,
    blizzard_root: Path,
    collect_cache: dict[str, list[str] | None],
) -> list[Finding]:
    findings: list[Finding] = []
    files_for_marker: dict[str, set[str]] = {}
    for marker, nodes in collect_cache.items():
        if nodes is None:
            continue
        files_for_marker[marker] = {n.split("::", 1)[0] for n in nodes}

    for heading, body_start_line, body in _sections(commands_text, "###"):
        section_tier = TIER_METHODS.get(heading)
        if section_tier is None:
            continue
        masked_body = _mask_markdown_links(body)
        for m in _CODE_SPAN_RE.finditer(body):
            content = m.group(1)
            path_part = content.split("::", 1)[0]
            base = path_part.rsplit("/", 1)[-1]
            if not _TEST_FILE_RE.fullmatch(base):
                continue
            resolved = _resolve_test_file(path_part, blizzard_root)
            if resolved is None:
                continue
            relpath = resolved.relative_to(blizzard_root).as_posix()
            abs_line = body.count("\n", 0, m.start()) + body_start_line
            radius_start = max(0, m.start() - _NAMED_TIER_WINDOW)
            sentence_boundary = masked_body.rfind(". ", radius_start, m.start())
            window_start = sentence_boundary + 2 if sentence_boundary != -1 else radius_start
            window = masked_body[window_start : m.start()]
            named = _named_tiers(window) - {section_tier}
            if named:
                findings.append(
                    Finding(
                        "B2",
                        "pass",
                        f"{relpath} cited under ### {heading} names tier(s) {sorted(named)} — cross-tier, classified",
                        commands_relfile,
                        abs_line,
                    )
                )
                continue
            if not files_for_marker:
                continue
            actual = {marker for marker, files in files_for_marker.items() if relpath in files}
            if section_tier not in actual:
                findings.append(
                    Finding(
                        "B2",
                        "fail",
                        f"{relpath} cited under ### {heading} (`-m {section_tier}`) but collects 0 nodes there — actually {sorted(actual) or 'nothing'}",
                        commands_relfile,
                        abs_line,
                        f"Move the citation to its real tier's section, or name the real tier in the sentence.",
                    )
                )
    return findings


# --------------------------------------------------------------------------
# Check C — e2e roster completeness
# --------------------------------------------------------------------------


def check_C(
    e2e_relfile: str,
    e2e_text: str,
    collect_cache: dict[str, list[str] | None],
) -> list[Finding]:
    findings: list[Finding] = []
    e2e_nodes = collect_cache.get("e2e")
    if e2e_nodes is None:
        return findings

    actual: set[tuple[str, str]] = set()
    for node in e2e_nodes:
        path, _, func = node.partition("::")
        func = func.split("[", 1)[0]
        module = Path(path).stem
        actual.add((module, func))

    bullet_re = re.compile(r"^- `(test_[A-Za-z0-9_]+)`", re.MULTILINE)
    all_headings = list(_HEADING_RE.finditer(e2e_text))

    documented: set[tuple[str, str]] = set()
    module_heading_line: dict[str, int] = {}
    orphans: list[tuple[int, str]] = []

    first_start = all_headings[0].start() if all_headings else len(e2e_text)
    for bm in bullet_re.finditer(e2e_text[:first_start]):
        line = e2e_text.count("\n", 0, bm.start()) + 1
        orphans.append((line, bm.group(1)))

    for i, m in enumerate(all_headings):
        level = len(m.group(1))
        heading_text = m.group(2).strip()
        body_start = m.end()
        body_end = all_headings[i + 1].start() if i + 1 < len(all_headings) else len(e2e_text)
        body = e2e_text[body_start:body_end]
        if level == 3:
            module_heading_line[heading_text] = e2e_text.count("\n", 0, m.start()) + 1
            for bm in bullet_re.finditer(body):
                documented.add((heading_text, bm.group(1)))
        else:
            for bm in bullet_re.finditer(body):
                line = e2e_text.count("\n", 0, body_start + bm.start()) + 1
                orphans.append((line, bm.group(1)))

    for module, func in sorted(actual - documented):
        line = module_heading_line.get(module)
        findings.append(
            Finding(
                "C",
                "fail",
                f"tests/e2e/{module}.py::{func} is collected but not described under ### {module} in the registry",
                e2e_relfile,
                line,
                "Add a bullet naming this function under its module heading.",
            )
        )

    for module, func in sorted(documented - actual):
        line = module_heading_line.get(module)
        findings.append(
            Finding(
                "C",
                "fail",
                f"registry bullet `{func}` under ### {module} has no matching collected e2e node",
                e2e_relfile,
                line,
                "Fix the function/module name or remove the stale bullet.",
            )
        )

    for line, func in orphans:
        findings.append(
            Finding(
                "C",
                "fail",
                f"bullet `{func}` cited with no owning ### module heading",
                e2e_relfile,
                line,
                "Move the bullet under its module's ### heading.",
            )
        )

    return findings


# --------------------------------------------------------------------------
# Check C2 — shell-sweep roster
# --------------------------------------------------------------------------


def check_C2(commands_relfile: str, commands_text: str, blizzard_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    sections = _sections(commands_text, "###")
    body = ""
    body_start_line = 1
    for heading, start_line, text in sections:
        if heading == "web:shell-sweep":
            body = text
            body_start_line = start_line
            break
    else:
        return findings

    doc_names: dict[str, int] = {}
    for m in re.finditer(r"`([A-Za-z0-9_.-]*\.shell-sweep\.spec\.ts)`", body):
        name = m.group(1)
        if "*" in name:
            continue
        line = body.count("\n", 0, m.start()) + body_start_line
        doc_names.setdefault(name, line)

    doc_paths: set[str] = set()
    for name, line in doc_names.items():
        matches = glob.glob(str(blizzard_root / "web" / "projects" / "**" / name), recursive=True)
        matches = [m for m in matches if os.path.isfile(m)]
        if matches:
            doc_paths.add(Path(matches[0]).relative_to(blizzard_root).as_posix())
        else:
            findings.append(
                Finding(
                    "C2",
                    "fail",
                    f"`{name}` cited under ### web:shell-sweep but not found on disk",
                    commands_relfile,
                    line,
                    "Fix the filename or remove the citation.",
                )
            )

    disk_matches = glob.glob(str(blizzard_root / "web" / "projects" / "**" / "*.shell-sweep.spec.ts"), recursive=True)
    disk_paths = {Path(m).relative_to(blizzard_root).as_posix() for m in disk_matches if os.path.isfile(m)}

    for p in sorted(disk_paths - doc_paths):
        findings.append(
            Finding(
                "C2",
                "fail",
                f"{p} exists on disk but is not cited under ### web:shell-sweep",
                commands_relfile,
                body_start_line,
                "Add its filename to ### web:shell-sweep.",
            )
        )
    return findings


# --------------------------------------------------------------------------
# Check D — task-name resolution
# --------------------------------------------------------------------------


def _load_mise_tasks(blizzard_root: Path) -> dict[str, dict] | None:
    path = blizzard_root / "mise.toml"
    if not path.is_file():
        return None
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError):
        return None
    return data.get("tasks", {})


def _load_npm_scripts(blizzard_root: Path) -> dict[str, str] | None:
    path = blizzard_root / "web" / "package.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return data.get("scripts", {})


def check_D(md_files: list[tuple[str, str]], blizzard_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    mise_tasks = _load_mise_tasks(blizzard_root)
    npm_scripts = _load_npm_scripts(blizzard_root)
    if mise_tasks is None:
        findings.append(Finding("D", "warn", "could not read blizzard/mise.toml — task-name resolution skipped"))
    if npm_scripts is None:
        findings.append(Finding("D", "warn", "could not read blizzard/web/package.json — npm-script resolution skipped"))

    for relfile, text in md_files:
        if mise_tasks is not None:
            for m in _MISE_RUN_ANY_RE.finditer(text):
                task = m.group(1)
                if task not in mise_tasks:
                    line = text.count("\n", 0, m.start()) + 1
                    findings.append(
                        Finding(
                            "D",
                            "fail",
                            f"`mise run {task}` does not resolve to a [tasks.{task}] in mise.toml",
                            relfile,
                            line,
                            "Fix the task name or add it to mise.toml.",
                        )
                    )
        if npm_scripts is not None:
            for m in _NPM_RUN_ANY_RE.finditer(text):
                script = m.group(1)
                if script not in npm_scripts:
                    line = text.count("\n", 0, m.start()) + 1
                    findings.append(
                        Finding(
                            "D",
                            "fail",
                            f"`npm run {script}` does not resolve to a scripts entry in web/package.json",
                            relfile,
                            line,
                            "Fix the script name or add it to web/package.json.",
                        )
                    )
    return findings


# --------------------------------------------------------------------------
# Check D2 — task-command agreement
# --------------------------------------------------------------------------


def _looks_like_command(text: str) -> bool:
    tokens = _safe_shlex_split(text)
    i = 0
    while i < len(tokens) and _ASSIGN_RE.match(tokens[i]):
        i += 1
    if i >= len(tokens):
        return False
    first = tokens[i]
    if "/" in first:
        return True
    return first in {"uv", "npm", "npx", "python", "pytest"}


def _split_assigns(text: str) -> tuple[frozenset[str], list[str]]:
    tokens = _safe_shlex_split(text)
    tokens = [t[2:] if t.startswith("./") else t for t in tokens]
    i = 0
    while i < len(tokens) and _ASSIGN_RE.match(tokens[i]):
        i += 1
    return frozenset(tokens[:i]), tokens[i:]


def _compare_commands(doc_text: str, task_text: str) -> str:
    doc_assigns, doc_rest = _split_assigns(doc_text)
    task_assigns, task_rest = _split_assigns(task_text)
    if doc_assigns != task_assigns:
        return "mismatch"
    if doc_rest == task_rest:
        return "exact"
    n = len(doc_rest)
    if 0 < n < len(task_rest) and task_rest[:n] == doc_rest:
        return "prefix"
    if 0 < n < len(task_rest) and task_rest[-n:] == doc_rest:
        return "missing-runner-prefix"
    return "mismatch"


def check_D2(md_files: list[tuple[str, str]], blizzard_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    mise_tasks = _load_mise_tasks(blizzard_root)
    if mise_tasks is None:
        findings.append(
            Finding("D2", "warn", "could not read blizzard/mise.toml — task-command agreement skipped")
        )
        return findings

    for relfile, text in md_files:
        for line_no, line in enumerate(text.splitlines(), start=1):
            spans = list(_CODE_SPAN_RE.finditer(line))
            for idx, sp in enumerate(spans):
                mm = _MISE_RUN_RE.fullmatch(sp.group(1).strip())
                if not mm:
                    continue
                task = mm.group(1)
                paired = None
                if idx + 1 < len(spans):
                    gap = line[sp.end() : spans[idx + 1].start()]
                    if re.fullmatch(r"[\s()]{0,4}", gap):
                        paired = spans[idx + 1]
                if paired is None and idx - 1 >= 0:
                    gap = line[spans[idx - 1].end() : sp.start()]
                    if re.fullmatch(r"[\s()]{0,4}", gap):
                        paired = spans[idx - 1]
                if paired is None:
                    continue
                candidate_text = paired.group(1)
                if not _looks_like_command(candidate_text):
                    continue
                if task not in mise_tasks:
                    continue
                task_run = mise_tasks[task].get("run", "")
                if not isinstance(task_run, str):
                    continue
                relation = _compare_commands(candidate_text, task_run)
                if relation == "exact":
                    continue
                if relation == "prefix":
                    findings.append(
                        Finding(
                            "D2",
                            "warn",
                            f"`mise run {task}` documents `{candidate_text}`, a strict prefix of the task's `{task_run}`",
                            relfile,
                            line_no,
                            f"Bring the documented form to `{task_run}`.",
                        )
                    )
                elif relation == "missing-runner-prefix":
                    findings.append(
                        Finding(
                            "D2",
                            "fail",
                            f"`mise run {task}` documents `{candidate_text}`, missing the task's runner prefix — the task actually runs `{task_run}`",
                            relfile,
                            line_no,
                            f"Bring the documented form to `{task_run}`.",
                        )
                    )
                else:
                    findings.append(
                        Finding(
                            "D2",
                            "fail",
                            f"`mise run {task}` documents `{candidate_text}`, which does not match the task's `{task_run}`",
                            relfile,
                            line_no,
                            f"Bring the documented form to `{task_run}`.",
                        )
                    )
    return findings


# --------------------------------------------------------------------------
# Check E — no ordinal or cardinal spec identification (repo-wide)
# --------------------------------------------------------------------------


def _lines_excluding_fences(text: str) -> list[tuple[int, str, list[tuple[int, int]]]]:
    out: list[tuple[int, str, list[tuple[int, int]]]] = []
    in_fence = False
    fence_marker: tuple[str, int] | None = None
    for i, line in enumerate(text.splitlines(), start=1):
        fm = _FENCE_RE.match(line)
        if in_fence:
            assert fence_marker is not None
            if fm and fm.group(1)[0] == fence_marker[0] and len(fm.group(1)) >= fence_marker[1]:
                in_fence = False
            continue
        if fm:
            in_fence = True
            fence_marker = (fm.group(1)[0], len(fm.group(1)))
            continue
        spans = [(m.start(), m.end()) for m in _CODE_SPAN_RE.finditer(line)]
        out.append((i, line, spans))
    return out


def _in_span(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(s <= pos < e for s, e in spans)


def _e1a_hits(line: str, spans: list[tuple[int, int]]) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    seen: set[int] = set()
    for regex in (_E1A_WORD_DIGIT_RE, _E1A_HYPHEN_RE):
        for m in regex.finditer(line):
            dpos = m.start("digit")
            if dpos in seen:
                continue
            run_start = dpos
            while run_start > 0 and line[run_start - 1].isdigit():
                run_start -= 1
            run_end = dpos
            while run_end < len(line) and line[run_end].isdigit():
                run_end += 1
            for p in range(run_start, run_end):
                seen.add(p)
            if _in_span(run_start, spans):
                continue
            prev_char = line[run_start - 1] if run_start > 0 else ""
            if prev_char and re.match(r"[A-Za-z0-9_]", prev_char):
                continue
            suffix = line[run_end : run_end + 3]
            if any(suffix.startswith(s) for s in UNIT_SUFFIXES):
                continue
            hits.append((run_start, line[run_start:run_end]))
    return hits


def _e1b_hits(line: str, spans: list[tuple[int, int]]) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    numerals = [(m.start(), m.end()) for m in _NUMERAL_RE.finditer(line) if not _in_span(m.start(), spans)]
    words = [(m.start(), m.end()) for m in _SCENARIO_SPEC_WORD_RE.finditer(line) if not _in_span(m.start(), spans)]
    reported: set[int] = set()
    for ns, ne in numerals:
        for ws, we in words:
            gap = max(ns, ws) - min(ne, we)
            if gap <= 20 and ns not in reported:
                hits.append((min(ns, ws), line[min(ns, ws) : max(ne, we)]))
                reported.add(ns)
                break
    return hits


def _e2_hits(line: str, spans: list[tuple[int, int]]) -> list[tuple[int, str]]:
    matches = [
        (int(m.group(1)), m.start())
        for m in _PAREN_INT_RE.finditer(line)
        if not _in_span(m.start(), spans)
    ]
    hits: list[tuple[int, str]] = []
    expected = 1
    for value, start in matches:
        if value == expected:
            expected += 1
        elif value == 1:
            expected = 2
        else:
            hits.append((start, f"({value})"))
    return hits


def check_E(md_files: list[tuple[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for relfile, text in md_files:
        for line_no, line, spans in _lines_excluding_fences(text):
            for _pos, snippet in _e1a_hits(line, spans):
                findings.append(
                    Finding(
                        "E1a",
                        "fail",
                        f"standalone ordinal digit `{snippet}` near scenario/spec — {line.strip()}",
                        relfile,
                        line_no,
                        "Name the test/module instead of an ordinal.",
                    )
                )
            for _pos, snippet in _e1b_hits(line, spans):
                findings.append(
                    Finding(
                        "E1b",
                        "fail",
                        f"cardinal numeral `{snippet}` near scenario/spec — {line.strip()}",
                        relfile,
                        line_no,
                        "Name the test/module instead of a count.",
                    )
                )
            for _pos, snippet in _e2_hits(line, spans):
                findings.append(
                    Finding(
                        "E2",
                        "fail",
                        f"orphan parenthesized integer `{snippet}` — {line.strip()}",
                        relfile,
                        line_no,
                        "Name the test/module instead of a back-reference.",
                    )
                )
    return findings


# --------------------------------------------------------------------------
# Interpreter / collection
# --------------------------------------------------------------------------


def _resolve_interpreter(blizzard_root: Path) -> list[str] | None:
    venv_python = blizzard_root / ".venv" / "bin" / "python"
    if venv_python.is_file():
        return [str(venv_python), "-m", "pytest"]
    if shutil.which("uv"):
        return ["uv", "run", "--project", str(blizzard_root), "python", "-m", "pytest"]
    return None


def _collect(cmd_prefix: list[str], blizzard_root: Path, marker: str) -> list[str] | None:
    cmd = cmd_prefix + ["-m", marker, "tests/", "--collect-only", "-q"]
    try:
        result = subprocess.run(cmd, cwd=blizzard_root, capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode not in (0, 5):
        return None
    nodes = [ln.strip() for ln in result.stdout.splitlines() if "::" in ln]
    return nodes


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

# Every check `run()` may execute — the set `--gate` compares its actually-run
# checks against, so a check dropped by a missing checkout, interpreter, or
# registry input (rather than run and passing) is caught explicitly instead
# of inferred from warn text.
ALL_CHECKS = ("A", "B1", "B2", "C", "C2", "D", "D2", "E")


def run(repo_root: Path, blizzard_root: Path, blizzard_mock_root: Path, gate: bool) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    executed: set[str] = set()
    registry_input_missing = False

    checkouts: dict[str, Path] = {}
    if blizzard_root.is_dir():
        checkouts["blizzard"] = blizzard_root
    else:
        findings.append(
            Finding(
                "A",
                "warn",
                f"blizzard checkout not found at {blizzard_root} — checks A, B1, B2, C, C2, D, D2 skipped for blizzard-scoped citations",
            )
        )
    if blizzard_mock_root.is_dir():
        checkouts["blizzard-mock"] = blizzard_mock_root
    else:
        findings.append(
            Finding(
                "A",
                "warn",
                f"blizzard-mock checkout not found at {blizzard_mock_root} — check A skipped for blizzard-mock-scoped citations",
            )
        )

    collect_cache: dict[str, list[str] | None] = {}
    if "blizzard" in checkouts:
        interpreter = _resolve_interpreter(checkouts["blizzard"])
        if interpreter is None:
            findings.append(
                Finding("B1", "warn", "no python interpreter resolvable (.venv or uv) — checks B1, B2, C skipped")
            )
        else:
            for marker in MARKERS:
                nodes = _collect(interpreter, checkouts["blizzard"], marker)
                collect_cache[marker] = nodes
                if nodes is None:
                    findings.append(
                        Finding(
                            "B1",
                            "warn",
                            f"pytest collection failed for `-m {marker}` — checks needing it are incomplete for this marker",
                        )
                    )

    verification_dir = repo_root / "verification"
    verification_files: list[tuple[str, str]] = []
    for path in _md_files(verification_dir):
        verification_files.append((_relpath(path, repo_root), path.read_text(errors="replace")))
    if not verification_files:
        findings.append(
            Finding(
                "A",
                "warn",
                f"no markdown files found under {_relpath(verification_dir, repo_root)} — the registry sweep is empty",
            )
        )
        registry_input_missing = True

    all_md_files: list[tuple[str, str]] = []
    for path in _md_files(repo_root):
        all_md_files.append((_relpath(path, repo_root), path.read_text(errors="replace")))

    blizzard_md_path = verification_dir / "blizzard.md"
    if not blizzard_md_path.is_file():
        findings.append(
            Finding("A", "warn", f"expected registry input not found: {_relpath(blizzard_md_path, repo_root)}")
        )
        registry_input_missing = True

    commands_path = verification_dir / "blizzard" / "commands.md"
    commands_relfile = _relpath(commands_path, repo_root)
    commands_text = commands_path.read_text(errors="replace") if commands_path.is_file() else ""
    if not commands_text:
        findings.append(
            Finding("A", "warn", f"expected registry input not found: {commands_relfile} — checks B2, C2 skipped")
        )
        registry_input_missing = True

    e2e_path = verification_dir / "blizzard" / "e2e-scenarios.md"
    e2e_relfile = _relpath(e2e_path, repo_root)
    e2e_text = e2e_path.read_text(errors="replace") if e2e_path.is_file() else ""
    if not e2e_text:
        findings.append(Finding("A", "warn", f"expected registry input not found: {e2e_relfile} — check C skipped"))
        registry_input_missing = True

    # Effectiveness, not attempt: a check enters `executed` only when the
    # inputs it draws on were actually present, so a check that ran against
    # an empty/partial `collect_cache` (an unresolved interpreter, or one
    # marker's collection failing) lands in `skipped` exactly like a check
    # that never ran at all — `--gate` does not distinguish the two.
    markers_ok = {m: collect_cache.get(m) is not None for m in MARKERS}
    all_markers_ok = all(markers_ok.values())
    tier_markers_ok = all(markers_ok[m] for m in TIER_METHODS.values())
    e2e_marker_ok = markers_ok["e2e"]

    findings += check_A(verification_files, checkouts, collect_cache)
    # Check A's own node-id function-half assert (the `::func` half of a
    # citation) draws on every marker's collected nodes, same as B1 below.
    # A missing blizzard-mock checkout leaves blizzard-mock-scoped citations
    # unresolvable (downgraded to warn, never a fail), so A never actually
    # ran to completion against its full required inputs either.
    if all_markers_ok and "blizzard-mock" in checkouts:
        executed.add("A")

    if "blizzard" in checkouts:
        findings += check_B1(verification_files, checkouts["blizzard"], collect_cache)
        if all_markers_ok:
            executed.add("B1")
        if commands_text:
            findings += check_B2(commands_relfile, commands_text, checkouts["blizzard"], collect_cache)
            if tier_markers_ok:
                executed.add("B2")
        if e2e_text:
            findings += check_C(e2e_relfile, e2e_text, collect_cache)
            if e2e_marker_ok:
                executed.add("C")
        if commands_text:
            findings += check_C2(commands_relfile, commands_text, checkouts["blizzard"])
            executed.add("C2")

        mise_tasks_readable = _load_mise_tasks(checkouts["blizzard"]) is not None
        npm_scripts_readable = _load_npm_scripts(checkouts["blizzard"]) is not None
        findings += check_D(verification_files, checkouts["blizzard"])
        if mise_tasks_readable and npm_scripts_readable:
            executed.add("D")
        findings += check_D2(verification_files, checkouts["blizzard"])
        if mise_tasks_readable:
            executed.add("D2")

    findings += check_E(all_md_files)
    executed.add("E")

    fail_count = sum(1 for f in findings if f.status == "fail")
    skipped = set(ALL_CHECKS) - executed
    if gate and (fail_count or skipped or registry_input_missing):
        return findings, 1
    return findings, 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blizzard", default=None)
    parser.add_argument("--blizzard-mock", default=None)
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parent.parent
    blizzard_root = Path(args.blizzard).resolve() if args.blizzard else (repo_root.parent / "blizzard").resolve()
    blizzard_mock_root = (
        Path(args.blizzard_mock).resolve() if args.blizzard_mock else (repo_root.parent / "blizzard-mock").resolve()
    )

    findings, exit_code = run(repo_root, blizzard_root, blizzard_mock_root, args.gate)
    for finding in findings:
        print(finding.to_json())
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
