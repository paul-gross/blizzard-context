# Performing a `blizzard-mock:` manual method (`bzh:matrix-manual-mock-detail`)

<!-- One flat `###` section per method id — the shape this file's sibling spokes share. -->
<!-- rumdl-disable MD001 -->

Full detail for the `blizzard-mock:` manual methods named in [`../blizzard.md`](../blizzard.md)'s Manual testing table;
the `blizzard:` manual methods live in [`./manual.md`](./manual.md).

Both seeded-store methods are driven by a human, or a `frontend-verifier` agent, in a real browser — the pass condition
is a rendered view — and both start from a freshly provisioned env with its shell vars sourced and its daemons up; for
the seeded board, an env never yet seeded:

```bash
winter provision alpha
winter service up alpha --wait
source <(winter env alpha)
```

A plain shell needs that `source <(winter env <env>)` before `$BZ_HUB_RUNTIME` and `$BZ_HUB_WEB_PORT` resolve —
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) §Running it owns why.

### `blizzard-mock:manual`

**Surface.** The winter-wired mock forge (`tool:service-up`) fronting a real fixture workspace's per-env bare origins —
the daemons' own git truth, exercised out of process.

**Setup.** Mint a fixture at the path the forge reads,
`$BZ_FORGE_REPOS_DIR = ${BLIZZARD_MOCK_SCRATCH_ROOT}/${WINTER_ENV}/origins`, then bring the stack up, running from the
workspace root:

```bash
BLIZZARD_MOCK_SCRATCH_ROOT=/tmp/blizzard-mock/fixtures WINTER_ENV=alpha sh -c 'cd alpha/blizzard-mock && uv run blizzard-mock-fixture mint --env alpha'
winter service up alpha --wait
```

Do not pass `--winter-source $PWD` when minting: inside a `cd … && …` subshell `$PWD` expands after the `cd` and names
the `blizzard-mock` checkout — which has no `tools/winter-cli` — and minting fails; let the walk-up from the worktree to
the workspace root resolve it, or set `$BLIZZARD_MOCK_WINTER_SOURCE` to the workspace root explicitly.

**Passes when.** `curl -fs localhost:${BZ_FORGE_PORT:-4421}/healthz` returns `ok` and
`curl -fs localhost:${BZ_FORGE_PORT:-4421}/repos/blizzard/toy-api` returns `200` with `"default_branch": "main"`.

**Teardown.** Leave services down afterwards with `winter service down alpha`, and remove the fixture with
`blizzard-mock-fixture destroy --env alpha`.

### `blizzard-mock:manual-seeded-board`

**Surface.** `blizzard-mock-data scenario board` (`tool:mock-data`, owned by
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md)) — a fresh env's hub serving a fully populated board
from data written straight into its store, with no work source ever configured and the hub daemon never restarted
between seed and view. `blizzard:service-test`'s `test_mock_data_seeding_service.py` already proves the claim's
machine-checkable halves — seeder per-chunk status agrees with the hub's own `derive_chunk_status`, and the hub reads
the seeded rows with no restart — leaving this method only the human-eye half: whether the board renders the seeded
facts correctly.

**Setup.** Before seeding, confirm the env's hub runtime config carries zero `[[work_source]]` blocks —
`cat $BZ_HUB_RUNTIME/blizzard-hub.toml`; a fresh `hub init` scaffold emits the work-source block only as a commented-out
example — and that no forge fixture has been minted for the env: `blizzard-mock-fixture` was never run against it, so
`tool:mock-fleet`'s forge is up but fronts no origins.

**Steps.**

1. Seed straight into the running env's own hub store:

   ```bash
   cd alpha/blizzard-mock && uv run blizzard-mock-data scenario board --chunks 9 --stress --dir "$BZ_HUB_RUNTIME"
   ```

   `--chunks 9` rather than the `--chunks 6` default is deliberate: fewer than nine covers only a prefix of
   `blizzard-mock/src/blizzard_mock/mock_data/domain/hub/scenario_seed.py`'s `STATUS_ORDER`, and the render check needs
   every derived status actually seeded.

2. Without restarting the hub, open the board at `http://localhost:${BZ_HUB_WEB_PORT}/` and confirm the seeded chunk
   cards render across all nine derived statuses.

3. Confirm the cost column shows the cost-partial chunk `scenario board` always seeds — a `NULL cost_usd` usage fact —
   as partial rather than as `$0.00`.

4. Open the Events tab and confirm the seeded mixed-severity rows render.

5. Open the `ready` chunk's chunk page, census index 0, at `http://localhost:${BZ_HUB_WEB_PORT}/board/chunk/<chunk-id>`
   and confirm its Artifacts tab shows the seeded artifact; do the same for the `waiting_on_human` chunk, census index
   3, confirming the spread reaches more than one chunk. The Artifacts and Node history tabs live on the chunk page, not
   the board's desktop dock — the dock renders one flat Artifacts section and a non-activatable timeline with no
   per-step panel, while the chunk page is the mobile drill-down whose URL resolves from any viewport.

6. Open the `done` chunk's chunk page, census index 4, and confirm its Artifacts tab shows both seeded artifacts, its
   Node history tab shows two node-steps, and picking each step in turn shows that step's own artifact —
   `build.build-log.1` under the `build` step, `deliver.release-commit.1` under the `deliver` step — in the per-step
   Artifacts panel beside the timeline.

