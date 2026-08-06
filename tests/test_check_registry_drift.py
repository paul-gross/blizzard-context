#!/usr/bin/env python3
"""Stdlib-only fixture tests for scripts/check-registry-drift.py.

Builds fake registry-markdown trees and fake checkouts under ``tempfile``
directories and asserts each check's finding shape, including one silent
case per exclusion class named in the plan. Collection-backed checks (B1,
B2, C) mostly run against a canned ``collect_cache`` dict, decoupled from
how it is obtained; one dedicated test proves the stub-interpreter plumbing
(``_resolve_interpreter`` / ``_collect``) itself, so no real pytest run is
needed anywhere in this suite.
"""

from __future__ import annotations

import importlib.util
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check-registry-drift.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_registry_drift", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


drift = _load_module()


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def _shape(findings) -> list[tuple[str, str]]:
    return [(f.check, f.status) for f in findings]


def _messages(findings, check=None) -> list[str]:
    return [f.message for f in findings if check is None or f.check == check]


# --------------------------------------------------------------------------
# Check A — cited-path existence
# --------------------------------------------------------------------------


class CheckATests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.blizzard = self.root / "blizzard"
        self.blizzard_mock = self.root / "blizzard-mock"
        (self.blizzard / "tests").mkdir(parents=True)
        (self.blizzard_mock / "src").mkdir(parents=True)
        self.checkouts = {"blizzard": self.blizzard, "blizzard-mock": self.blizzard_mock}

    def _run(self, text: str, collect_cache=None):
        return drift.check_A([("verification/x.md", text)], self.checkouts, collect_cache or {})

    def test_missing_path_fails(self):
        text = "See `tests/test_does_not_exist.py` for detail."
        findings = self._run(text)
        self.assertEqual(_shape(findings), [("A", "fail")])

    def test_repo_prefixed_literals_resolve_in_named_checkout(self):
        _write(self.blizzard / "src" / "blizzard" / "x.py", "# x\n")
        _write(self.blizzard_mock / "src" / "y.py", "# y\n")
        text = (
            "`blizzard/src/blizzard/x.py` and `blizzard-mock/src/y.py` both resolve."
        )
        findings = self._run(text)
        self.assertEqual(findings, [])

    def test_scope_preferred_falls_back_to_sibling_checkout_silently(self):
        # Cited under a blizzard-mock-scoped section but the file only
        # exists in the blizzard checkout — the fallback is load-bearing.
        _write(self.blizzard / "tests" / "test_seed.py", "def test_x(): pass\n")
        text = "### blizzard-mock:manual-seeded-board\ncites `tests/test_seed.py` here."
        findings = self._run(text)
        self.assertEqual(findings, [])

    def test_glob_literal_resolves(self):
        _write(self.blizzard / "src" / "graphs" / "default" / "graph.yaml", "x: 1\n")
        text = "`src/graphs/*/graph.yaml`"
        findings = self._run(text)
        self.assertEqual(findings, [])

    def test_brace_literal_requires_every_expansion(self):
        _write(self.blizzard / "openapi" / "hub.openapi.json", "{}")
        text = "`openapi/{hub,runner}.openapi.json`"
        findings = self._run(text)
        self.assertEqual(_shape(findings), [("A", "fail")])

    def test_node_id_path_resolved_function_matched(self):
        _write(self.blizzard / "tests" / "test_store.py", "def test_migrate(): pass\n")
        collect_cache = {"unit": ["tests/test_store.py::test_migrate"]}
        text = "`tests/test_store.py::test_migrate`"
        findings = self._run(text, collect_cache)
        self.assertEqual(findings, [])

    def test_node_id_function_half_mismatch_fails(self):
        _write(self.blizzard / "tests" / "test_store.py", "def test_migrate(): pass\n")
        collect_cache = {"unit": ["tests/test_store.py::test_migrate"]}
        text = "`tests/test_store.py::test_migrateX`"
        findings = self._run(text, collect_cache)
        self.assertEqual(_shape(findings), [("A", "fail")])

    def test_embedded_command_line_non_path_tokens_stay_silent(self):
        _write(self.blizzard / "scripts" / "prose_density.py", "# x\n")
        text = "`scripts/prose_density.py check src tests ../blizzard-mock/src`"
        findings = self._run(text)
        self.assertEqual(findings, [])

    def test_angle_bracket_placeholder_excluded(self):
        # Rooted, so it would be a candidate path (and fail — no such literal
        # file exists) were the placeholder not excluded first.
        text = "`tests/e2e/<module>.py`"
        findings = self._run(text)
        self.assertEqual(findings, [])

    def test_rootless_wildcard_excluded(self):
        text = "`*.shell-sweep.spec.ts`"
        findings = self._run(text)
        self.assertEqual(findings, [])

    def test_wire_route_and_relative_dotdot_token_excluded(self):
        text = "`/api/fleet/events` and `_drive/complete` and `../blizzard-mock/src`"
        findings = self._run(text)
        self.assertEqual(findings, [])


