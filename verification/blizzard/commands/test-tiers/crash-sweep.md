# `blizzard:crash-sweep` detail (`bzh:matrix-tier-crash-sweep`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading, every test-filename code span, and each `mise run` name with its paired command span are machine-checked registrations — keep them verbatim, inside the section. -->

The crash-sweep spoke of the test-tier hub [`../test-tiers.md`](../test-tiers.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### blizzard:crash-sweep

The tier command is `BLIZZARD_CRASH_SWEEP=1 uv run pytest -m crash_sweep tests/crash/` (`mise run crash-sweep`) — the
FULL kill-9 sweep; the crash-correctness contract it enforces is owned by
[`../../../../architecture/crash-correctness.md`](../../../../architecture/crash-correctness.md). The sweep enumerates
the crash-point registry (`blizzard.foundation.crash.discover_crash_points`) and, per point, runs the hub and runner as
real subprocesses over the mock fleet, arms the point so its owning daemon `SIGKILL`s itself there, then asserts the
invariant checker (`blizzard dev check-invariants`) is green over both stores and the chunk still lands exactly once
after an unarmed restart — startup is REAP. It needs the sibling `blizzard-mock` worktree and a winter source, and is
skipped without `BLIZZARD_CRASH_SWEEP=1`.

In CI the `pr` and `push` workflows run the bounded CI profile —
`BLIZZARD_CRASH_SWEEP=1 BLIZZARD_CRASH_SWEEP_CI=1 uv run pytest -m crash_sweep tests/crash/` (`mise run crash-sweep-ci`)
— one representative point per boundary family plus the whole-process cases and the recovery-critical windows, six and a
half to eight minutes of wall time on a GitHub runner — bounded, but a real fraction of the CI budget, not a fast check.
The bounded subset is intersected with the live registry and asserts each named point still exists
(`bzh:crash-point-registry`), so a rename fails loudly; the FULL sweep stays the documented local command above and runs
in the tag `release` workflow. Both CI workflows run it as a real gate over a multi-repo checkout — `blizzard`,
`blizzard-mock`, and the public `blizzard-workspace` (the winter source) as siblings, `BLIZZARD_MOCK_WINTER_SOURCE`
pointed at the last.

The registry's boundary families are `resume.`, `abandon.`, `pause.`, `hubnode.` (the generic hub command node's
per-step and pending-poll windows), `migrate.`, `attach.`, `nudge.`, `checks.`, `preempt.`, and `close.` (the
close-intent outbox's enqueue-then-drain windows, blizzard#383), plus ungrouped generic build-to-deliver points that
mostly fire in the runner loop (`bzh:crash-point-registry`). No case count is kept — the predicate is the membership
test, not a number that drifts.

`claim.` — the route-claim boundary between persisting the route with its capability-token fact and the runner reading
the plaintext token back — is the first ungrouped point armed on the hub, recovered generically by the runner's
interrupted-claim adoption rather than a dedicated scenario. The windows with dedicated scenarios:

- `migrate.`, the cross-graph migration window armed on the hub, is swept by `test_kill9_at_migrate_crash_point`: a kill
  right after the atomic re-pin loses only the `MIGRATED` response, the runner's replay re-derives it via the
  `accepted_migration` probe, and the migration invariants come back green.
  `test_kill9_at_migrate_crash_point_landing_on_a_hub_node` drives a migration onto a hub-executed node, where the route
  is retained, not released: the replay returns `HUB_NODE_TAKEN`, the holding runner keeps its envs, and its ADVANCE
  poll drives the landed hub node to `done` instead of the chunk wedging at `delivering`. The per-chunk intended
  migration is swept on the same point by `test_kill9_at_migrate_crash_point_for_an_intended_migration`; its component-
  and unit-tier coverage is `tests/test_intended_migration_apply.py`, `tests/test_chunk_edit_api.py`, and
  `tests/test_hub_cli_chunk.py`, since e2e's `test_migration_e2e.py` exercises only the authored-choice migration.
- `attach.`, the worker artifact-attach durability window armed on the runner, is swept by
  `test_kill9_at_attach_crash_point`: the runner's local `POST /api/leases/{id}/attachments` records the attachment in
  one committed txn, the kill lands in the after-record-before-response window, and the durable row with full provenance
  is still readable via `attachments_for_lease` after an unarmed restart. `attach.` is an out-of-band HTTP write no loop
  step drives, so its scenario stands up a real runner daemon alone — no hub, no forge — seeding a parked lease and its
  capability token, the invariant checker running over the runner store only.
- `nudge.`, the produces-unmet nudge-once window armed on the runner, is swept by `test_kill9_at_nudge_crash_point` over
  both of its members: a `produces:` name with neither commit nor attachment gets exactly one resumed nudge in
  `_advance_exited_worker`, gated on a durable `(lease, epoch)` fact recorded before the resume it guards, so
  at-most-once is structural — recovery consults the fact, never the resume's outcome; the window fires inside ADVANCE,
  so a real hub stands up too.
- `checks.`, the checks-at-exit windows armed on the runner, is swept by `test_kill9_at_checks_crash_point` over both of
  its members: the runner runs a node's `checks:` at worker exit, recording each result row then a `checks_ran` marker;
  a kill before the marker leaves it unset and recovery re-runs the checks with latest-wins overwrite, while after the
  marker recovery reads the recorded results back and judges. The bounded-CI representative is the recovery-critical
  `checks.after-results.before-marker`.
- `close.`, the close-intent outbox's enqueue-then-drain windows armed on the hub (blizzard#383), is swept by
  `test_kill9_at_close_crash_point` over both of its members — `close.after-enqueue.before-drain` and
  `close.after-close.before-record` — driven entirely through the built-in `hub` work source, no forge involved: the
  pending intent survives either kill and the item closes exactly once after convergence.
  `blizzard-context/architecture/crash-correctness/hub.md` owns both windows' own ground.
- `preempt.`, the operator-restart teardown window armed on the runner, is swept by `test_kill9_at_preempt_crash_point`:
  an operator restarts a running chunk and the runner dies between killing the displaced worker and recording the
  `preempted` closure; recovery re-derives the same preempt off the hub's still-standing fence — the lease closes
  `preempted`, never `reaped` or `failed`, which would spend the retry budget the move exists to protect.

Whole-process cases round out the sweep: `tests/crash/test_kill9_sweep.py`'s own unparametrized test functions signal a
whole daemon process or process group, a graceful SIGTERM qualifying as readily as a `kill -9`. The whole-process
scenarios are:

- an external runner kill mid-flight, both before and after the worker's commit is durably declared;
- daemon restarts re-attaching an in-flight session in place;
- a `killpg` of the hub process group mid-delivery between repo pushes, both land graphs swept.
