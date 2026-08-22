# Performing a `blizzard-mock:` manual method (`bzh:matrix-manual-mock-detail`)

<!-- One flat `###` section per method id — the shape this file's sibling spokes share. -->
<!-- rumdl-disable MD001 -->

Full detail for the `blizzard-mock:` manual methods named in [`../blizzard.md`](../blizzard.md)'s Manual testing table,
one section per row, in that table's order, each ending with a `Teardown.` only where its own method declares one. The
`blizzard:` methods live in [`./manual.md`](./manual.md).

Both seeded-store methods below start from a freshly provisioned env with its shell vars sourced and its daemons up —
for the seeded board, an env not yet seeded:

```bash
winter provision alpha
winter service up alpha --wait
source <(winter env alpha)
```

A plain shell needs that `source <(winter env <env>)` before `$BZ_HUB_RUNTIME` and `$BZ_HUB_WEB_PORT` resolve, and
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) §Running it owns why. Both are executed by a human,
or a `frontend-verifier` agent, driving a real browser against the view under test, since the pass condition is a
rendered view — the same executor precedent `blizzard:manual-standing-idp` names.

### `blizzard-mock:manual`

**Surface.** The winter-wired mock forge (`tool:service-up`) fronting a real fixture workspace's per-env bare origins —
the same single git truth the daemons bind to, exercised out of process.

**Setup.** Mint a fixture at the path the forge reads,
`$BZ_FORGE_REPOS_DIR = ${BLIZZARD_MOCK_SCRATCH_ROOT}/${WINTER_ENV}/origins`, then bring the stack up, running from the
workspace root:

```bash
BLIZZARD_MOCK_SCRATCH_ROOT=/tmp/blizzard-mock/fixtures WINTER_ENV=alpha sh -c 'cd alpha/blizzard-mock && uv run blizzard-mock-fixture mint --env alpha'
winter service up alpha --wait
```

Do not pass `--winter-source $PWD` when minting: inside a `cd … && …` subshell `$PWD` expands after the `cd`, names the
`blizzard-mock` checkout, which has no `tools/winter-cli`, and minting fails. Let the walk-up from the worktree to the
workspace root resolve it, or set `$BLIZZARD_MOCK_WINTER_SOURCE` to the workspace root explicitly.

**Passes when.** `curl -fs localhost:${BZ_FORGE_PORT:-4421}/healthz` returns `ok` and
`curl -fs localhost:${BZ_FORGE_PORT:-4421}/repos/blizzard/toy-api` returns `200` with `"default_branch": "main"`,
showing the live forge fronting the minted origins.

**Teardown.** Leave services down afterwards with `winter service down alpha`, and remove the fixture with
`blizzard-mock-fixture destroy --env alpha`.

### `blizzard-mock:manual-seeded-board`

**Surface.** `blizzard-mock-data scenario board` (`tool:mock-data`,
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md)) as the direct store-seed path a human renders: a
fresh env's hub serving a realistic, fully-populated board from data written straight into its store, with no work
source ever configured and the hub daemon never restarted between seed and view. `blizzard:service-test`'s
`test_mock_data_seeding_service.py` already proves the machine-checkable halves of that claim — the seeder's per-chunk
status agrees with the hub's own `derive_chunk_status`, and the hub reads the seeded rows with no restart — leaving this
method only what a human eye is needed for: whether the board renders the seeded facts correctly.

**Setup.** Confirm before seeding that the env's hub runtime config carries zero `[[work_source]]` blocks —
`cat $BZ_HUB_RUNTIME/blizzard-hub.toml`, where a fresh `hub init` scaffold emits the work-source block as a
commented-out example only, never live — and that no forge fixture has been minted for the env, meaning
`blizzard-mock-fixture` was never run against it, so `tool:mock-fleet`'s forge is up but fronts no origins.

**Steps.**

1. Seed a stress board straight into the running env's own hub store:

   ```bash
   cd alpha/blizzard-mock && uv run blizzard-mock-data scenario board --chunks 9 --stress --dir "$BZ_HUB_RUNTIME"
   ```

   `--chunks 9` rather than the `--chunks 6` default is deliberate: fewer than nine covers only a prefix of
   `blizzard-mock/src/blizzard_mock/mock_data/domain/hub/scenario_seed.py`'s `STATUS_ORDER`, and the render check needs
   every one of the derived statuses actually seeded.

2. Without restarting the hub, open the board at `http://localhost:${BZ_HUB_WEB_PORT}/`. Confirm the seeded chunk cards
   render across all nine derived statuses.
3. Confirm the cost column shows the cost-partial chunk `scenario board` always seeds — a `NULL cost_usd` usage fact —
   as partial rather than as `$0.00`.
4. Open the `ready` chunk's chunk page, census index 0, at `http://localhost:${BZ_HUB_WEB_PORT}/board/chunk/<chunk-id>`
   and confirm its Artifacts tab shows the seeded artifact, then do the same for the `waiting_on_human` chunk at census
   index 3 to confirm the spread reaches more than one chunk.
5. Open the `done` chunk's chunk page, census index 4, and confirm its Artifacts tab shows both seeded artifacts, then
   that its Node history tab shows two node-steps and that picking each in turn shows that step's own artifact —
   `build.build-log.1` under the `build` step, `deliver.release-commit.1` under the `deliver` step — in the per-step
   Artifacts panel beside the timeline. Those tabs live on the chunk page, not the board's desktop dock: the dock
   renders one flat Artifacts section and a non-activatable timeline with no per-step panel, while the page is the
   mobile drill-down whose URL resolves from any viewport.
