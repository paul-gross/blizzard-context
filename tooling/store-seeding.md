# Seeding a store to develop against (`bzh:store-seeding-guide`)

Develop and demo the board against a local store seeded directly by `blizzard-mock-data` (`tool:mock-data`); never point
`blizzard-mock-data`, `ng serve`, or any other dev surface at the hosted deployment, whose standing rule
`workspace:/context/project/local-instance.md` owns.

Reach for the real wire path — a configured `[[work_source]]`, a minted forge fixture, and a real `POST /api/chunks`
ingest — only when the ingest path itself, rather than the data it produces, is what is under test. The sequence that
path rides is owned by `blizzard:manual` in [`../verification/blizzard.md`](../verification/blizzard.md). An edit to a
`[[work_source]]` entry takes effect only after a restart — `winter service restart <env>/hub` — because the hub reads
`blizzard-hub.toml` once at `blizzard hub host` startup and has no reload or SIGHUP handler.

## Running it

Every seeding command assumes a provisioned env whose shell vars have been sourced with `source <(winter env <env>)`,
and runs from the sibling `blizzard-mock` worktree under its own venv, as `uv run blizzard-mock-data …`.
`$BZ_HUB_RUNTIME` and `$BZ_RUNNER_RUNTIME` are winter-injected service vars declared in
`workspace:/.winter/config.toml`, not plain environment variables.

Every verb except `scenario fleet` names its target store either as `--url <DSN>` (or `$DATABASE_URL`) or as
`--dir <runtime dir>`, the sugar that reads the runtime config's `db_url`.

Run `uv run blizzard-mock-data reset --store hub --dir "$BZ_HUB_RUNTIME"` first whenever the store is not already
known-clean.

## Seeding a board

`scenario board` seeds a whole board in one command and writes only the hub store:

```sh
uv run blizzard-mock-data scenario board --chunks 6 --stress --dir "$BZ_HUB_RUNTIME"
```

Reach for the per-concept `create` verbs individually when a scenario needs one hand-placed concept rather than a whole
board. `create chunk` prints the minted chunk id, so its output pipes into the sibling verbs that take the chunk as an
argument.

## Seeding both stores together

`scenario fleet` composes a second, runner-store half from the same chunk ids mirrored under one pinned runner id, so
the runner's own local panel renders leases, asks, escalations, takeovers, environments, and facts alongside the seeded
board:

```sh
uv run blizzard-mock-data scenario fleet --chunks 6 --seed 1 --hub-dir "$BZ_HUB_RUNTIME" --runner-dir "$BZ_RUNNER_RUNTIME"
```

It names its two stores explicitly and separately, and neither half falls back to `$DATABASE_URL`. A `--dir`-family flag
resolves only after `winter service up <env>` has brought that daemon up at least once, because the daemon's first start
is what writes the `blizzard-hub.toml` or `blizzard-runner.toml` the flag reads; `--runner-dir` reads the pinned
`runner_id` from that file as well as `db_url`.

Do not reach for `fixture list` or `fixture apply`: the named, versioned, cross-store scenario surface is still a stub,
and `scenario board` and `scenario fleet` are the one-command preset surfaces that exist.

## Seeding an env whose daemons are up

A running runner daemon rewrites its store every tick, so `scenario fleet`'s mirrored chunks are composed dormant rather
than as live running leases — an active lease with no worker process behind it is reaped as a stalled attempt within one
tick. Leave the seeded runner's own local pause engaged and do not clear it from the panel: one click unbrakes FILL,
which claims the board's `ready` chunks and spawns real workers.

A seed made once the runtime config exists survives every later restart or shutdown, daemon up or down: the runner falls
back to the same `runner-local` id on every start because the workspace injects no override, and the runner store is
never cleared.

## When a write meets a moved schema

Every write is preceded by a drift guard: when the live store's schema no longer carries a table or column a composer
expects, the command fails loud and names the table and column rather than landing a silently-wrong row. The guard's
home is `blizzard-mock/src/blizzard_mock/mock_data/domain/schema_contract.py`.

Do not hand-edit a store's rows with raw SQL to work around a `SchemaDriftError` — fix the composer, or, if the schema
itself moved, treat the drift as the actionable signal it is.

## See also

- The `blizzard-mock` repo's `src/blizzard_mock/mock_data/README.md` — every verb's exact flags and defaults, and what
  `scenario board` and `--stress` seed.
- [`../verification/blizzard/tools.md`](../verification/blizzard/tools.md) — what `tool:mock-data`'s verb surface makes
  available for verification setup.
- `blizzard-mock:manual-seeded-board` and `blizzard-mock:manual-seeded-fleet` in
  [`../verification/blizzard.md`](../verification/blizzard.md) — the manual methods that exercise this guide's direct
  path on a live env, board alone and board plus mirrored runner.
- [`../domain/execution/fencing.md`](../domain/execution/fencing.md) (`bzh:epoch-fencing`) — the epoch a fresh claim or
  lease carries; [`../architecture/crash-correctness.md`](../architecture/crash-correctness.md) — the gapless
  outbound-buffer sequence invariant governing how the runner's outbound buffer sequences its facts.
