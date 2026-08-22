# Blizzard-mock manual-method detail (`bzh:matrix-manual-mock-detail`)

<!-- the flat `###` shape is this file's stated contract, shared with its sibling spokes. -->
<!-- rumdl-disable MD001 -->

Full detail for the `blizzard-mock:` manual methods [../blizzard.md](../blizzard.md)'s Manual testing table names — one
`### <method-id>` section per row, in table order. The `blizzard:` methods are [./manual.md](./manual.md).

### blizzard-mock:manual — the live wired-service forge over a real fixture

Surface: the winter-wired mock forge (`tool:service-up`, band `+1`) fronting a real fixture workspace's per-env bare
origins — the same single git truth the daemons will bind to, exercised out of process rather than in-test. Setup — mint
a fixture at the path the forge reads (`$BZ_FORGE_REPOS_DIR = ${BLIZZARD_MOCK_SCRATCH_ROOT}/${WINTER_ENV}/origins`),
then bring the stack up. Run from the workspace root:

```bash
BLIZZARD_MOCK_SCRATCH_ROOT=/tmp/blizzard-mock/fixtures WINTER_ENV=alpha \
  sh -c 'cd alpha/blizzard-mock && uv run blizzard-mock-fixture mint --env alpha'
winter service up alpha --wait
```

The fixture's winter source resolves by walking up from the `blizzard-mock` worktree to the workspace root — **do not
pass `--winter-source $PWD`**: inside a `cd … && …` subshell `$PWD` expands *after* the `cd`, so it names the
`blizzard-mock` checkout (which has no `tools/winter-cli`) and minting fails. Let the walk-up default resolve it, or set
`$BLIZZARD_MOCK_WINTER_SOURCE` to the workspace root explicitly. Pass:
`curl -fs localhost:${BZ_FORGE_PORT:-4421}/healthz` returns `ok`, and
`curl -fs localhost:${BZ_FORGE_PORT:-4421}/repos/blizzard/toy-api` returns `200` with `"default_branch": "main"` — the
live forge fronts the minted origins. Leave services down after (`winter service down alpha`; remove the fixture with
`blizzard-mock-fixture destroy --env alpha`).

### blizzard-mock:manual-seeded-board — a realistic board with zero work sources and no hub restart

Surface: `blizzard-mock-data scenario board` (`tool:mock-data`,
[../tooling/store-seeding.md](../../tooling/store-seeding.md)) as the direct store-seed path a human actually renders —
proving a fresh env's hub serves a realistic, fully-populated board from data written straight into its store, with no
work source ever configured and the hub daemon never restarted between the seed and the view. `blizzard:service-test`'s
`test_mock_data_seeding_service.py` already proves the two machine-checkable halves of this claim (the seeder's intended
per-chunk status agrees with the hub's own `derive_chunk_status`, and the hub reads the seeded rows with no restart) —
this method covers only what a human eye is needed for: does the board actually *render* the seeded facts correctly.
Setup: a human, or a `frontend-verifier` agent, driving a real browser against the board — this method's whole pass
condition is a rendered view, the same executor precedent `blizzard:manual-standing-idp` names. A freshly provisioned,
not-yet-seeded env, its shell vars sourced (see [../tooling/store-seeding.md](../../tooling/store-seeding.md)'s §Running
it for why a plain shell needs `source <(winter env <env>)` before `$BZ_HUB_RUNTIME`/`$BZ_HUB_WEB_PORT` resolve):

```bash
winter provision alpha
winter service up alpha --wait
source <(winter env alpha)
```

Confirm the env's hub runtime config carries zero `[[work_source]]` blocks (`cat $BZ_HUB_RUNTIME/blizzard-hub.toml` — a
fresh `hub init` scaffold emits the work-source block as a commented-out example only, never live) and that no forge
fixture has been minted for the env (`blizzard-mock-fixture` never run against it — `tool:mock-fleet`'s forge is up but
fronts no origins).

Steps:

