#!/usr/bin/env python3
"""Reference-integrity lint contribution for `winter lint`.

Checks the in-repo references a blizzard-context repo's Markdown makes, under four
check names:

  bzh-id-integrity       every `bzh:<slug>` citation resolves to exactly one heading
                         defined as `... (`bzh:<slug>`)`; a duplicate is reported at
                         every defining site
  reference-links        every inline relative link reaches an existing path; a
                         `#fragment` or a `§Heading` after a link or path-notation path
                         names a heading in the target
  hub-routing            every leaf is linked from its nearest hub (`<dir>/index.md`,
                         else the spoke-dir sibling `<dir>.md`)
  path-notation-targets  every `<module>:/path[#fragment]` token reaches an existing file

Only Markdown is scanned, never inside fenced code blocks. A scoped file belongs to a
blizzard-context repo when its nearest ancestor `winter-ext.toml` declares
`name = "blizzard-context"`; any other scoped path produces nothing. Indexes are built
from the whole owning repo, but findings are emitted only for files inside scope.

`blizzard-context:` path notation resolves against the owning repo root. `workspace:`
resolves against WINTER_WORKSPACE_DIR and any other module against the installed
`.winter/ext/*` extension whose manifest declares that `name`; both need
WINTER_WORKSPACE_DIR set and containing `.winter/`. Without it, each other module is
reported once per run as a `warn`, never a `fail`. A module neither installed nor
`workspace` is skipped: dependency direction is not this lint's domain.

This is a `winter lint` check (see winter-cli `configuration/lint.md`): it confines
itself to WINTER_LINT_PATHS and exits 0 by default. `--gate` exits 1 when any `fail`
was emitted, for a CI-usable exit.

Env contract (from `winter lint`):
  WINTER_WORKSPACE_DIR  absolute workspace root (findings are relativized to it)
  WINTER_LINT_PATHS     newline-delimited absolute paths in scope (files or dirs)
  WINTER_LINT_SCOPE     scope kind (all/repo/env/changed) — informational

Standalone: pass scope paths as argv.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

REPO_NAME = "blizzard-context"
MANIFEST = "winter-ext.toml"
SKIP_DIRS = {"node_modules", "__pycache__"}

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^ {0,3}#{1,6}[ \t]+(.*?)[ \t]*#*[ \t]*$")
LINK_RE = re.compile(r"\[(?:[^\]\\]|\\.)*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
PARAGRAPH_RE = re.compile(r"[^\n]+(?:\n[^\n]+)*")
PATH_NOTATION_RE = re.compile(r"(?<![\w/.:-])([A-Za-z][\w-]*):(/(?!/)[^\s`)\]>\"',;|]*)")
TRAILING_PATH_NOTATION_RE = re.compile(r"(?<![\w/.:-])([A-Za-z][\w-]*):(/[^\s`]*)$")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
SLUG_TAIL = r"[a-z0-9]+(?:-[a-z0-9]+)*"
BARE_NAME_BEFORE_SECTION_RE = re.compile(
    r"(?<![\w/.-])(?:[\w.-]+/)*[\w-]+\.[A-Za-z0-9]+$|(?<![\w-])[a-z][\w-]*:" + SLUG_TAIL + "$")


def emit(check: str, status: str, message: str, *, file: str | None = None, line: int | None = None, remediation: str | None = None) -> None:
    payload: dict[str, object] = {"check": check, "status": status, "message": message}
    if file is not None:
        payload["file"] = file
    if line is not None:
        payload["line"] = line
    if remediation is not None:
        payload["remediation"] = remediation
    print(json.dumps(payload))


def scope_paths(argv: list[str]) -> list[Path]:
    if argv:
        return [Path(p) for p in argv]
    raw = os.environ.get("WINTER_LINT_PATHS", "")
    return [Path(p) for p in raw.splitlines() if p.strip()]


def read_manifest(directory: Path) -> dict | None:
    manifest = directory / MANIFEST
    if not manifest.is_file():
        return None
    try:
        return tomllib.loads(manifest.read_text())
    except (OSError, tomllib.TOMLDecodeError):
        return None


def owning_repo(path: Path) -> tuple[Path, dict] | None:
    for parent in [path, *path.parents] if path.is_dir() else path.parents:
        manifest = read_manifest(parent)
        if manifest is not None:
            return (parent, manifest) if manifest.get("name") == REPO_NAME else None
    return None


def markdown_files(root: Path) -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS)
        found += [Path(dirpath) / n for n in sorted(filenames) if n.endswith(".md")]
    return found


def normalize(text: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return " ".join(text.replace("`", "").replace("*", "").lower().split())


def github_slug(heading: str) -> str:
    text = re.sub(r"[^\w\- ]", "", normalize(heading))
    return text.replace(" ", "-")


@dataclass
class Doc:
    path: Path
    text: str = ""
    nocode: str = ""
    spans: list[tuple[int, int, str]] = field(default_factory=list)
    headings: list[tuple[int, str]] = field(default_factory=list)
    links: list[tuple[int, int, str]] = field(default_factory=list)

    def line_of(self, pos: int) -> int:
        return self.text.count("\n", 0, pos) + 1

    @classmethod
    def load(cls, path: Path) -> Doc:
        doc = cls(path)
        lines: list[str] = []
        fence: tuple[str, int] | None = None
        for raw in path.read_text().split("\n"):
            m = FENCE_RE.match(raw)
            if fence is None:
                if m:
                    fence = (m.group(1)[0], len(m.group(1)))
                    raw = ""
            else:
                if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and not raw.strip().strip(fence[0]):
                    fence = None
                raw = ""
            lines.append(raw)
        doc.text = "\n".join(lines)
        masked = list(doc.text)
        for para in PARAGRAPH_RE.finditer(doc.text):
            for span in CODE_SPAN_RE.finditer(para.group()):
                start, end = para.start() + span.start(), para.start() + span.end()
                doc.spans.append((start, end, span.group(2).strip()))
                for i in range(start, end):
                    if masked[i] != "\n":
                        masked[i] = " "
        doc.nocode = "".join(masked)
        for number, line in enumerate(lines, 1):
            m = HEADING_RE.match(line)
            if m:
                doc.headings.append((number, m.group(1)))
        for m in LINK_RE.finditer(doc.nocode):
            doc.links.append((m.start(), m.end(), m.group(1)))
        return doc

    def anchors(self) -> set[str]:
        seen: dict[str, int] = {}
        found: set[str] = set()
        for _, heading in self.headings:
            slug = github_slug(heading)
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            found.add(slug if count == 0 else f"{slug}-{count}")
        return found

    def heading_texts(self, id_re: re.Pattern[str]) -> set[str]:
        """Each heading's full folded text, and again without its trailing rule id."""
        texts: set[str] = set()
        for _, heading in self.headings:
            texts.add(normalize(heading))
            texts.add(normalize(id_re.sub("", heading)))
        texts.discard("")
        return texts


