# Store seeding (`bzh:store-seeding-guide`)

**Rule.** Develop and demo the board against a local store seeded directly by `blizzard-mock-data` (`tool:mock-data`) —
never against the hosted deployment (`workspace:/context/project/local-instance.md` owns why; this guide's first path
exists precisely so nothing needs to). Reach for the real wire path (a configured `[[work_source]]`, a minted forge
fixture, and a real `POST /api/chunks` ingest) only when the ingest path itself, not the data it produces, is what's
under test.

## Running it — invocation context

Every example below assumes: a provisioned env, its shell vars sourced (`source <(winter env <env>)` —
`$BZ_HUB_RUNTIME`/`$BZ_HUB_WEB_PORT` are winter-injected service vars, not plain env vars, per
`workspace:/.winter/config.toml`), and the sibling `blizzard-mock` worktree's own venv as the command's `cwd`:

```bash
source <(winter env <env>)
cd <env>/blizzard-mock && uv run blizzard-mock-data scenario board --chunks 6 --stress --dir "$BZ_HUB_RUNTIME"
```

`$BZ_HUB_RUNTIME` resolves once `winter service up <env>` has brought the env's hub up at least once (its startup runs
`blizzard hub init "$BZ_HUB_RUNTIME"`, which is what seeds the `blizzard-hub.toml` this tool's `--dir` reads).

## The direct store-seed path (recommended)

Every verb except `scenario fleet` takes its target store as `--url <DSN>`/`$DATABASE_URL`, or as `--dir <runtime dir>`
— sugar that reads the runtime's `blizzard-hub.toml`/`blizzard-runner.toml` `db_url` (`blizzard-mock` repo's
`src/blizzard_mock/mock_data/internal/runtime_config.py`). `scenario fleet` names two stores and so takes neither form;
§Seeding both stores together owns its flags.

One command, one board:

```bash
blizzard-mock-data scenario board --chunks 6 --stress --dir "$BZ_HUB_RUNTIME"
```

The board it seeds also carries an artifact spread — a chunk detail page's Artifacts tab and its Node history tab's
per-step artifact panel both render something without a real workload, the `done` chunk's own two node-steps included.

Reset first when the store isn't already known-clean:

```bash
blizzard-mock-data reset --store hub --dir "$BZ_HUB_RUNTIME"
```

Reach for the per-concept `create` verbs individually when a scenario needs one hand-placed concept rather than a whole
board — `create chunk`'s output pipes into a sibling verb:

```bash
chunk_id=$(blizzard-mock-data create chunk --store hub --status running --dir "$BZ_HUB_RUNTIME")
blizzard-mock-data create usage --store hub --chunk "$chunk_id" --kind spawn --model claude-opus-4 \
  --input-tokens 4000 --output-tokens 800 --no-cost --dir "$BZ_HUB_RUNTIME"
blizzard-mock-data create question --store hub --chunk "$chunk_id" --text "Which config wins?" \
  --dir "$BZ_HUB_RUNTIME"
```

Every verb's exact flags, defaults, and what `scenario board`/`--stress` seed is the tool's own contract at the
`blizzard-mock` repo's `src/blizzard_mock/mock_data/README.md` — this guide shows how to reach for it, that doc owns
what each flag does.

