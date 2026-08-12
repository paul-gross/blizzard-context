#!/usr/bin/env python3
"""Tests for scripts/lint-markdown-style.py — stdlib-only, hermetic.

The winter-lint contribution is exercised as a subprocess with the lint env
contract, against throwaway repos and stub `dprint`/`rumdl` executables placed
on PATH, so no real tool install is needed. Mirrors the fixture style of
test_check_registry_drift.py.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "lint-markdown-style.py"


def write_stub(bin_dir: Path, name: str, stdout: str, exit_code: int) -> None:
    stub = bin_dir / name
    stub.write_text("#!/bin/sh\ncat <<'EOF'\n" + stdout + "EOF\nexit " + str(exit_code) + "\n")
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)


def run_check(paths: list[Path], workspace: Path, bin_dir: Path | None) -> tuple[list[dict], int]:
    env = dict(os.environ)
    env["WINTER_WORKSPACE_DIR"] = str(workspace)
    env["WINTER_LINT_PATHS"] = "\n".join(str(p) for p in paths)
    env["WINTER_LINT_SCOPE"] = "repo"
    env["PATH"] = (str(bin_dir) + os.pathsep if bin_dir else "") + "/usr/bin:/bin"
    proc = subprocess.run([sys.executable, str(SCRIPT)], env=env, capture_output=True, text=True)
    findings = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    return findings, proc.returncode


class LintMarkdownStyleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        self.repo = self.workspace / "repo"
        self.repo.mkdir()
        self.bin = self.workspace / "bin"
        self.bin.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def configure(self, dprint: bool = True, rumdl: bool = True) -> None:
        if dprint:
            (self.repo / "dprint.json").write_text("{}\n")
        if rumdl:
            (self.repo / ".rumdl.toml").write_text("[global]\n")

    def test_violations_become_fail_findings(self) -> None:
        self.configure()
        (self.repo / "doc.md").write_text("x\n")
        write_stub(self.bin, "dprint", f"from {self.repo}/doc.md:\n1 1| x\n", 20)
        write_stub(self.bin, "rumdl", "doc.md:12:1: [MD013] Line length 130 exceeds 120 characters [*]\n", 1)
        findings, code = run_check([self.repo], self.workspace, self.bin)
        self.assertEqual(code, 0)
        by_check = {f["check"]: f for f in findings}
        self.assertEqual(by_check["markdown-format"]["status"], "fail")
        self.assertEqual(by_check["markdown-format"]["file"], "repo/doc.md")
        self.assertEqual(by_check["markdown-lint"]["status"], "fail")
        self.assertEqual(by_check["markdown-lint"]["file"], "repo/doc.md")
        self.assertEqual(by_check["markdown-lint"]["line"], 12)
        self.assertIn("MD013", by_check["markdown-lint"]["message"])

    def test_clean_run_emits_nothing(self) -> None:
        self.configure()
        write_stub(self.bin, "dprint", "", 0)
        write_stub(self.bin, "rumdl", "Success: No issues found in 1 file\n", 0)
        findings, code = run_check([self.repo], self.workspace, self.bin)
        self.assertEqual(code, 0)
        self.assertEqual(findings, [])

    def test_unconfigured_repo_is_silently_out_of_scope(self) -> None:
        (self.repo / "doc.md").write_text("x\n")
        findings, code = run_check([self.repo], self.workspace, self.bin)
        self.assertEqual(code, 0)
        self.assertEqual(findings, [])

    def test_missing_binaries_degrade_to_warn(self) -> None:
        self.configure()
        findings, code = run_check([self.repo], self.workspace, None)
        self.assertEqual(code, 0)
        self.assertEqual({f["status"] for f in findings}, {"warn"})
        self.assertEqual({f["check"] for f in findings}, {"markdown-format", "markdown-lint"})

    def test_changed_scope_files_route_to_owning_repo(self) -> None:
        self.configure()
        nested = self.repo / "docs"
        nested.mkdir()
        changed = nested / "note.md"
        changed.write_text("x\n")
        write_stub(self.bin, "dprint", "", 0)
        write_stub(self.bin, "rumdl", "docs/note.md:3:1: [MD047] File should end with a single newline character [*]\n", 1)
        findings, code = run_check([changed], self.workspace, self.bin)
        self.assertEqual(code, 0)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["file"], "repo/docs/note.md")
        # A changed file outside any configured repo stays silent.
        stray = self.workspace / "stray.md"
        stray.write_text("x\n")
        findings, _ = run_check([stray], self.workspace, self.bin)
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