# --------------------------------------------------------------------------
# Check B1 — every cited test file lives in some tier
# --------------------------------------------------------------------------


class CheckB1Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.blizzard = Path(self.tmp.name) / "blizzard"
        (self.blizzard / "tests").mkdir(parents=True)

    def _run(self, text: str, collect_cache):
        return drift.check_B1([("verification/x.md", text)], self.blizzard, collect_cache)

    def test_markerless_file_fails(self):
        _write(self.blizzard / "tests" / "test_bare.py", "def test_x(): pass\n")
        collect_cache = {"unit": [], "component": [], "service": [], "crash_sweep": [], "journey": [], "e2e": []}
        findings = self._run("`tests/test_bare.py`", collect_cache)
        self.assertEqual(_shape(findings), [("B1", "fail")])

    def test_known_unmarked_exemption_warns_not_fails(self):
        _write(self.blizzard / "tests" / "test_intended_migration_apply.py", "def test_x(): pass\n")
        collect_cache = {"unit": [], "component": [], "service": [], "crash_sweep": [], "journey": [], "e2e": []}
        findings = self._run("`tests/test_intended_migration_apply.py`", collect_cache)
        self.assertEqual(_shape(findings), [("B1", "warn")])

    def test_conftest_is_silent(self):
        _write(self.blizzard / "tests" / "conftest.py", "# fixtures\n")
        collect_cache = {"unit": [], "component": [], "service": [], "crash_sweep": [], "journey": [], "e2e": []}
        findings = self._run("`tests/conftest.py`", collect_cache)
        self.assertEqual(findings, [])

    def test_node_id_citation_path_half_checked(self):
        _write(self.blizzard / "tests" / "test_marked.py", "def test_x(): pass\n")
        collect_cache = {"unit": ["tests/test_marked.py::test_x"], "component": [], "service": [], "crash_sweep": [], "journey": [], "e2e": []}
        findings = self._run("`tests/test_marked.py::test_x`", collect_cache)
        self.assertEqual(findings, [])

    def test_blizzard_mock_scoped_citation_silent(self):
        # File lives only outside the blizzard checkout -> B1 does not resolve it, so it stays silent.
        collect_cache = {"unit": [], "component": [], "service": [], "crash_sweep": [], "journey": [], "e2e": []}
        findings = self._run("`test_idp.py`", collect_cache)
        self.assertEqual(findings, [])


# --------------------------------------------------------------------------
# Check B2 — own-tier agreement
# --------------------------------------------------------------------------


class CheckB2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.blizzard = Path(self.tmp.name) / "blizzard"
        (self.blizzard / "tests").mkdir(parents=True)

    def test_own_tier_mismatch_fails(self):
        _write(self.blizzard / "tests" / "test_gate.py", "def test_x(): pass\n")
        text = "### blizzard:unit-test\n\nThe checks-gate agreement guard (`tests/test_gate.py`) drives both sides.\n"
        collect_cache = {"unit": [], "component": ["tests/test_gate.py::test_x"]}
        findings = drift.check_B2("verification/commands.md", text, self.blizzard, collect_cache)
        self.assertEqual(_shape(findings), [("B2", "fail")])

    def test_cross_tier_named_sentence_classified_not_failed(self):
        _write(self.blizzard / "tests" / "test_gate.py", "def test_x(): pass\n")
        text = (
            "### blizzard:component-test\n\n"
            "Its unit-tier sibling `tests/test_gate.py` pins the accept end.\n"
        )
        collect_cache = {"unit": [], "component": []}
        findings = drift.check_B2("verification/commands.md", text, self.blizzard, collect_cache)
        self.assertEqual(_shape(findings), [("B2", "pass")])


