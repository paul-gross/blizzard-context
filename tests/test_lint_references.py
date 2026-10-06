#!/usr/bin/env python3
"""Tests for scripts/lint-references.py — stdlib-only, hermetic.

The winter-lint contribution is exercised as a subprocess with the lint env
contract against throwaway blizzard-context fixture repos. Each check is proven
by seeding one violation into a clean fixture and expecting that check, and only
that check, to turn red.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "lint-references.py"

CLEAN = {
    "winter-ext.toml": 'name = "blizzard-context"\nprefix = "bzh"\n',
    "index.md": "# Hub\n\n- [rules](./rules/index.md)\n- [spoke](./spoke.md)\n",
    "README.md": "# Front page\n",
    "rules/index.md": "# Rules\n\n- [one](./one.md)\n",
    "rules/one.md": (
        "# One\n\n## The rule body (`bzh:the-rule`)\n\nSee `bzh:the-rule` and [the hub](./index.md#rules)"
        " and [spoke](../spoke.md) §Spoke heading.\n\n```text\nbzh:fenced-only [x](./missing.md)\n```\n"
    ),
    "spoke.md": "# Spoke\n\n## Spoke heading\n\n- [leaf](./spoke/leaf.md)\n",
    "spoke/leaf.md": "# Leaf\n\n## Runner-level pause\n\nWraps §Runner-\nlevel pause, and a §Runner-level pause.\n",
}


def run_lint(paths: list[Path], workspace: Path, *, workspace_env: bool = True, gate: bool = False) -> tuple[list[dict], int]:
    env = dict(os.environ)
    env.pop("WINTER_WORKSPACE_DIR", None)
    if workspace_env:
        env["WINTER_WORKSPACE_DIR"] = str(workspace)
    env["WINTER_LINT_PATHS"] = "\n".join(str(p) for p in paths)
    env["WINTER_LINT_SCOPE"] = "repo"
    argv = [sys.executable, str(SCRIPT)] + (["--gate"] if gate else [])
    proc = subprocess.run(argv, env=env, capture_output=True, text=True)
    return [json.loads(line) for line in proc.stdout.splitlines() if line.strip()], proc.returncode


class LintReferencesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name).resolve()
        (self.workspace / ".winter" / "ext" / "canon").mkdir(parents=True)
        (self.workspace / ".winter" / "ext" / "canon" / "winter-ext.toml").write_text('name = "winter-canon"\n')
        (self.workspace / ".winter" / "ext" / "canon" / "rule-shape.md").write_text("# Rule shape\n")
        self.repo = self.workspace / "ctx"
        self.write(CLEAN)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, files: dict[str, str]) -> None:
        for name, body in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)

    def lint(self, **kwargs) -> list[dict]:
        findings, code = run_lint([self.repo], self.workspace, **kwargs)
        self.assertEqual(code, 0)
        return findings

    def fails(self, check: str, **kwargs) -> list[dict]:
        findings = self.lint(**kwargs)
        self.assertEqual({f["check"] for f in findings if f["status"] == "fail"}, {check}, findings)
        return [f for f in findings if f["status"] == "fail"]

    def test_clean_fixture_is_silent(self) -> None:
        self.assertEqual(self.lint(), [])

    def test_dangling_citation_fails(self) -> None:
        self.write({"rules/one.md": CLEAN["rules/one.md"] + "\nAlso `bzh:does-not-exist`.\n"})
        found = self.fails("bzh-id-integrity")
        self.assertEqual(len(found), 1)
        self.assertEqual((found[0]["file"], found[0]["line"]), ("ctx/rules/one.md", 11))
        self.assertIn("bzh:does-not-exist", found[0]["message"])
        self.assertIn("remediation", found[0])

    def test_duplicate_definition_fails_at_every_site(self) -> None:
        self.write({"rules/two.md": "# Two (`bzh:the-rule`)\n", "rules/index.md": CLEAN["rules/index.md"] + "- [two](./two.md)\n"})
        found = self.fails("bzh-id-integrity")
        self.assertEqual({f["file"] for f in found}, {"ctx/rules/one.md", "ctx/rules/two.md"})

    def test_broken_anchor_fails(self) -> None:
        self.write({"rules/one.md": CLEAN["rules/one.md"] + "\n[gone](./index.md#no-such-heading)\n"})
        found = self.fails("reference-links")
        self.assertIn("#no-such-heading", found[0]["message"])

    def test_shortened_section_heading_fails(self) -> None:
        self.write({"spoke.md": "# Spokes\n\n## Spoke heading in full\n\n- [leaf](./spoke/leaf.md)\n"})
        self.assertEqual({f["file"] for f in self.fails("reference-links")}, {"ctx/rules/one.md"})

    def test_section_after_a_named_target_is_not_a_same_file_citation(self) -> None:
        cited = (
            "\nSee `bzh:the-rule` §Not a heading here, `scripts/tool.py` §Also not here,"
            " and spoke.md §Not here either; bzh:the-rule §Nor this.\n"
        )
        self.write({"rules/one.md": CLEAN["rules/one.md"] + cited})
        self.assertEqual(self.lint(), [])

    def test_quoted_section_heading_resolves_against_a_real_heading(self) -> None:
        self.write({"rules/one.md": CLEAN["rules/one.md"] + '\nSee [spoke](../spoke.md) §"Spoke heading".\n'})
        self.assertEqual(self.lint(), [])

    def test_prose_preceded_same_file_section_with_a_missing_heading_fails(self) -> None:
        self.write({"rules/one.md": CLEAN["rules/one.md"] + "\nThe fix is under §No such heading.\n"})
        found = self.fails("reference-links")
        self.assertIn("§No such heading", found[0]["message"])

    def test_missing_link_target_fails(self) -> None:
        self.write({"rules/one.md": CLEAN["rules/one.md"] + "\n[gone](./nope.md)\n"})
        self.fails("reference-links")

    def test_unrouted_leaf_fails(self) -> None:
        self.write({"rules/orphan.md": "# Orphan\n"})
        found = self.fails("hub-routing")
        self.assertEqual(found[0]["file"], "ctx/rules/orphan.md")

    def test_leaf_with_no_hub_fails(self) -> None:
        self.write({"stray/leaf.md": "# Leaf\n"})
        self.assertIn("no hub", self.fails("hub-routing")[0]["message"])

    def test_unresolvable_own_path_fails_and_resolves_against_repo_root(self) -> None:
        self.write({"rules/one.md": CLEAN["rules/one.md"] + "\n`blizzard-context:/spoke.md#spoke-heading` is fine.\n"})
        self.assertEqual(self.lint(), [])
        self.write({"rules/one.md": CLEAN["rules/one.md"] + "\n`blizzard-context:/missing.md`\n"})
        self.assertIn("blizzard-context:/missing.md", self.fails("path-notation-targets")[0]["message"])

    def test_other_module_resolves_through_installed_manifest_name(self) -> None:
        self.write({"rules/one.md": CLEAN["rules/one.md"] + "\n`winter-canon:/rule-shape.md` `winter-canon:/gone.md` `unknown:/x.md`\n"})
        found = self.fails("path-notation-targets")
        self.assertEqual(len(found), 1)
        self.assertIn("winter-canon:/gone.md", found[0]["message"])

    def test_single_repo_mode_warns_once_per_module_and_never_fails(self) -> None:
        line = "\n`winter-canon:/a.md` `winter-canon:/b.md` `workspace:/c.md`\n"
        self.write({"rules/one.md": CLEAN["rules/one.md"] + line})
        findings = self.lint(workspace_env=False)
        self.assertEqual([f["status"] for f in findings], ["warn", "warn"])
        self.assertEqual({f["check"] for f in findings}, {"path-notation-targets"})
        self.assertEqual(len([f for f in findings if "winter-canon" in f["message"]]), 1)

    def test_paths_outside_a_blizzard_context_repo_produce_nothing(self) -> None:
        other = self.workspace / "other"
        other.mkdir()
        (other / "winter-ext.toml").write_text('name = "someone-else"\nprefix = "bzh"\n')
        (other / "doc.md").write_text("`bzh:nope` [x](./gone.md)\n")
        loose = self.workspace / "loose.md"
        loose.write_text("`bzh:nope`\n")
        findings, code = run_lint([other, loose], self.workspace)
        self.assertEqual((findings, code), ([], 0))

    def test_findings_are_confined_to_scoped_files(self) -> None:
        self.write({"rules/one.md": CLEAN["rules/one.md"] + "\n`bzh:nope`\n", "spoke.md": CLEAN["spoke.md"] + "\n`bzh:nope`\n"})
        findings, _ = run_lint([self.repo / "spoke.md"], self.workspace)
        self.assertEqual({f["file"] for f in findings}, {"ctx/spoke.md"})

    def test_gate_exits_nonzero_only_on_fail(self) -> None:
        self.assertEqual(run_lint([self.repo], self.workspace, gate=True)[1], 0)
        self.write({"rules/one.md": CLEAN["rules/one.md"] + "\n`bzh:nope`\n"})
        self.assertEqual(run_lint([self.repo], self.workspace, gate=True)[1], 1)


if __name__ == "__main__":
    unittest.main()