class Run:
    def __init__(self, workspace: Path, workspace_mode: bool) -> None:
        self.workspace = workspace
        self.workspace_mode = workspace_mode
        self.failed = False
        self.warned_modules: set[str] = set()
        self.installed: dict[str, Path] | None = None
        self.docs: dict[Path, Doc] = {}

    def rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.workspace))
        except ValueError:
            return str(path)

    def fail(self, check: str, doc: Doc, pos_or_line: int, message: str, remediation: str, *, is_line: bool = False) -> None:
        self.failed = True
        line = pos_or_line if is_line else doc.line_of(pos_or_line)
        emit(check, "fail", message, file=self.rel(doc.path), line=line, remediation=remediation)

    def doc(self, path: Path) -> Doc:
        resolved = path.resolve()
        if resolved not in self.docs:
            self.docs[resolved] = Doc.load(resolved)
        return self.docs[resolved]

    def module_root(self, module: str, repo: Path) -> Path | None:
        if module == REPO_NAME:
            return repo
        if not self.workspace_mode:
            return None
        if module == "workspace":
            return self.workspace
        if self.installed is None:
            self.installed = {}
            for manifest in sorted((self.workspace / ".winter" / "ext").glob(f"*/{MANIFEST}")):
                declared = read_manifest(manifest.parent)
                if declared and "name" in declared:
                    self.installed[declared["name"]] = manifest.parent
        return self.installed.get(module)


def check_fragment(run: Run, doc: Doc, pos: int, target: Path, fragment: str, shown: str) -> None:
    if target.suffix != ".md" or not target.is_file():
        return
    if fragment not in run.doc(target).anchors():
        run.fail("reference-links", doc, pos, f"#{fragment}: no heading with that anchor in {shown}",
                 "Point the fragment at a heading slug that exists in the target, or drop it.")