# --------------------------------------------------------------------------
# Check C — e2e roster completeness
# --------------------------------------------------------------------------


class CheckCTests(unittest.TestCase):
    def test_both_directions_and_orphan_bullet(self):
        e2e_text = (
            "# roster\n\n"
            "lead paragraph.\n\n"
            "### module_a\n\n"
            "- `test_documented_a` — covers a.\n\n"
            "### module_b\n\n"
            "- `test_stale_bullet` — no longer real.\n\n"
            "## Wave-by-wave coverage rollup\n\n"
            "- `test_orphan` — has no owning module heading.\n"
        )
        collect_cache = {
            "e2e": [
                "tests/e2e/module_a.py::test_documented_a",
                "tests/e2e/module_a.py::test_undocumented_a",
                "tests/e2e/module_c.py::test_undocumented_c",
            ]
        }
        findings = drift.check_C("verification/e2e-scenarios.md", e2e_text, collect_cache)
        checks = _shape(findings)
        self.assertEqual(len(checks), 4)
        self.assertTrue(all(c == ("C", "fail") for c in checks))
        messages = " ".join(_messages(findings))
        self.assertIn("test_undocumented_a", messages)
        self.assertIn("test_undocumented_c", messages)
        self.assertIn("test_stale_bullet", messages)
        self.assertIn("test_orphan", messages)
        self.assertIn("no owning ### module heading", messages)

    def test_matching_roster_is_silent(self):
        e2e_text = "### module_a\n\n- `test_a` — covers a.\n"
        collect_cache = {"e2e": ["tests/e2e/module_a.py::test_a"]}
        findings = drift.check_C("verification/e2e-scenarios.md", e2e_text, collect_cache)
        self.assertEqual(findings, [])

    def test_parametrized_nodes_documented_by_one_bare_bullet_is_silent(self):
        e2e_text = "### module_a\n\n- `test_param` — covers both cases.\n"
        collect_cache = {
            "e2e": [
                "tests/e2e/module_a.py::test_param[1]",
                "tests/e2e/module_a.py::test_param[2]",
            ]
        }
        findings = drift.check_C("verification/e2e-scenarios.md", e2e_text, collect_cache)
        self.assertEqual(findings, [])

    def test_parametrized_node_with_no_bullet_names_the_bare_function(self):
        e2e_text = "### module_a\n\nlead paragraph, no bullets yet.\n"
        collect_cache = {"e2e": ["tests/e2e/module_a.py::test_param[1]"]}
        findings = drift.check_C("verification/e2e-scenarios.md", e2e_text, collect_cache)
        self.assertEqual(_shape(findings), [("C", "fail")])
        self.assertIn("test_param", findings[0].message)
        self.assertNotIn("test_param[1]", findings[0].message)


# --------------------------------------------------------------------------
# Check C2 — shell-sweep roster
# --------------------------------------------------------------------------


class CheckC2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.blizzard = Path(self.tmp.name) / "blizzard"
        self.projects = self.blizzard / "web" / "projects"
        self.projects.mkdir(parents=True)

    def test_both_directions_screenshot_dir_and_naming_pattern_silent(self):
        _write(self.projects / "hub" / "a.shell-sweep.spec.ts", "// spec\n")
        _write(self.projects / "hub" / "b.shell-sweep.spec.ts", "// spec\n")
        # A directory sharing a spec's basename under __screenshots__ — must not
        # count as a phantom unlisted spec once filtered to regular files.
        (self.projects / "hub" / "__screenshots__" / "a.shell-sweep.spec.ts").mkdir(parents=True)

        commands_text = (
            "### web:shell-sweep\n\n"
            "`a.shell-sweep.spec.ts` covers the header. Every `*.shell-sweep.spec.ts` "
            "file is excluded from the default run.\n"
        )
        findings = drift.check_C2("verification/commands.md", commands_text, self.blizzard)
        # b.shell-sweep.spec.ts is on disk but uncited -> exactly one fail,
        # not two (the screenshots directory must not count).
        self.assertEqual(_shape(findings), [("C2", "fail")])
        self.assertIn("b.shell-sweep.spec.ts", findings[0].message)

    def test_cited_but_missing_from_disk_fails(self):
        commands_text = "### web:shell-sweep\n\n`missing.shell-sweep.spec.ts` covers nothing real.\n"
        findings = drift.check_C2("verification/commands.md", commands_text, self.blizzard)
        self.assertEqual(_shape(findings), [("C2", "fail")])
        self.assertIn("not found on disk", findings[0].message)

    def test_fully_matching_roster_is_silent(self):
        _write(self.projects / "hub" / "a.shell-sweep.spec.ts", "// spec\n")
        commands_text = "### web:shell-sweep\n\n`a.shell-sweep.spec.ts` covers the header.\n"
        findings = drift.check_C2("verification/commands.md", commands_text, self.blizzard)
        self.assertEqual(findings, [])