1. seed a stress board straight into the running env's own hub store:
   `cd alpha/blizzard-mock && uv run blizzard-mock-data scenario board --chunks 9 --stress --dir "$BZ_HUB_RUNTIME"` —
   `--chunks 9` (not the `--chunks 6` default) is deliberate here: fewer than nine only covers a prefix of
   `blizzard-mock/src/blizzard_mock/mock_data/domain/hub/scenario_seed.py`'s `STATUS_ORDER`, and step 3 below needs
   every one of the nine derived statuses actually seeded
2. without restarting the hub, open the board at `http://localhost:${BZ_HUB_WEB_PORT}/`
3. confirm the seeded chunk cards render across all nine derived statuses
4. confirm the cost column shows the cost-partial chunk `scenario board` always seeds (a `NULL cost_usd` usage fact) as
   partial, not as `$0.00`
5. open the Events tab and confirm the seeded mixed-severity rows render
6. open the multi-question `--stress` chunk's detail dock and confirm its two extra independent question trails render
   in the dock's trail
7. open the `ready` chunk's (census index 0) chunk page at `http://localhost:${BZ_HUB_WEB_PORT}/board/chunk/<chunk-id>`
   and confirm its Artifacts tab shows the seeded artifact, then the same for the `waiting_on_human` chunk (census index
   3), confirming the spread reaches more than one chunk. The tabs live on the **chunk page**, not on the board's
   desktop dock — the dock renders one flat Artifacts section and a non-activatable timeline, so it carries no per-step
   panel at all; the page is the mobile drill-down, and its URL resolves from any viewport
8. open the `done` chunk's (census index 4) chunk page: confirm its Artifacts tab shows both seeded artifacts, then
   confirm its Node history tab shows two node-steps and that picking each in turn shows that step's own artifact —
   `build.build-log.1` under the `build` step, `deliver.release-commit.1` under the `deliver` step — in the per-step
   Artifacts panel beside the timeline.

Pass: every check in steps 3–8 holds, observed against the same hub process `service up` started — no restart, reset, or
re-init between the seed command and the view.

### blizzard-mock:manual-seeded-fleet — a seeded runner panel beside a seeded board, coherent, live