7. Open the multi-question `--stress` chunk's detail dock and confirm its two extra independent question trails render
   in the dock's trail.

**Passes when.** Every rendered check holds against the same hub process `service up` started, with no restart, reset,
or re-init between the seed command and the view.

### `blizzard-mock:manual-seeded-fleet`

**Surface.** `blizzard-mock-data scenario fleet` (`tool:mock-data`, owned by
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) §Seeding both stores together) — a fresh env's runner
panel rendering the leases, asks, escalations, takeovers, environments, and facts written straight into the runner
store, coherent with a hub board seeded in the same invocation, the runner daemon already up. No automated tier covers
this claim: `blizzard:service-test`'s `test_mock_data_seeding_service.py` exercises only unpinned `scenario board`,
never `scenario fleet`'s pinned mode — the path where seeder belief and hub derivation can part ways — and the mock's
own composer tests restate the seeder's belief rather than check it against a live hub; this rendered check is the
claim's sole check against reality. And there is no never-restarted variant: `blizzard runner host` is the only serve
mode — reconciliation loop and local API are one process — so the daemon reconciles against exactly this seed every
tick.

**Setup.** Only the provisioned, daemons-up env of the shared preamble.

**Steps.**

1. From `alpha/blizzard-mock`, reset both stores, then seed one coherent fleet:

   ```bash
   uv run blizzard-mock-data reset --store hub --dir "$BZ_HUB_RUNTIME"
   uv run blizzard-mock-data reset --store runner --dir "$BZ_RUNNER_RUNTIME"
   uv run blizzard-mock-data scenario fleet --chunks 6 --seed 1 --hub-dir "$BZ_HUB_RUNTIME" --runner-dir "$BZ_RUNNER_RUNTIME"
   ```

   Seed after `winter service up`, never before: `--runner-dir` has no `blizzard-runner.toml` to resolve `db_url` and
   `runner_id` from until the runner's first start writes it —
   [`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) §Seeding both stores together owns why.

2. Open the board at `http://localhost:${BZ_HUB_WEB_PORT}/`, confirm the six seeded chunks render with their statuses,
   and note the census.

3. On the runner panel at `http://localhost:${BZ_RUNNER_WEB_PORT}/`, BOARD tab: its ACTIVE LEASES panel shows the one
   parked lease (`PARKED`, `pid —`) — the closed, escalated lease is deliberately absent; its ENVIRONMENTS panel shows
   the two held bindings each naming its chunk beside the env's own unheld workspace environment; its CHUNKS ON THIS
   MACHINE · DERIVED STATUS list shows both mirrored chunks as `WAITING · ASK` and `HUMAN IN SESSION`; and its LOCAL
   ASKS panel shows the open ask with its question text.

4. Select the `HUMAN IN SESSION` chunk and confirm the detail pane renders the mirrored escalation — the closed lease
   and its session id, then an ESCALATED — RESUME SESSION block whose resume command is built from the escalation's own
   lease session id and the chunk's bound workdir. The mirrored takeover has no rendering of its own in the detail pane;
   its only rendered trace is the `HUMAN IN SESSION` header label, because the derived status folds an open takeover
   ahead of the escalation.

5. Open the EVENTS tab and confirm its LOCAL FACT LOG shows the two seeded facts, `question.asked` and
   `escalation.recorded`, each against its mirrored chunk and ticked as acked.

6. The seeded runner-store `usage_facts` and `transcript_segments` rows have no panel surface — `/api/dashboard` carries
   neither, and the per-lease transcript route never reads `transcript_segments` — so check those two tables in the
   store instead, expecting the same two mirrored chunk ids from both:

   ```bash
   sqlite3 "$BZ_RUNNER_RUNTIME/data/runner.db" 'select chunk_id from usage_facts; select chunk_id from transcript_segments;'
   ```

7. Do not check the HUB panel's `link` and `loop` rows before the first tick: the runner-store reset deleted the
   `hub_control` row — `reset` only clears rows, so the table itself survives — and only the next tick's registry sync
   re-inserts the row, so `link` reads `UNREACHABLE` regardless of the seed until then. Wait at least one tick — 30
   seconds by default, watching the runner's log for `tick end` — then re-check every panel, now including the HUB
   panel: `link` `CONNECTED` and `loop` `PAUSED` — the seeded local brake — now that the runner's registry sync has
   recreated `hub_control`.

8. Expect the LOCAL FACT LOG to grow on that first tick: the reset emptied `external_usage_samples`, so the cadence
   anchor `max(sampled_at)` is `None` and the interval gate does not apply — the usage sampler runs unconditionally,
   landing an `external_subscription_usage.sampled` fact only if a readable access token lets it return a snapshot. The
   two seeded facts must still be there and still ticked.

9. Re-open the board and confirm every chunk's status and the overall census are unchanged.

Do not clear the local pause from the panel: one click unbrakes FILL, which claims the board's `ready` chunk and spawns
real workers.

**Passes when.** Every checked panel renders populated, every seeded row still renders unchanged after the first tick
apart from the fact log's daemon-appended rows, and the board's statuses and census are unchanged.
