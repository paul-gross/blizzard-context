# The live-fleet journey command detail (`bzh:matrix-command-journey`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `### blizzard:journey` heading and its cited code spans — test paths, and the `mise run journey` pairing with its exact command text — are machine-checked; keep them verbatim. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:journey

`npx playwright test --project=journey` (`mise run journey`) — the capstone: the MVP acceptance journey as one
committed, repeatable test, `tests/journey/journey.spec.ts::test_the_acceptance_journey_end_to_end`, in the Playwright
package's `journey` project. It runs on a fresh hub and a runner host of its own, real daemons, `blizzard hub host` plus
`blizzard runner host`, on a timed runner loop and on the mock forge. It is winter-free: its runner uses the built-in
`basic` provider over the forge's bare repositories, so it needs only the sibling provisioned `blizzard-mock` worktree.
The `journey` project is no `service-*` project, so no service selection runs it. `upper-tiers.yml` runs it as a job on
every pull request and tag.

One shared `build → review → deliver` graph, with the shipped `land` action, drives the journeys by reading each chunk's
work item through the hub pass-through (`blizzard runner work-items`) and branching on a directive in the issue body.
Five issues are filed across both forge repositories and ingested by id; direct hub API calls group two into one chunk
and place the riskiest first. The journeys:

- a clean multi-repo land with grouping and serial delivery (criteria 11/13);
- a review-fail loop carrying its findings asset and `prompt_addendum` back into build (criterion 9);
- an ask parked `waiting_on_human` and answered with `blizzard hub question answer` (criterion 7);
- a genuine failure escalated to `needs_human` whose takeover command, run verbatim, resumes the stuck session
  (criterion 6), its `wrapped_takeover_command` compared exactly against the runner's name from `GET /api/host/runners`.

Every phase gates on a chunk's latched hub state, not timing — the run is deterministic. Mid-run both daemons are
`SIGKILL`ed and restarted on their directories and ports; every chunk resumes at exactly the node the hub last recorded
— the exhaustive per-boundary proof, including the window right after the kill, stays `blizzard:crash-sweep`. Both
stores keep their invariants, checked with `blizzard dev check-invariants` in client mode once after the restart and
again in the morning. The morning-after assertions read each surface the system offers: succeeded chunks merged to the
forge's bare `main`, read through the harness's tree, history and file reads; full history and artifacts at the hub API;
the asked chunk resumed without takeover, from the mock fleet's own session record; each landed file reachable from
`main` exactly once; no environment orphaned, `GET /api/host/environments` holding the escalated chunk's alone; and
`blizzard hub status` truthful for every chunk.

Beyond the service tier's `test_retries_exhausted_escalates_and_takeover_resumes_session`
([`./test-tiers/service.md`](./test-tiers/service.md)), the journey adds the process boundary: the takeover command is
composed by a runner spawned as its own OS process, not by the loop's tick function called inside the test process.
Deliberately unstressed: a simultaneous hub-and-runner crash inside a build's base turn before the commit is submitted —
the reboot targets a latched fleet, so no chunk is mid-build.
