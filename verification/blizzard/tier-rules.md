# The test tiers, and writing a test at one (`bzh:matrix-tier-rules`)

The tier roster, and the standard every tier's tests are written to. The command each tier runs is its row in
[`../blizzard.md`](../blizzard.md)'s Commands table; what a change owes as a companion landing is
[`./companion-changes.md`](./companion-changes.md)'s; whether a green run counts as evidence at all is
[`./evidence.md`](./evidence.md)'s.

## Test tiers

Four tiers, all used — each answers a different question, and none substitutes for another. The mocks the upper tiers
bind are owned by `blizzard-mock`.

| Tier          | Method                    | Scope                                                                                                     | Tooling                                                                                                                             |
| ------------- | ------------------------- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Unit**      | `blizzard:unit-test`      | One class or function in isolation.                                                                       | pytest                                                                                                                              |
| **Component** | `blizzard:component-test` | A domain slice wired with real internal collaborators, doubles only at the seams.                         | pytest                                                                                                                              |
| **Service**   | `blizzard:service-test`   | A running hub or runner's HTTP API exercised from outside, seams bound to the mock fleet.                 | pytest + HTTP                                                                                                                       |
| **E2E**       | `blizzard:e2e`            | The full system — hub, runner, web app — through the browser and CLI, every seam bound to the mock fleet. | pytest plus a real Chromium via Playwright; each browser-driven scenario states its own guard in the [registry](./e2e-scenarios.md) |

## Hermetic by construction

Service and e2e tests never spend a real token and never touch the network: the harness seam binds a mock coding
harness, the work-source and delivery seams bind the mock GitHub forge, and the workspace seam binds mocks or local
fixtures.

Tests run against sqlite. Postgres is a configuration concern, held by staying inside SQLAlchemy's portable surface
(`bzh:sql-portable`) rather than by a second test matrix.

Stand test data up through the mock-data CLI and its fixtures (`tool:mock-data`), never through ad-hoc SQL.

## One-sided service tests

A one-sided service test drives the mock counterpart: runner service tests run against the mock hub, hub service tests
against the mock runner. Its edge cases come from driving the mock's levers, never from contriving the real daemon into
a rare state.

## Crash correctness is a dimension, not a tier

Crash correctness cuts across the tiers rather than adding one. The unit tier covers each step function's idempotency in
isolation, the component tier drives steps in-process against the virtual clock, and only the kill-9 sweep
`blizzard:crash-sweep` needs real subprocesses and real signals. The architectural requirements that sweep exercises are
owned by [`../../architecture/crash-correctness.md`](../../architecture/crash-correctness.md).

## A spawned daemon's output goes to a file (`bzh:daemon-stdout-to-file`)

**Rule.** A spawned daemon's output goes to an append-mode file, never to a pipe nothing drains.

**Why.** `stdout=subprocess.PIPE` on a process nobody reads is a deadlock on a timer: the daemon runs until its output
fills the ~64 KiB pipe buffer, then blocks in `write` forever. A pipe-wedged daemon never dies — `poll()` still reports
it alive and its port still answers `connect`, but it stops serving mid-tick and every wait against it times out.

**Detect.** `tests/test_daemon_spawn_sink.py` fails the unit tier on any newly introduced `stdout=subprocess.PIPE`. Log
volume is what arms the wedge, so a change that adds daemon logging can wedge a suite that was passing and the symptom
lands far from the cause — suspect the wedge before the test.

**Do.** The tiers that spawn real daemons with `subprocess.Popen` — `blizzard:crash-sweep`, `blizzard:service-test`,
`blizzard:e2e`, and `blizzard:journey` — spawn through `tests/support.py`'s `daemon_log_sink`, which is that file: a
daemon with a runtime dir logs to `daemon.log` beside its store, and the mock fleet's dirless daemons log to
`shared_daemon_log_dir()`.

## Narrow width is proved by a test (`bzh:narrow-viewport-tier-rule`)

**Rule.** A change to a component reachable from the mobile shell's bottom nav is exercised at a narrow width by at
least one test.

**Why.** Neither `web:unit-test` nor a browser e2e scenario at Playwright's default 1280x720 viewport can see a layout
collapse, because jsdom parses `@container` and media-query rules without ever evaluating them.

**Do.** The `wide_viewport` and `narrow_viewport` fixtures in `tests/e2e/conftest.py` give any browser scenario a real
~390px page to assert against, and `web:shell-sweep` proves the real-Chromium layout claims jsdom cannot — the surfaces
it covers and what each of its specs asserts are stated in [`./commands.md`](./commands/web.md#webshell-sweep).

**Don't.** Treat a component with no narrow-width handling of its own as a defect to fix in place. It is a gap to close
with a narrow-width proof in whichever narrow-width method fits the surface.
