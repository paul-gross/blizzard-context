# Tier rules — what a test at any tier is held to (`bzh:matrix-tier-rules`)

The standard the tests behind [../blizzard.md](../blizzard.md)'s [tier table](../blizzard.md#test-tiers) are written to.
The rules a change must land a companion for are [./companion-changes.md](./companion-changes.md); what makes a passing
test count as evidence is [./evidence.md](./evidence.md).

- **Service and e2e tests never spend real tokens and never touch the network.** The harness seam binds a mock coding
  harness; the work-source and delivery seams bind the mock GitHub forge; the workspace seam binds mocks or local
  fixtures.
- **One-sided service tests use the mock counterpart.** Runner service tests run against the mock hub; hub service tests
  against the mock runner — edge cases come from driving the mock's levers, not from contriving the real daemon into
  rare states.
- **Test data is set up through the mock-data CLI and fixtures** (`tool:mock-data`), not ad-hoc SQL.
- **Tests run against sqlite.** Postgres support is a configuration concern held by staying inside SQLAlchemy's portable
  surface (`bzh:sql-portable`), not a second test matrix.
- **A spawned daemon's output goes to a file, never to a pipe nothing drains (`bzh:daemon-stdout-to-file`).** The tiers
  that run real daemons — `blizzard:crash-sweep`, `blizzard:service`, `blizzard:e2e`, `blizzard:journey` — start them
  with `subprocess.Popen`, and `stdout=subprocess.PIPE` on a process no one reads from is a deadlock on a timer: the
  daemon runs until its output fills the ~64 KiB pipe buffer, then blocks in `write` forever. It does not die, so
  `poll()` still says alive and the port still answers `connect`; it simply stops serving mid-tick, and every wait
  against it times out. Pass an append-mode file instead, which has no ceiling and leaves the log readable after a
  failure rather than discarded with the pipe. `tests/support.py`'s `daemon_log_sink` is that file, and every
  daemon-running tier spawns through it — a daemon with a runtime dir logs to `daemon.log` beside its store, the mock
  fleet's dirless daemons to `shared_daemon_log_dir()`. `tests/test_daemon_spawn_sink.py` fails the unit tier on any new
  `stdout=subprocess.PIPE`, so the rule is enforced rather than remembered. This is a rule rather than a note because
  the symptom points nowhere near the cause: it first surfaced as the journey's *escalate* chunk sitting in `running` —
  a chunk whose path touched nothing the change had altered, three assertions after the ones that had already passed on
  the same wedged hub. Volume is what arms it, so any change that adds daemon logging shortens the fuse on a suite that
  was passing; suspect this before suspecting the scenario.

- **A change to a component reachable from the mobile shell's bottom nav must be exercised at ≥1 narrow width
  (`bzh:narrow-viewport-tier-rule`, issue #171).** Neither `web:unit-test` (jsdom parses `@container`/media-query rules
  without evaluating them) nor a browser e2e scenario run at Playwright's default 1280×720 can see a layout collapse —
  the two defect classes this rule exists for both shipped past every other tier: the profile menu pushed off-screen at
  a narrow header width (issues #161/#163) and the Events grid collapsing to ~104,000px of scroll below ~640px (issues
  #153–155). Two methods now close it: `web:shell-sweep` proves the real-Chromium layout claims jsdom cannot, spec by
  spec — [its own registry](./commands.md#webshell-sweep) states which surfaces it covers and what each one asserts;
  `tests/e2e/`'s `wide_viewport`/`narrow_viewport` fixtures (`tests/e2e/conftest.py`) give any browser scenario a real
  ~390px page to assert against, first used by `test_event_log_e2e.py`'s narrow-viewport Events assertion. A component
  with no narrow-width handling of its own (this rule's whole point) is not itself a gap to fix here — it is a gap to
  close with a narrow-width proof in whichever of the two methods fits the surface, the same way #171 closed the two
  above.
- **Crash correctness is an orthogonal dimension, not a fifth tier** — the kill-9 sweep (`blizzard:crash-sweep`) and the
  architectural requirements it exercises are
  [../architecture/crash-correctness.md](../../architecture/crash-correctness.md). The unit tier covers each step
  function's idempotency in isolation; the component tier drives steps in-process against the virtual clock; the sweep
  is the only piece needing real subprocesses and real signals.