Every write runs a drift guard first (`blizzard-mock` repo's `src/blizzard_mock/mock_data/domain/schema_contract.py`) —
a schema drift (a table or column the live store no longer carries as a composer expects) fails loud, naming the table
and column, rather than landing a silently-wrong row; see that README's Design section for the mechanism.

## Seeding both stores together — `scenario fleet`

`scenario board` above stays within the hub store alone. `scenario fleet` composes a second runner-store half — the same
chunk ids, mirrored under one pinned runner id — sharing the hub board's graph id and its `build` node's id, name, and
epoch (the mirror mints its own ask/question ids, not the hub board's) — so the runner's own local panel renders leases,
asks, escalations, takeovers, environments, and facts alongside the seeded board. Its `usage_facts` and
`transcript_segments` are seeded for store-level coherence only; the local API exposes no surface for either, so nothing
renders them:

```bash
blizzard-mock-data scenario fleet --chunks 6 --seed 1 \
  --hub-dir "$BZ_HUB_RUNTIME" --runner-dir "$BZ_RUNNER_RUNTIME"
```

The hub and runner stores must each be named **explicitly and separately** — neither falls back to `$DATABASE_URL`,
since one env var cannot name two stores. Which flags do that naming, and where the pinned runner id comes from, is the
README's own contract (see above).

**Seed only once `winter service up` has brought the runner up at least once.** `--runner-dir` resolves `db_url` and
`runner_id` by reading the runtime's `blizzard-runner.toml`, which doesn't exist until the runner's first start writes
it — the requirement is that resolution, not a live daemon: the runner falls back to the same `runner-local` id on every
start (the workspace injects no override), and the runner store itself is never cleared, so a seed made once the toml
exists survives every later restart or shutdown, daemon up or down. `blizzard runner host` is the only serve mode — the
reconciliation loop and the local API are one process — so whenever the daemon *is* running it rewrites the store every
tick; that's why `scenario fleet`'s two mirrored chunks (a `waiting_on_human` chunk parked on an open ask; a
`needs_human` chunk under a closed, escalated lease and an open takeover) are composed dormant rather than as a live
running lease — an active lease with no worker process behind it is reaped as a stalled attempt within one tick,
whenever the daemon next runs. The seeded runner's own local pause stays engaged for the same reason, so the board's
`ready` chunks are never claimed out from under the seed. **Do not clear the local pause from the panel** — the same
condition `blizzard-mock:manual-seeded-board` pins for the board's own no-restart requirement: one click unbrakes FILL,
which claims the board's `ready` chunks and spawns real workers.

## The real wire path (when ingest itself is under test)

The direct path above writes facts straight into the store; it never touches the hub's ingest API, a configured work
source, or the mock forge. When the thing under test is the ingest arc itself — a work-source config,
`POST /api/chunks`, or the runner's first claim/lease sequence — drive it for real instead, following the sequence
`blizzard:manual` already documents ([../verification/blizzard.md](../verification/blizzard.md): mint a fixture, drop
the harness fence marker, file a forge issue, `POST /api/chunks`).

One mechanic of that arc belongs here rather than there, because it's what an edit to this path needs to know: **a
`[[work_source]]` edit needs a restart to take effect.** The hub reads `blizzard-hub.toml` once, at
`blizzard hub host --dir <dir>` startup (`blizzard/src/blizzard/hub/cli.py`) — there is no reload or SIGHUP handler, so
an edit to the runtime's config is inert until the process restarts:

```bash
winter service restart <env>/hub
```

For the epoch a fresh claim/lease carries and how the runner's outbound buffer sequences its facts, see
[../domain/execution/fencing.md](../domain/execution/fencing.md) (`bzh:epoch-fencing`) and
[../architecture/crash-correctness.md](../architecture/crash-correctness.md)'s gapless-outbound-seq invariant — this
guide doesn't restate them.

## Don't

- Point `blizzard-mock-data`, `ng serve`, or any dev surface at the hosted deployment to develop or demo against.
- Reach for `fixture list`/`fixture apply` — the named, versioned, cross-store scenario surface remains a stub
  (`_not_implemented`, `blizzard-mock` repo's `src/blizzard_mock/mock_data/cli.py`). `scenario board`/`scenario fleet`
  are the one-command preset surfaces this feature actually delivers; neither is a stopgap for `fixture`.
- Seed `scenario fleet`'s runner half before `winter service up` has brought the runner up at least once — see above;
  `--runner-dir` has no `blizzard-runner.toml` to resolve `db_url`/`runner_id` from until that first start writes it.
- Hand-edit a hub/runner store's rows with raw SQL to work around a `SchemaDriftError` — fix the composer (or, if the
  schema itself moved, treat the drift as the actionable signal it is) rather than routing around the guard that exists
  to catch exactly that.

## See also

- [../verification/blizzard/tools.md](../verification/blizzard/tools.md) — `tool:mock-data`, what the tool's verb
  surface asserts is available for verification setup.
- [../verification/blizzard.md](../verification/blizzard.md) — `blizzard:manual`, the full ingest sequence the real wire
  path above rides; `blizzard-mock:manual-seeded-board`/`blizzard-mock:manual-seeded-fleet`, the manual methods that
  exercise this guide's direct path — board alone, or board plus mirrored runner — on a live env.
- `workspace:/context/project/local-instance.md` — the standing "never against the hosted hub" rule.
- The `blizzard-mock` repo's `src/blizzard_mock/mock_data/README.md` — the tool's own component contract: every verb's
  exact flags and defaults.