Surface: `blizzard-mock-data scenario fleet` (`tool:mock-data`,
[../tooling/store-seeding.md](../../tooling/store-seeding.md)'s §Seeding both stores together) — proving a fresh env's
runner panel renders the leases, asks, escalations, takeovers, environments, and facts written straight into the runner
store, coherent with a hub board seeded the same invocation, with the runner daemon already up. The seeded runner-store
`usage_facts` and `transcript_segments` are checked in the store, not on the panel: the local API exposes no surface for
either (`/api/dashboard` carries neither, and the per-lease transcript route projects parsed conversation turns, never
reading `transcript_segments` itself), so a rendered check cannot reach them. `blizzard runner host` is the only serve
mode — the reconciliation loop and the local API are one process — so unlike `blizzard-mock:manual-seeded-board`'s hub
half there is no "never restarted" variant to check: the daemon reconciles against exactly this seed every tick, and
this method's pass condition is that reconciliation leaving every seeded section populated and the board unchanged.

**Gap.** Unlike `blizzard-mock:manual-seeded-board`, no automated tier covers this method's own claim.
`blizzard:service-test`'s `test_mock_data_seeding_service.py` exercises only unpinned `scenario board` — it never
invokes `scenario fleet`'s pinned mode, which is exactly where the seeder's own belief about a chunk's derived status
and the hub's actual derivation can part ways. This method's only machine-checkable proof of the pinned path is the
mock's own composer tests, which restate the seeder's belief rather than checking it against a live hub — this rendered
check is this claim's sole check against reality.

Setup: a human, or a `frontend-verifier` agent, driving a real browser against the runner panel — the same executor
precedent `blizzard:manual-standing-idp` names. A freshly provisioned, seeded-clean env with the runner daemon up:

```bash
winter provision alpha
winter service up alpha --wait
source <(winter env alpha)
```

Seed **after** `winter service up`, never before: `--runner-dir` has no `blizzard-runner.toml` to resolve `db_url`/
`runner_id` from until the runner's first start writes it
([../tooling/store-seeding.md](../../tooling/store-seeding.md)'s §Seeding both stores together owns why).

Steps:

1. reset both stores, then seed one coherent fleet:

   ```bash
   cd alpha/blizzard-mock
   uv run blizzard-mock-data reset --store hub --dir "$BZ_HUB_RUNTIME"
   uv run blizzard-mock-data reset --store runner --dir "$BZ_RUNNER_RUNTIME"
   uv run blizzard-mock-data scenario fleet --chunks 6 --seed 1 \
     --hub-dir "$BZ_HUB_RUNTIME" --runner-dir "$BZ_RUNNER_RUNTIME"
   ```

2. open the board at `http://localhost:${BZ_HUB_WEB_PORT}/` and confirm the six seeded chunks render, statuses included,
   and note the census
3. open the runner panel at `http://localhost:${BZ_RUNNER_WEB_PORT}/` — the **BOARD** tab — and confirm: its **ACTIVE
   LEASES** panel shows the one *parked* lease (`PARKED`, `pid —`); its **ENVIRONMENTS** panel shows the two held
   bindings, each naming its chunk, beside the env's own unheld workspace environment; its **CHUNKS ON THIS MACHINE ·
   DERIVED STATUS** list shows both mirrored chunks, one `WAITING · ASK` and one `HUMAN IN SESSION`; and its **LOCAL
   ASKS** panel shows the open ask with its question text. The closed, escalated lease is **not** in ACTIVE LEASES: that
   panel lists live leases only. **Do not check the HUB panel's `link`/`loop` rows yet** — step 1's
   `reset --store runner` deleted the `hub_control` row (the table itself survives — `reset` only clears rows), and only
   the runner's next tick re-inserts it via `Pull._sync_registry`; checked before that first tick, `link` reads
   `UNREACHABLE` regardless of the seed. Step 7 is where that check belongs
4. select the `HUMAN IN SESSION` chunk in that list and confirm the detail pane renders the mirrored escalation: the
   closed lease and its session id, then an **ESCALATED — RESUME SESSION** block whose resume command is built from the
   escalation's own lease session id and the chunk's bound workdir. The mirrored takeover has no rendering of its own in
   this pane — its only rendered trace is the `HUMAN IN SESSION` header label already confirmed in step 3 (the derived
   status folds an open takeover ahead of the escalation)
5. open the **EVENTS** tab and confirm its **LOCAL FACT LOG** shows the two seeded facts — `question.asked` and
   `escalation.recorded`, each against its mirrored chunk and ticked as acked
6. **do not clear the local pause from the panel** — the same no-tamper condition `blizzard-mock:manual-seeded-board`
   pins for the board's own no-restart requirement: one click unbrakes FILL, which claims the board's `ready` chunk and
   spawns real workers
7. wait at least one tick (30 seconds by default — watch the runner's log for `tick end` to confirm one has landed),
   then re-check every panel from steps 3–5, plus now the **HUB** panel: it should read a `link` row valued `CONNECTED`
   and a `loop` row valued `PAUSED` — the seeded local brake — now that the runner's own registry sync has recreated
   `hub_control` on this first tick. Every other seeded row still renders, unchanged. The **LOCAL FACT LOG** may grow:
   step 1's `reset --store runner` empties `external_usage_samples`, so its cadence anchor (`max(sampled_at)`) is `None`
   and the interval gate does not apply on this first tick — the sampler runs unconditionally, and an
   `external_subscription_usage.sampled` fact lands only if it returns a snapshot (only when an access token is
   readable). Whether or not it lands, the seeded two facts must still be there and still ticked
8. re-open the board from step 2 and confirm every chunk's status and the overall census are unchanged.

Pass: every panel checked in steps 3–5 renders populated (the HUB panel's `link`/`loop` rows excepted, first checked in
step 7), and after step 7's tick every seeded row still renders unchanged (the fact log's daemon-appended rows excepted)
with the HUB panel now reading `link` `CONNECTED` and `loop` `PAUSED`, and the board's chunk statuses and census from
step 2 are unchanged in step 8 — the daemon reconciled the mirrored fleet without altering either store's seeded shape.

The seeded runner-store `usage_facts` and `transcript_segments` have no panel surface (see Surface above); check them in
the store instead —
`sqlite3 "$BZ_RUNNER_RUNTIME/data/runner.db" 'select chunk_id from usage_facts; select chunk_id from
transcript_segments;'`
names the same two mirrored chunk ids.