# --------------------------------------------------------------------------
# Check D / D2 — task-name resolution and task-command agreement
# --------------------------------------------------------------------------


class CheckDTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.blizzard = Path(self.tmp.name) / "blizzard"
        self.blizzard.mkdir(parents=True)
        _write(
            self.blizzard / "mise.toml",
            (
                '[tasks.gate]\n'
                'run = "./scripts/ci-gate.sh"\n\n'
                '[tasks.journey]\n'
                'run = "BLIZZARD_JOURNEY=1 uv run pytest -m journey tests/journey/"\n\n'
                '[tasks.prose-check]\n'
                'run = "uv run python scripts/prose_density.py check src tests ../blizzard-mock/src"\n\n'
                '[tasks.image-smoke]\n'
                'run = "./scripts/image-smoke.sh"\n'
            ),
        )
        (self.blizzard / "web").mkdir(parents=True)
        _write(self.blizzard / "web" / "package.json", '{"scripts": {"lint": "ng lint"}}')

    def test_unknown_mise_task_fails(self):
        text = "Run `mise run does-not-exist` first."
        findings = drift.check_D([("verification/x.md", text)], self.blizzard)
        self.assertEqual(_shape(findings), [("D", "fail")])

    def test_unknown_npm_script_fails(self):
        text = "Run `npm run does-not-exist` in web/."
        findings = drift.check_D([("verification/x.md", text)], self.blizzard)
        self.assertEqual(_shape(findings), [("D", "fail")])

    def test_known_task_and_script_silent(self):
        text = "`mise run gate` and `npm run lint` both resolve."
        findings = drift.check_D([("verification/x.md", text)], self.blizzard)
        self.assertEqual(findings, [])

    def _d2(self, text: str):
        return drift.check_D2([("verification/x.md", text)], self.blizzard)

    def test_exact_match_silent(self):
        text = "`mise run gate` (`./scripts/ci-gate.sh`)"
        self.assertEqual(self._d2(text), [])

    def test_strict_prefix_warns(self):
        text = "`mise run journey` (`BLIZZARD_JOURNEY=1 uv run pytest -m journey`)"
        findings = self._d2(text)
        self.assertEqual(_shape(findings), [("D2", "warn")])

    def test_missing_runner_prefix_fails(self):
        text = "`mise run prose-check` (`scripts/prose_density.py check src tests ../blizzard-mock/src`)"
        findings = self._d2(text)
        self.assertEqual(_shape(findings), [("D2", "fail")])

    def test_leading_dot_slash_difference_silent(self):
        text = "`mise run image-smoke` (`scripts/image-smoke.sh`)"
        self.assertEqual(self._d2(text), [])

    def test_env_assignment_reordering_silent(self):
        _write(
            self.blizzard / "mise.toml",
            '[tasks.crash-sweep-ci]\n'
            'run = "BLIZZARD_CRASH_SWEEP=1 BLIZZARD_CRASH_SWEEP_CI=1 uv run pytest -m crash_sweep tests/crash/"\n',
        )
        text = (
            "`BLIZZARD_CRASH_SWEEP_CI=1 BLIZZARD_CRASH_SWEEP=1 uv run pytest -m crash_sweep tests/crash/` "
            "(`mise run crash-sweep-ci`)"
        )
        self.assertEqual(self._d2(text), [])

    def test_toml_assignment_span_not_paired(self):
        text = "`mise run e2e` therefore `depends = [\"web-build\"]` — do not skip it."
        self.assertEqual(self._d2(text), [])

    def test_assignments_only_span_not_paired(self):
        text = "the bounded CI profile (`mise run crash-sweep-ci`) — documented span `BLIZZARD_CRASH_SWEEP_CI=1`"
        self.assertEqual(self._d2(text), [])


