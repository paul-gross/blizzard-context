# The live-fleet journey command detail (`bzh:matrix-command-journey`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->

The acceptance journey a real fleet runs end to end. Read [`../../blizzard.md`](../../blizzard.md) first for the short
command and the method-id inventory; [`../commands.md`](../commands.md) routes to every other method's detail.

### blizzard:journey

`BLIZZARD_JOURNEY=1 uv run pytest -m journey tests/journey/` (`mise run journey`) — the **capstone acceptance-journey
rehearsal**: the whole MVP acceptance journey as one committed, repeatable test over **real host daemons**
(`blizzard hub host` + `blizzard runner host`, the systemd units' `ExecStart`). Five issues are filed across both
fixture repos and ingested by id; two are **grouped** into one chunk (`POST /chunks/{id}/group`) and the riskiest
**reordered** to the top (`POST /queue/reorder`) — the same board controls the operator uses. One shared
`build → review → deliver` graph drives four different journeys by reading each chunk's work item **through the hub
pass-through** (`blizzard runner work-items`) and branching on a directive in the issue body: a clean **multi-repo**
land (grouping + serial delivery, criteria 11/13), a **review-fail** loop carrying its findings asset +
`prompt_addendum` back into build (criterion 9), an **ask** that parks `waiting_on_human` and is answered with
`blizzard hub answer` (criterion 7), and a **genuine failure** that escalates to `needs_human` whose takeover command,
run **verbatim**, resumes the stuck session (criterion 6) — its `wrapped_takeover_command` shape-checked alongside,
proving what [`blizzard:e2e`'s `test_escalation_e2e`](../e2e-scenarios.md#test_escalation_e2e) cannot:
[`test_escalation_e2e`](../e2e-scenarios.md#test_escalation_e2e) already resolves its own runner's runtime directory for
real (a genuine `tmp_path`, resolved the same way), so what only the journey adds is the **process boundary** — the
command is composed by a runner running as its own spawned OS process (`blizzard runner host`'s real `ExecStart`), not
by the loop's tick function called directly inside the test process the way `test_escalation_e2e` drives it. Mid-run
**both daemons are `SIGKILL`ed and restarted** through the migrate-then-host path — the invariant checker is green the
instant after, and every chunk resumes at exactly the node the hub last recorded (the exhaustive per-boundary proof
stays `blizzard:crash-sweep`). The morning-after assertions are taken verbatim from the journey: succeeded chunks merged
to bare `main`, full history + artifacts at the hub API, the asked chunk resumed **without** takeover, nothing worked
twice (each landed file reachable from bare `main` exactly once), no environment orphaned
(`blizzard dev check-invariants` clean), and `blizzard hub status` truthful for every chunk. Local-only like
`blizzard:e2e` / `blizzard:crash-sweep` — needs the sibling provisioned `blizzard-mock` worktree and a local winter
source; skipped without `BLIZZARD_JOURNEY=1`. Deterministic (every phase gates on a latched hub state, not on timing) —
run it twice, it is green twice. The one behaviour the capstone deliberately does **not** stress is a *simultaneous*
hub-and-runner crash landing inside a build's base turn (before the commit is submitted): the reboot is timed to a
latched fleet so no chunk is mid-build, and the exhaustive single-daemon per-boundary recovery stays
`blizzard:crash-sweep`.
