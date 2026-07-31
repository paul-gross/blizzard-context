# Store seeding (`bzh:store-seeding-guide`)

**Rule.** Develop and demo the board against a local store seeded directly by `blizzard-mock-data` (`tool:mock-data`) — never against the hosted deployment. Reach for the real wire path (a configured `[[work_source]]`, a minted forge fixture, and a real `POST /api/chunks` ingest) only when the ingest path itself, not the data it produces, is what's under test.

**Why.** `blizzard-mock-data` reflects the live hub/runner schema at runtime and writes fact rows directly (`bzh:facts-not-status`), so a realistic board renders in one command with no forge, no work source, and no daemon restart — the ingest path exists to prove the same facts arrive *through the wire*, a slower, heavier proof this guide's first path never needs to pay for. `workspace:/context/project/local-instance.md` states the standing constraint that a dev surface never points at the hosted hub; this guide doesn't restate why, only where seeding fits inside it.

## The direct store-seed path (recommended)

Every `blizzard-mock-data` verb takes a target store as `--url <DSN>`/`$DATABASE_URL`, or as `--dir <runtime dir>` — sugar that reads the runtime's `blizzard-hub.toml`/`blizzard-runner.toml` `db_url` (`internal/hub_runtime.py`). Inside a provisioned feature env, `$BZ_HUB_RUNTIME` is that directory (`workspace:/.winter/config.toml`), so every example below runs as-is once `winter service up <env>` has brought the env's hub up at least once (its startup runs `blizzard hub init "$BZ_HUB_RUNTIME"`).

One command, one board:

```bash
blizzard-mock-data scenario board --chunks 6 --stress --dir "$BZ_HUB_RUNTIME"
```

Seeds a synthetic graph, six chunks spread deterministically across all nine derived statuses, a varying cost spread (at least one cost-partial usage fact), a ceiling-paused runner, a runner per chunk, and a mixed-severity event log; `--stress` layers on four narrow-viewport/overflow extremes (a long-identity runner, a long custom node name, and a second `waiting_on_human` chunk carrying two extra question trails). Pass `--seed N` to pin both id-minting and the clock for byte-identical reruns. Always the hub store — there is no `--store` flag on `scenario board` to get wrong.

Reset first when the store isn't already known-clean:

```bash
blizzard-mock-data reset --store hub --dir "$BZ_HUB_RUNTIME"
```

Reach for the nine `create` verbs individually when a scenario needs one hand-placed concept rather than a whole board — `create chunk`'s output pipes into a sibling verb:

```bash
chunk_id=$(blizzard-mock-data create chunk --store hub --status running --dir "$BZ_HUB_RUNTIME")
blizzard-mock-data create usage --store hub --chunk "$chunk_id" --kind spawn --model claude-opus-4 \
  --input-tokens 4000 --output-tokens 800 --no-cost --dir "$BZ_HUB_RUNTIME"
blizzard-mock-data create question --store hub --chunk "$chunk_id" --text "Which config wins?" \
  --dir "$BZ_HUB_RUNTIME"
```

Full verb reference — every flag, every default, on all nine `create` subcommands plus `reset` and `scenario board` — is the tool's own contract at the `blizzard-mock` repo's `src/blizzard_mock/mock_data/README.md`; this guide shows how to reach for it, not what every flag does.

### The drift guard

Every write is checked against the live store's *reflected* schema before it lands (`domain/schema_contract.py`) — never a silently-wrong row. A miss raises `SchemaDriftError` and the CLI exits non-zero, naming the table and the offending column(s):

```
schema drift: table 'usage_facts' has no column(s) ['bogus_column'] — see blizzard-context:/tooling/store-seeding.md
schema drift: table 'lease_facts' requires column(s) ['epoch'], not supplied — see blizzard-context:/tooling/store-seeding.md
```

A drift means the live store moved out from under a `domain/*_seed.py` composer (a migration added, renamed, or tightened a column) — fix the composer, not the guard.