# --------------------------------------------------------------------------
# run() — registry-input findings and --gate's skipped-check semantics
# --------------------------------------------------------------------------


class RunRegistryInputAndGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo_root = Path(self.tmp.name) / "repo"
        _write(self.repo_root / "verification" / "blizzard.md", "# blizzard\n")
        _write(self.repo_root / "verification" / "blizzard" / "commands.md", "# commands\n")
        _write(self.repo_root / "verification" / "blizzard" / "e2e-scenarios.md", "# e2e\n")
        self.blizzard_mock = Path(self.tmp.name) / "blizzard-mock"
        self.blizzard_mock.mkdir()
        # Never a real checkout — keeps every check gated behind `if "blizzard"
        # in checkouts` skipped, with no interpreter/subprocess ever invoked.
        self.missing_blizzard = Path(self.tmp.name) / "no-such-blizzard-checkout"

    def test_missing_registry_file_emits_a_finding(self):
        (self.repo_root / "verification" / "blizzard" / "commands.md").unlink()
        findings, _ = drift.run(self.repo_root, self.missing_blizzard, self.blizzard_mock, gate=False)
        messages = _messages(findings)
        self.assertTrue(any("commands.md" in m and "not found" in m for m in messages))

    def test_gate_is_nonzero_when_a_check_is_skipped(self):
        _, exit_code = drift.run(self.repo_root, self.missing_blizzard, self.blizzard_mock, gate=True)
        self.assertEqual(exit_code, 1)

    def test_plain_run_stays_exit_0_with_the_same_skipped_check(self):
        _, exit_code = drift.run(self.repo_root, self.missing_blizzard, self.blizzard_mock, gate=False)
        self.assertEqual(exit_code, 0)


# --------------------------------------------------------------------------
# run() — effectiveness gating: a check that ran against a partial or absent
# `collect_cache`/task file lands in `skipped`, never a silent pass, so
# `--gate` refuses green on it exactly like a check that never ran.
# --------------------------------------------------------------------------


class RunEffectivenessGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo_root = Path(self.tmp.name) / "repo"
        _write(self.repo_root / "verification" / "blizzard.md", "# blizzard\n")
        _write(self.repo_root / "verification" / "blizzard" / "commands.md", "# commands\n")
        _write(self.repo_root / "verification" / "blizzard" / "e2e-scenarios.md", "# e2e\n")
        self.blizzard_mock = Path(self.tmp.name) / "blizzard-mock"
        self.blizzard_mock.mkdir()
        self.blizzard = Path(self.tmp.name) / "blizzard"
        (self.blizzard / "tests").mkdir(parents=True)
        _write(self.blizzard / "mise.toml", '[tasks.gate]\nrun = "./scripts/ci-gate.sh"\n')
        _write(self.blizzard / "web" / "package.json", '{"scripts": {}}')

    def _write_stub_interpreter(self, *, failing_markers: frozenset[str] = frozenset()) -> None:
        venv_bin = self.blizzard / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        stub = venv_bin / "python"
        stub.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "m_indices = [i for i, a in enumerate(sys.argv) if a == '-m']\n"
            "marker = sys.argv[m_indices[-1] + 1]\n"
            f"if marker in {sorted(failing_markers)!r}:\n"
            "    sys.exit(2)\n"
            "print('1 test collected')\n"
        )
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)

    def test_interpreter_unresolvable_with_a_present_checkout_gates_nonzero(self):
        # No .venv and no `uv` on PATH — `_resolve_interpreter` returns None even
        # though the blizzard checkout itself is present.
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = ""
        try:
            findings, exit_code = drift.run(self.repo_root, self.blizzard, self.blizzard_mock, gate=True)
        finally:
            os.environ["PATH"] = old_path
        self.assertEqual(exit_code, 1)
        self.assertTrue(any("no python interpreter resolvable" in (f.message or "") for f in findings))

    def test_one_marker_collection_failure_gates_nonzero(self):
        self._write_stub_interpreter(failing_markers=frozenset({"e2e"}))
        findings, exit_code = drift.run(self.repo_root, self.blizzard, self.blizzard_mock, gate=True)
        self.assertEqual(exit_code, 1)
        self.assertTrue(any("collection failed for `-m e2e`" in (f.message or "") for f in findings))
        # C3 — a fail derived from that same partial collect_cache is a
        # degraded run inventing registry breakage, never a real finding.
        self.assertEqual([f for f in findings if f.check == "B1" and f.status == "fail"], [])

    def test_malformed_mise_toml_emits_a_d2_warn_and_gates_nonzero(self):
        self._write_stub_interpreter()
        _write(self.blizzard / "mise.toml", "not valid toml {{{\n")
        findings, exit_code = drift.run(self.repo_root, self.blizzard, self.blizzard_mock, gate=True)
        self.assertEqual(exit_code, 1)
        d2_warns = [f for f in findings if f.check == "D2" and f.status == "warn"]
        self.assertTrue(any("could not read" in (f.message or "") and "mise.toml" in (f.message or "") for f in d2_warns))

    @unittest.skipIf(os.geteuid() == 0, "root bypasses file permission checks")
    def test_permission_denied_mise_toml_emits_a_d2_warn_and_gates_nonzero(self):
        self._write_stub_interpreter()
        mise_path = self.blizzard / "mise.toml"
        mise_path.chmod(0)
        self.addCleanup(mise_path.chmod, 0o644)
        findings, exit_code = drift.run(self.repo_root, self.blizzard, self.blizzard_mock, gate=True)
        self.assertEqual(exit_code, 1)
        d2_warns = [f for f in findings if f.check == "D2" and f.status == "warn"]
        self.assertTrue(any("could not read" in (f.message or "") and "mise.toml" in (f.message or "") for f in d2_warns))

    def test_missing_blizzard_mock_gates_nonzero_with_check_a_flagged_skipped(self):
        # M1 — an absent blizzard-mock checkout leaves blizzard-mock-scoped
        # citations unresolvable in check A (downgraded to warn, never a
        # fail), so A never ran to completion and must not gate green.
        self._write_stub_interpreter()
        missing_mock = Path(self.tmp.name) / "no-such-blizzard-mock"
        findings, exit_code = drift.run(self.repo_root, self.blizzard, missing_mock, gate=True)
        self.assertEqual(exit_code, 1)
        self.assertTrue(
            any(
                f.check == "A" and "blizzard-mock" in (f.message or "") and "skipped" in (f.message or "")
                for f in findings
            )
        )

    def test_stub_interpreter_exit_1_treated_as_failed_collection(self):
        # M2 — `python -m pytest` on a venv without pytest installed exits 1
        # ("No module named pytest"), which must not read as a clean empty
        # collection.
        venv_bin = self.blizzard / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        stub = venv_bin / "python"
        stub.write_text("#!/usr/bin/env python3\nimport sys\nsys.exit(1)\n")
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        _write(
            self.repo_root / "verification" / "blizzard.md",
            "# blizzard\n\ncites `tests/test_something.py` for detail.\n",
        )
        _write(self.blizzard / "tests" / "test_something.py", "def test_x(): pass\n")
        findings, exit_code = drift.run(self.repo_root, self.blizzard, self.blizzard_mock, gate=True)
        self.assertEqual(exit_code, 1)
        self.assertTrue(any("collection failed" in (f.message or "") for f in findings))
        self.assertEqual([f for f in findings if f.check == "B1" and f.status == "fail"], [])

    def test_fully_effective_run_gates_zero(self):
        # C4 — pins the green path: a fully effective run against a fixture
        # with both checkouts present, a stub interpreter that always
        # succeeds, and a consistent registry must gate exit 0, so an
        # always-red regression in the effectiveness bookkeeping is caught.
        self._write_stub_interpreter()
        findings, exit_code = drift.run(self.repo_root, self.blizzard, self.blizzard_mock, gate=True)
        self.assertEqual(exit_code, 0)
        self.assertEqual([f for f in findings if f.status == "fail"], [])


# --------------------------------------------------------------------------
# Check E — no ordinal or cardinal spec identification
# --------------------------------------------------------------------------