def check_section(run: Run, doc: Doc, pos: int, target: Path, shown: str, id_re: re.Pattern[str]) -> None:
    """Resolve the `§Heading` citation starting at `pos` against `target`'s headings."""
    if target.suffix != ".md" or not target.is_file():
        return
    headings = run.doc(target).heading_texts(id_re)
    tail = doc.text[pos + 1:]
    end = re.search(r"\n[ \t]*\n|\|", tail)
    tail = tail[:end.start()] if end else tail
    quoted = re.match(r"[\"“]([^\"”]+)[\"”]", tail)
    if quoted:
        wanted = normalize(re.sub(r"-\s*\n\s*", "-", quoted.group(1)))
        if wanted in headings:
            return
        cited = f'§"{quoted.group(1)}"'
    else:
        folded = normalize(re.sub(r"-[ \t]*\n[ \t]*", "-", tail[:300]))
        for heading in headings:
            if folded.startswith(heading) and (len(folded) == len(heading) or not folded[len(heading)].isalnum()):
                return
        cited = "§" + " ".join(tail[:60].split())
    run.fail("reference-links", doc, pos, f"{cited}: no heading in {shown} matches it as a whole-heading prefix",
             "Cite the target's full heading text after `§`; a shortened heading is not a near-match.")


def section_target(run: Run, doc: Doc, pos: int, repo: Path, link_ends: dict[int, str]) -> Path | None:
    """The file a `§` at `pos` names, or None when its form is not checked."""
    before = doc.text[:pos].rstrip()
    if not before:
        return doc.path
    last = len(before) - 1
    if before[-1] == ")":
        target = link_ends.get(last + 1)
        if target is None or SCHEME_RE.match(target):
            return None
        path = target.split("#", 1)[0]
        return (doc.path.parent / path).resolve() if path else doc.path
    if before[-1] == "`":
        content = next((c for s, e, c in doc.spans if e == last + 1), "")
        m = re.fullmatch(r"([A-Za-z][\w-]*):(/[^\s]*)", content)
    else:
        m = TRAILING_PATH_NOTATION_RE.search(before[-300:])
        if m is None:
            if before[-1] == "]" or BARE_NAME_BEFORE_SECTION_RE.search(before[-300:]):
                return None
            return doc.path
    if m is None:
        return None
    root = run.module_root(m.group(1), repo)
    return (root / m.group(2).lstrip("/").split("#", 1)[0]) if root else None


def check_doc(run: Run, doc: Doc, repo: Path, prefix: str, defs: dict[str, list[tuple[Path, int]]], routed: dict[Path, set[Path]], id_re: re.Pattern[str]) -> None:
    token_re = re.compile(rf"(?<![\w-]){re.escape(prefix)}:({SLUG_TAIL})")
    def_lines = {number for number, heading in doc.headings if id_re.search(heading)}
    for m in token_re.finditer(doc.text):
        line = doc.line_of(m.start())
        if line in def_lines and id_re.search(doc.text.split("\n")[line - 1]) and \
                id_re.search(doc.text.split("\n")[line - 1]).group(1) == m.group(1):
            continue
        if m.group(1) not in defs:
            run.fail("bzh-id-integrity", doc, line, f"{prefix}:{m.group(1)}: no heading defines it",
                     "Cite an id defined by a heading ending in (`" + prefix + ":<slug>`), or drop the token.", is_line=True)
    for number in sorted(def_lines):
        slug = id_re.search(doc.text.split("\n")[number - 1]).group(1)
        sites = defs[slug]
        if len(sites) > 1:
            others = ", ".join(f"{run.rel(p)}:{n}" for p, n in sites if (p, n) != (doc.path, number))
            run.fail("bzh-id-integrity", doc, number, f"{prefix}:{slug}: defined more than once (also {others})",
                     "Keep the id on the rule's one heading; drop it from the other.", is_line=True)

    link_ends = {end: target for _, end, target in doc.links}
    for start, end, target in doc.links:
        if SCHEME_RE.match(target) or target.startswith("/"):
            continue
        path, _, fragment = target.partition("#")
        resolved = (doc.path.parent / path).resolve() if path else doc.path
        if path and not resolved.exists():
            run.fail("reference-links", doc, start, f"{target}: no such path from {run.rel(doc.path.parent)}",
                     "Point the link at an existing file, or remove it.")
            continue
        if fragment:
            check_fragment(run, doc, start, resolved, fragment, path or doc.path.name)

    for m in re.finditer("§", doc.nocode):
        target = section_target(run, doc, m.start(), repo, link_ends)
        if target is not None and target.is_file():
            check_section(run, doc, m.start(), target, run.rel(target) if target != doc.path else doc.path.name, id_re)

    seen_missing: set[str] = set()
    for m in PATH_NOTATION_RE.finditer(doc.text):
        module, path = m.group(1), m.group(2).rstrip(".:")
        if any(c in path for c in "<*") or "..." in path or module == prefix:
            continue
        root = run.module_root(module, repo)
        if root is None:
            if module != REPO_NAME and not run.workspace_mode and module not in run.warned_modules:
                run.warned_modules.add(module)
                emit("path-notation-targets", "warn", f"{module}: not resolved — no WINTER_WORKSPACE_DIR with .winter/ to hold its root",
                     file=run.rel(doc.path), line=doc.line_of(m.start()),
                     remediation="Run with WINTER_WORKSPACE_DIR set to the workspace root to resolve this module's paths.")
            continue
        file_part, _, fragment = path.partition("#")
        target = root / file_part.lstrip("/")
        shown = f"{module}:{file_part}"
        if not target.exists():
            run.fail("path-notation-targets", doc, m.start(), f"{shown}: no such path under {run.rel(root)}",
                     "Point the notation at an existing file, or remove it.")
        elif fragment:
            check_fragment(run, doc, m.start(), target, fragment, shown)

    check_routing(run, doc, repo, routed)


