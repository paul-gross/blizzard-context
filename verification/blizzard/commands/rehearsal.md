# The published-release command detail (`bzh:matrix-command-rehearsal`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `### blizzard:rehearsal` heading and its cited code spans — test paths, and the `mise run rehearsal` pairing with its exact command text — are machine-checked; keep them verbatim. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:rehearsal

`scripts/rehearsal.sh` (`mise run rehearsal`) — the upgrade an operator performs, rehearsed for real: each supported
release's own published wheel seeds a hub and a runner host, the hub is upgraded first to the candidate, the baseline
runner keeps working against it, then the runner is upgraded too, and both stores are walked down to the baseline and
forward again. It is skipped without `BLIZZARD_REHEARSAL=1`, and a tree with no supported release skips it and says so.
The contract is `blizzard-product:/plans/release-engineering/compat-floor/spec/rehearsal.md`.

**Inputs.** Each leg holds two isolated virtualenvs, every daemon and verb a subprocess: the baseline is the release's
published wheel from its GitHub Release, and the candidate is the wheel built from HEAD. `blizzard-mock` is checked out
at the baseline's tag, or its `master` when the baseline has none. The legs are a matrix over the supported releases,
each running the hub store on SQLite and on Postgres; the runner store is SQLite only.

**What it asserts.**

- The seeded baseline hub, migrated by the candidate, starts, answers `/api/ready`, and serves the seeded chunks' views
  unchanged in every field the baseline's document carried.
- The baseline runner host, untouched, is admitted by the candidate hub's handshake, lands a fresh chunk, and finishes
  the chunk it left delivering — read back as landed through the hub's API.
- The candidate runner host, migrated, resumes its runners and lands one more chunk.
- The walk down to each store's baseline head revision, read from the baseline tag's `contracts/store/*.json`, loses no
  seeded row: every table holds at least its seeded count, the seeded views match their fingerprints, and the baseline
  daemons start on the walked stores; the walk forward again leaves each candidate daemon ready.
- On the Postgres leg, an empty hub store migrated to head reflects equal to `contracts/store/hub.json` through the same
  producer `blizzard:store-contract` uses on SQLite.

A failing step names the step, the baseline, and the backend, and attaches both daemons' logs.

**Where it runs, and why never on a pull request.** `.github/workflows/rehearsal.yml` is reusable, called by `push.yml`
on every `master` push — `dev-image` needs it, so `edge` advances only on a commit whose upgrade from every supported
release succeeded — and by `release.yml` on every `-rc.` tag before the image push. A stable tag promotes a candidate's
commit and relies on its candidate's run. A pull request does not run it: it takes minutes, and `blizzard:compat`
already holds every pull request to the same releases statically, so the rehearsal is the post-merge proof that the
static check's verdict holds for a real upgrade, not an ungated check.

### blizzard:store-baseline

`BLIZZARD_STORE_BASELINE=1 uv run --extra postgres pytest -m store_baseline tests/test_store_baseline.py`
(`mise run store-baseline`) — the proof that a fold replaced a store's migration history without changing the store it
builds. For each tree, the baseline alone is applied to an empty store, the floor release's own published wheel builds
its history's store from empty with its own `migrate` verbs, and the two are compared on the same backend: every table's
columns (type, nullability, default), primary key, foreign keys, unique constraints and indexes, by name; every row; and
on SQLite each table's `AUTOINCREMENT`, read from its DDL. The contract is
`blizzard-product:/plans/release-engineering/release-lines/spec/fold.md` §The two proofs.

It is skipped without `BLIZZARD_STORE_BASELINE=1`, and skips and says so while no tree's base revision declares a
`BASELINE_FLOOR`, which is every run before the first fold. `BLIZZARD_STORE_BASELINE_PG_URL` names the Postgres server
the Postgres legs create a throwaway database on; unset, those legs skip and say why, and under `CI` unset fails. It
downloads the floor's wheel, so it needs `gh` access (`GH_TOKEN`).

**Seeded values.** A history seeds rows whose ids are minted from the clock and `os.urandom` and whose instants are
stamped when they run, so no two runs agree. The baseline mints and stamps those afresh, and the comparison reads them
as `blizzard.tools.store_fold.seeds.normalize` does: ids up to a consistent renaming, instants by presence.

**The runner on Postgres.** The runner's history cannot reach head on Postgres from an empty store
(`20260920_0200_usage_cost_is_share` sets a Boolean `server_default` of `0`, which Postgres rejects), so that one leg
holds the baseline's Postgres store to the floor's committed `contracts/store/runner.json` through the producer
`blizzard:store-contract` uses, and its rows to the runner history's SQLite rows. This is the one place the proof
departs from comparing a history's store with the baseline's on the same backend.

**One named normalization.** A table the history renamed keeps its old name on its Postgres-generated primary key,
foreign key and serial sequence, which a baseline creating the table under the new name cannot reproduce. The test names
each such table beside the name it was renamed from; nothing else is read away, so a difference not of that class fails.

**Where it runs.** `.github/workflows/store-baseline.yml` is reusable, called by `pr.yml` when a pull request changes
either tree's `versions/` directory and by `release.yml` on candidate and patch tags, never a stable promotion. It is
not a required check on `master`, and not in `blizzard:gate`: the gate is token-free and reaches no network beyond
package installs.
