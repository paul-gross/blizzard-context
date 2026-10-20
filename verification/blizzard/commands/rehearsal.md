# The upgrade rehearsal command detail (`bzh:matrix-command-rehearsal`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `### blizzard:rehearsal` heading and its cited code spans — test paths, and the `mise run rehearsal` pairing with its exact command text — are machine-checked; keep them verbatim. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:rehearsal

`BLIZZARD_REHEARSAL=1 uv run pytest -m rehearsal tests/rehearsal/` (`mise run rehearsal`) — the upgrade an operator
performs, rehearsed for real: each supported release's own published wheel seeds a hub and a runner host, the hub is
upgraded first to the candidate, the baseline runner keeps working against it, then the runner is upgraded too, and both
stores are walked down to the baseline and forward again. It is skipped without `BLIZZARD_REHEARSAL=1`, and a tree with
no supported release skips it and says so. The contract is
`blizzard-product:/plans/release-engineering/compat-floor/spec/rehearsal.md`.

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