class CheckE1Tests(unittest.TestCase):
    def _e(self, text: str):
        return drift.check_E([("verification/x.md", text)])

    def test_scenario_paren_digit_fails(self):
        findings = self._e("The board answers scenario (6) directly.")
        self.assertIn(("E1a", "fail"), _shape(findings))

    def test_scenario_hyphen_digit_fails(self):
        findings = self._e("over the scenario-(11) build/review/build shape")
        self.assertEqual([f for f in findings if f.check == "E1a"] != [], True)

    def test_ordinal_scenario_named_module_silent(self):
        findings = self._e("scenario `test_migration_e2e.py` exercises the choice")
        self.assertEqual([f for f in findings if f.check == "E1a"], [])

    def test_kill9_module_digit_silent(self):
        findings = self._e("its crash-tier companion is `test_kill9_sweep.py`")
        self.assertEqual([f for f in findings if f.check == "E1a"], [])

    def test_fenced_scenario_command_silent(self):
        text = "prose before\n\n```bash\nblizzard-mock-data scenario board --chunks 6\n```\n"
        findings = self._e(text)
        self.assertEqual([f for f in findings if f.check == "E1a"], [])

    def test_inline_span_scenario_command_silent(self):
        text = "run `blizzard-mock-data scenario board --chunks 9` directly."
        findings = self._e(text)
        self.assertEqual([f for f in findings if f.check == "E1a"], [])

    def test_viewport_unit_suffix_silent(self):
        findings = self._e("gives any browser scenario a real ~390px page")
        self.assertEqual([f for f in findings if f.check == "E1a"], [])

    def test_registry_link_silent(self):
        findings = self._e("read the [registry](./blizzard/e2e-scenarios.md#test_escalation_e2e) entry")
        self.assertEqual([f for f in findings if f.check == "E1a"], [])

    def test_five_specs_fails_via_numeral(self):
        findings = self._e("runs five specs under real-browser mode")
        self.assertEqual(_shape(findings), [("E1b", "fail")])

    def test_two_scenarios_fails_via_numeral(self):
        findings = self._e("two scenarios over the fail-cycle shape")
        self.assertEqual(_shape(findings), [("E1b", "fail")])


class CheckE2Tests(unittest.TestCase):
    def _e(self, text: str):
        return drift.check_E([("verification/x.md", text)])

    def test_orphan_paren_int_fails(self):
        findings = self._e("unlike (6) it needs no runner")
        self.assertEqual(_shape(findings), [("E2", "fail")])

    def test_ascending_run_from_one_silent(self):
        findings = self._e("Steps: (1) start; (2) drive; (3) assert.")
        self.assertEqual([f for f in findings if f.check == "E2"], [])

    def test_two_ascending_runs_on_adjacent_lines_silent(self):
        text = "Setup: (1) one; (2) two; (3) three.\nSteps: (1) four; (2) five; (3) six; (4) seven.\n"
        findings = self._e(text)
        self.assertEqual([f for f in findings if f.check == "E2"], [])

    def test_inline_code_span_orphan_silent(self):
        findings = self._e("the vitest failure reads `node history's left (8) is not beside it`")
        self.assertEqual([f for f in findings if f.check == "E2"], [])


# --------------------------------------------------------------------------
# Stub interpreter — proves _resolve_interpreter / _collect against a fake
# pytest without ever shelling out to a real one.
# --------------------------------------------------------------------------


class StubInterpreterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.blizzard = Path(self.tmp.name) / "blizzard"
        venv_bin = self.blizzard / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        stub = venv_bin / "python"
        stub.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "m_indices = [i for i, a in enumerate(sys.argv) if a == '-m']\n"
            "marker = sys.argv[m_indices[-1] + 1]\n"
            "canned = {\n"
            "    'unit': ['tests/test_a.py::test_x'],\n"
            "    'component': ['tests/test_b.py::test_y'],\n"
            "}\n"
            "for node in canned.get(marker, []):\n"
            "    print(node)\n"
            "print('2 tests collected')\n"
        )
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        self.blizzard.mkdir(exist_ok=True)

    def test_resolve_and_collect_against_the_stub(self):
        interpreter = drift._resolve_interpreter(self.blizzard)
        self.assertIsNotNone(interpreter)
        self.assertTrue(interpreter[0].endswith(".venv/bin/python"))
        nodes = drift._collect(interpreter, self.blizzard, "unit")
        self.assertEqual(nodes, ["tests/test_a.py::test_x"])
        nodes = drift._collect(interpreter, self.blizzard, "component")
        self.assertEqual(nodes, ["tests/test_b.py::test_y"])

    def test_no_interpreter_resolves_to_none(self):
        empty = Path(self.tmp.name) / "no-venv-here"
        empty.mkdir()
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = ""
        try:
            self.assertIsNone(drift._resolve_interpreter(empty))
        finally:
            os.environ["PATH"] = old_path


if __name__ == "__main__":
    unittest.main()