## The real wire path (when ingest itself is under test)

The direct path above writes facts straight into the store; it never touches the hub's ingest API, a configured work source, or the mock forge. When the thing under test is the ingest arc itself — a work-source config, `POST /api/chunks`, or the runner's first claim/lease sequence — drive it for real instead. The end-to-end sequence (mint a fixture, drop the harness fence marker, file a forge issue, `POST /api/chunks`) is already documented at `blizzard:manual` ([../verification/blizzard.md](../verification/blizzard.md)); this guide only adds three facts about the arc's own mechanics that aren't written up elsewhere, each re-confirmed here by reading the code rather than copied from a plan:

- **The first claim envelope carries `epoch: 0`; the runner's first minted lease is `epoch: 1`.** A claim never mints a lease — it carries the chunk's current epoch (`latest_epoch(facts) or 0`) into the envelope so the worker can start without a round-trip (`blizzard/src/blizzard/hub/domain/claim.py`, `_claim_locked` and its module docstring). The runner mints the actual lease afterward, always strictly above both the hub-supplied floor and its own local fence: `epoch = max(ctx.store.latest_epoch(chunk_id), envelope.epoch) + 1` (`blizzard/src/blizzard/runner/loop/steps.py`, `_spawn_attempt`) — on a fresh chunk both floors are 0, so the first lease always mints at 1.
- **The runner's outbound buffer `seq` is a per-runner monotonic autoincrement, not a per-chunk or global counter.** `outbound_buffer.seq` is the table's autoincrement primary key, commented "per-runner monotonic" on the column itself (`blizzard/src/blizzard/runner/store/schema.py`); `enqueue_outbound` returns the inserted key as the fact's `seq` (`blizzard/src/blizzard/runner/store/internal/sqlalchemy_store.py`). Every fact this runner ever buffers — across every chunk and lease it drives — shares the one increasing sequence.
- **A `[[work_source]]` edit needs a restart to take effect.** The hub reads `blizzard-hub.toml` once, at `blizzard hub host --dir <dir>` startup (`blizzard/src/blizzard/hub/cli.py`) — there is no reload or SIGHUP handler, so an edit to the runtime's config is inert until the process restarts. Pick it up with:

  ```bash
  winter service restart <env>/hub
  ```

  the pattern-glob shape `winter service restart` takes (`workspace:/context/winter-cli/usage/service.md`).

## Don't

- Point `blizzard-mock-data`, `ng serve`, or any dev surface at the hosted deployment (`https://blizzard.grosscode.net`) to develop or demo against — `workspace:/context/project/local-instance.md` owns why; this guide's first path exists precisely so nothing needs to.
- Reach for `fixture list`/`fixture apply` — the named, versioned, cross-store scenario surface remains a stub (`_not_implemented`, `src/blizzard_mock/mock_data/cli.py`). `scenario board` is the one-command preset surface this feature actually delivers; it is not a stopgap for `fixture`, and `fixture` is not a "coming soon" spelling of it.
- Hand-edit a hub/runner store's rows with raw SQL to work around a `SchemaDriftError` — fix the composer (or, if the schema itself moved, treat the drift as the actionable signal it is) rather than routing around the guard that exists to catch exactly that.

## See also

- [../verification/blizzard/tools.md](../verification/blizzard/tools.md) — `tool:mock-data`, what the tool's verb surface asserts is available for verification setup.
- [../verification/blizzard.md](../verification/blizzard.md) — `blizzard:manual`, the full ingest sequence (fixture, fence marker, forge issue, `POST /api/chunks`) the real wire path above rides.
- `workspace:/context/project/local-instance.md` — the standing "never against the hosted hub" rule this guide's first path exists to satisfy.
- The `blizzard-mock` repo's `src/blizzard_mock/mock_data/README.md` — the tool's own component contract: every verb's exact flags and defaults.