def nearest_hub(path: Path, repo: Path) -> Path | None:
    directory = path.parent.parent if path.name == "index.md" else path.parent
    index = directory / "index.md"
    if index.is_file():
        return index
    sibling = directory.parent / f"{directory.name}.md"
    return sibling if directory != repo and sibling.is_file() else None


def check_routing(run: Run, doc: Doc, repo: Path, routed: dict[Path, set[Path]]) -> None:
    path = doc.path
    if path.parent == repo and path.name in ("index.md", "README.md"):
        return
    hub = nearest_hub(path, repo)
    if hub is None:
        run.fail("hub-routing", doc, 1, "no hub: neither index.md in its directory nor a spoke-dir sibling <dir>.md",
                 "Add the hub that routes this file, or move the file under one.", is_line=True)
        return
    if hub not in routed:
        hub_doc = run.doc(hub)
        routed[hub] = {(hub.parent / t.split("#", 1)[0]).resolve() for _, _, t in hub_doc.links
                       if not SCHEME_RE.match(t) and not t.startswith("/") and not t.startswith("#")}
    if path not in routed[hub]:
        run.fail("hub-routing", doc, 1, f"not linked from its hub {run.rel(hub)}",
                 f"Add a row linking {path.name} to {run.rel(hub)}.", is_line=True)


def main() -> int:
    argv = sys.argv[1:]
    gate = "--gate" in argv
    paths = [p.resolve() for p in scope_paths([a for a in argv if a != "--gate"])]
    workspace_dir = os.environ.get("WINTER_WORKSPACE_DIR")
    workspace = Path(workspace_dir or os.getcwd()).resolve()
    run = Run(workspace, bool(workspace_dir) and (workspace / ".winter").is_dir())

    scopes: dict[Path, tuple[dict, list[Path]]] = {}
    for path in paths:
        owner = owning_repo(path)
        if owner is not None:
            scopes.setdefault(owner[0].resolve(), (owner[1], []))[1].append(path)

    for repo, (manifest, scoped) in sorted(scopes.items()):
        prefix = manifest.get("prefix", "bzh")
        id_re = re.compile(rf"\s*\(`{re.escape(prefix)}:({SLUG_TAIL})`\)\s*$")
        files = markdown_files(repo)
        defs: dict[str, list[tuple[Path, int]]] = {}
        for file in files:
            for number, heading in run.doc(file).headings:
                m = id_re.search(heading)
                if m:
                    defs.setdefault(m.group(1), []).append((file.resolve(), number))
        routed: dict[Path, set[Path]] = {}
        for file in files:
            if any(file.resolve() == s or s in file.resolve().parents for s in scoped):
                check_doc(run, run.doc(file), repo, prefix, defs, routed, id_re)
    return 1 if gate and run.failed else 0


if __name__ == "__main__":
    sys.exit(main())
