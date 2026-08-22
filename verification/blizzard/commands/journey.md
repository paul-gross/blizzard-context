# The live-fleet journey command detail (`bzh:matrix-command-journey`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `### blizzard:journey` heading and its cited code spans — test paths, and the `mise run journey` pairing with its exact command text — are machine-checked; keep them verbatim. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:journey

`BLIZZARD_JOURNEY=1 uv run pytest -m journey tests/journey/` (`mise run journey`) — the capstone: the MVP acceptance
journey as one committed, repeatable test over real host daemons, `blizzard hub host` plus `blizzard runner host`. It
runs locally and nowhere else: it needs the sibling provisioned `blizzard-mock` worktree and a local winter source, and
is skipped without `BLIZZARD_JOURNEY=1`.

One shared `build → review → deliver` graph drives the journeys by reading each chunk's work item through the hub
pass-through (`blizzard runner work-items`) and branching on a directive in the issue body. Five issues are filed across
both fixture repos and ingested by id; two are grouped into one chunk and the riskiest reordered to the top via the
operator's own board controls. The journeys:

- a clean multi-repo land with grouping and serial delivery (criteria 11/13);
- a review-fail loop carrying its findings asset and `prompt_addendum` back into build (criterion 9);
- an ask parked `waiting_on_human` and answered with `blizzard hub answer` (criterion 7);
- a genuine failure escalated to `needs_human` whose takeover command, run verbatim, resumes the stuck session
  (criterion 6), its `wrapped_takeover_command` shape-checked alongside.

Every phase gates on a latched hub state, not timing — the run is deterministic. Mid-run both daemons are `SIGKILL`ed
and restarted through the migrate-then-host path; the invariant checker is green immediately after, and every chunk
resumes at exactly the node the hub last recorded — the exhaustive per-boundary proof stays `blizzard:crash-sweep`. The
morning-after assertions: succeeded chunks merged to bare `main`; full history and artifacts at the hub API; the asked
chunk resumed without takeover; each landed file reachable from bare `main` exactly once; no environment orphaned
(`blizzard dev check-invariants` clean); and `blizzard hub status` truthful for every chunk.

Beyond `blizzard:e2e`'s `test_escalation_e2e`
([`../e2e-scenarios/human-loop.md#test_escalation_e2e`](../e2e-scenarios/human-loop.md#test_escalation_e2e)), the
journey adds the process boundary: the takeover command is composed by a runner spawned as its own OS process, not by
the loop's tick function called inside the test process. Deliberately unstressed: a simultaneous hub-and-runner crash
inside a build's base turn before the commit is submitted — the reboot targets a latched fleet, so no chunk is
mid-build.