6. Open the multi-question `--stress` chunk's detail dock and confirm its two extra independent question trails render
   in the dock's trail.
7. Open the Events tab and confirm the seeded mixed-severity rows render.

**Passes when.** Every rendered check holds against the same hub process `service up` started, with no restart, reset,
or re-init between the seed command and the view.

### `blizzard-mock:manual-seeded-fleet`

**Surface.** `blizzard-mock-data scenario fleet` (`tool:mock-data`,
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) §Seeding both stores together), proving a fresh env's
runner panel renders the leases, asks, escalations, takeovers, environments, and facts written straight into the runner
store, coherent with a hub board seeded in the same invocation, with the runner daemon already up.

No automated tier covers that claim. `blizzard:service-test`'s `test_mock_data_seeding_service.py` exercises only
unpinned `scenario board` and never invokes `scenario fleet`'s pinned mode, which is exactly where the seeder's belief
about a chunk's derived status and the hub's actual derivation can part ways; the only other machine-checkable proof of
the pinned seeding path is the mock's own composer tests, which restate the seeder's belief rather than check it against
a live hub. This rendered check is that claim's sole check against reality. `blizzard runner host` is the only serve
mode — the reconciliation loop and the local API are one process — so there is no never-restarted variant to check here:
the daemon reconciles against exactly this seed every tick.

**Setup.** The provisioned, daemons-up env of the preamble above, with nothing further of this method's own.

**Steps.**

1. Reset both stores and seed one coherent fleet, from `alpha/blizzard-mock`:

   ```bash
   uv run blizzard-mock-data reset --store hub --dir "$BZ_HUB_RUNTIME"
   uv run blizzard-mock-data reset --store runner --dir "$BZ_RUNNER_RUNTIME"
   uv run blizzard-mock-data scenario fleet --chunks 6 --seed 1 --hub-dir "$BZ_HUB_RUNTIME" --runner-dir "$BZ_RUNNER_RUNTIME"
   ```

   Seed after `winter service up`, never before: `--runner-dir` has no `blizzard-runner.toml` to resolve `db_url` and
   `runner_id` from until the runner's first start writes it, and
   [`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) §Seeding both stores together owns why.

2. Open the board at `http://localhost:${BZ_HUB_WEB_PORT}/`, confirm the six seeded chunks render with their statuses,
   and note the census.
3. Open the runner panel at `http://localhost:${BZ_RUNNER_WEB_PORT}/` on the BOARD tab and confirm its ACTIVE LEASES
   panel shows the one parked lease (`PARKED`, `pid —`), its ENVIRONMENTS panel shows the two held bindings each naming
   its chunk beside the env's own unheld workspace environment, its CHUNKS ON THIS MACHINE · DERIVED STATUS list shows
   both mirrored chunks as `WAITING · ASK` and `HUMAN IN SESSION`, and its LOCAL ASKS panel shows the open ask with its
   question text. The closed, escalated lease is deliberately absent from ACTIVE LEASES.
4. Select the `HUMAN IN SESSION` chunk and confirm the detail pane renders the mirrored escalation: the closed lease and
   its session id, then an ESCALATED — RESUME SESSION block whose resume command is built from the escalation's own
   lease session id and the chunk's bound workdir. The mirrored takeover has no rendering of its own in the detail pane;
   its only rendered trace is the `HUMAN IN SESSION` header label, because the derived status folds an open takeover
   ahead of the escalation.
5. Open the EVENTS tab and confirm its LOCAL FACT LOG shows the two seeded facts, `question.asked` and
   `escalation.recorded`, each against its mirrored chunk and ticked as acked.
6. The seeded runner-store `usage_facts` and `transcript_segments` have no panel surface — `/api/dashboard` carries
   neither, and the per-lease transcript route projects parsed conversation turns without ever reading
   `transcript_segments` — so check those two tables in the store instead, which names the same two mirrored chunk ids:

   ```bash
   sqlite3 "$BZ_RUNNER_RUNTIME/data/runner.db" 'select chunk_id from usage_facts; select chunk_id from transcript_segments;'
   ```

7. Wait at least one tick, 30 seconds by default, watching the runner's log for `tick end` to confirm one has landed,
   then re-check every panel and now also the HUB panel, which should read `link` `CONNECTED` and `loop` `PAUSED` — the
   seeded local brake — now that the runner's registry sync has recreated `hub_control`. Do not check the HUB panel's
   `link` and `loop` rows before that first tick: the runner-store reset deleted the `hub_control` row — the table
   itself survives, since `reset` only clears rows — and only `Pull._sync_registry` on the next tick re-inserts it, so
   `link` reads `UNREACHABLE` regardless of the seed until then.
8. Expect the LOCAL FACT LOG to grow on that first tick: the runner-store reset empties `external_usage_samples`,
   leaving its cadence anchor `max(sampled_at)` at `None` so the interval gate does not apply and the sampler runs
   unconditionally, landing an `external_subscription_usage.sampled` fact only if a readable access token lets it return
   a snapshot. The two seeded facts must still be there and still ticked.
9. Re-open the board and confirm every chunk's status and the overall census are unchanged.

Do not clear the local pause from the panel — the same no-tamper condition the seeded-board method pins for its
no-restart requirement — because one click unbrakes FILL, which claims the board's `ready` chunk and spawns real
workers.

**Passes when.** Every checked panel renders populated, every seeded row still renders unchanged after the first tick
apart from the fact log's daemon-appended rows, and the board's statuses and census are unchanged — the daemon having
reconciled the mirrored fleet without altering either store's seeded shape.
