# Performing a `blizzard:` manual method (`bzh:matrix-manual-detail`)

<!-- One flat `###` section per method id — the shape this file's sibling spokes share. -->
<!-- rumdl-disable MD001 -->

Full detail for the `blizzard:` manual methods named in [`../blizzard.md`](../blizzard.md)'s Manual testing table, one
section per row, in that table's order. The `blizzard-mock:` methods live in [`./manual-mock.md`](./manual-mock.md).

### `blizzard:manual`

**Surface.** The walking skeleton — one chunk traveling ingest, acquire, mock-scripted commit, deliver, and landed in a
bare origin, with `done` derived from facts.

**Setup.** A fixture-workspace env (`tool:fixture-workspace`) with the hub, the runner, and the mock fleet bound, and
sqlite up via each daemon's embedded store.

**Steps.** This method is automated, and [`../blizzard.md`](../blizzard.md#manual-testing)'s Manual testing row names
the tier that runs the loop and stands the stack up for you. Two routes drive it by hand instead: read the
`mise run e2e` source for the exact in-process sequence, or walk it against live services —

1. `winter service up <env> --wait`, bringing up forge, hub, and runner.
2. `blizzard-mock-fixture reset --env <env>`.
3. Drop the harness fence marker in its `workspace/`.
4. File a forge issue.
5. `POST /api/chunks`, so the hosted runner ticks it to `done`.

**Passes when.** The chunk lands in the bare origin and the hub's facts derive `done`, run fully locally with no tokens
and no network.

### `blizzard:manual-sse-probe`

**Surface.** What only a live socket can show: timing and framing over the wire — the reserved open-of-stream comment,
the periodic keepalive comment, and the `id`/reconnect-replay behavior observed on a real `GET /api/events/stream`
connection. Frame-level field shape is `blizzard:sse-contract`'s claim against the golden corpus `contracts/sse/`, not
this method's.

**Setup.** The daemon under test, hosted on a scratch port. `init` takes only a positional directory and has no `--dir`,
while `host` accepts either form and is the only one that binds `--port`:

```bash
blizzard hub init <dir> && blizzard hub host --dir <dir> --port <p>
blizzard runner init <dir> && blizzard runner host --dir <dir> --port <p>
```

The probe is not hub-only — the runner serves the identical stream shape at its own `GET /api/events/stream` — so a run
is scoped to one daemon at a time and never needs both up.

**Steps.**

1. Start the daemon under test on the scratch port.
2. Hold an SSE subscription open against its `GET /api/events/stream` with `curl -N` or a streaming client, before
   driving the act.
3. Drive each publish site over HTTP — the endpoint or CLI call behind the `broker.publish_*` call under test.
4. Assert that the reserved comment opens the stream, that a keepalive comment arrives on an idle connection within the
   cadence `src/blizzard/foundation/events/stream.py`'s `DEFAULT_KEEPALIVE_SECONDS` declares, and that the frames'
   `id`/reconnect-replay behavior holds on a live socket. The hub's and the runner's reserved open-of-stream comments
   carry different literal text, so check the one the daemon under test actually owns.

**Passes when.** That framing and timing behavior holds over a real connection for every call driven.

### `blizzard:manual-standing-idp`

**Surface.** `blizzard:e2e`'s login-session scenario proves the full OAuth dance and its role-dependent UI only for a
pytest fixture's lifetime, so this method covers the same behavior against a standing hub a human or a
`frontend-verifier` agent can point a real browser at in a provisioned feature env. It stays manual because no automated
tier drives a real browser against a standing, out-of-fixture process pair, and giving the e2e tier a persistent-process
mode it does not otherwise need costs more than the surface is worth.

**Setup.** Start the stub IdP standing per `blizzard-mock/src/blizzard_mock/idp/README.md` §"Standing instance" —
`blizzard-mock-idp --host 127.0.0.1 --port <idp-port>`, confirmed with `GET /healthz`. Run `mise run web-build` so the
hub serves the built board. Give the hub a runtime dir — a scratch dir, or a provisioned env's own `$BZ_HUB_RUNTIME` if
that env's hub is meant to run in `oauth` mode — carrying `[auth] mode = "oauth"` and one
`[[auth.oauth.provider]] type = "oidc"` entry whose `issuer` points at the standing IdP. The auth mode value is
`"oauth"`, not `"oidc"`; `oidc` is the provider `type` (`hub/config.py`'s `AUTH_MODE_OAUTH`). `auth.mode = "none"` is
the default a `winter service up <env>`-started hub scaffolds via `blizzard hub init`, so a running env's own service
stack serves everything unauthenticated until this setup is applied to it.

**Steps.**

1. Start the hub with `blizzard hub host --dir <hub-dir> --port <hub-port>`.
2. Drive a real browser to `http://127.0.0.1:<hub-port>/`, confirm the `/login` gate renders the configured provider's
   button, click it, and confirm the dance lands authenticated — a fresh identity mints `pending`.
3. Script a specific identity with `PUT /_levers/profile` on the IdP before a login, or flip it between two logins in a
   fresh browser context each time to prove two distinct identities.
4. Confirm role-dependent UI by setting a role directly in `<hub-dir>/data/hub.db`'s `users` table — the seam
   `blizzard:e2e`'s login-session scenario uses ahead of a role-assignment API — and reloading on the same session
   cookie: a not-ready chunk's Promote control is present for `contributor` and absent for `guest`.

**Passes when.** The browser reaches an authenticated board through the standing IdP and at least two roles are observed
rendering visibly different UI on the same underlying state.

### `blizzard:manual-external-usage-probe`

**Surface.** No CI tier can prove a declared subscription's provider's real usage-endpoint response shape: the tier
rules forbid service and e2e tests from touching the network, and a provider's endpoint is typically undocumented and
unversioned, so it can drift with no changelog to catch it. Every CI-tier test exercises subscription-usage sampling
against a stubbed transport, and this probe is what ties that stub back to what the provider actually returns. A runner
with no `[[subscription]]` declared has exactly one slug to name, the legacy `anthropic` slug (Claude Code); one with
declarations names any of its own slugs instead, and none of them is guaranteed to be `anthropic`.

**Setup.** The runner machine's own real OAuth credentials for the slug under test (`~/.claude/.credentials.json` for
`anthropic`) and a working `blizzard runner` binary.

**Steps.** Run `blizzard runner external-usage probe <slug>` (e.g. `probe anthropic`), a read-only diagnostic
subcommand, then separately read that provider's own usage view for the same account (Claude Code's own `/usage`
command, for `anthropic`), and compare the two.

**Passes when.** The probe's parsed utilization percentages and reset times match what the provider's own usage view
reports for the same account, within the natural few-second sampling skew.

### `blizzard:manual-retired-wire-response-vocabulary-census`

**Surface.** Retired subscription wire-response vocabulary in the `blizzard` app repo — the response types, fields,
projections, and rendering paths a subscription-shape retirement was supposed to remove, plus the prose that still
describes them as live.

**Setup.** Run in the `blizzard` worktree of the feature env the retirement was built in, or in `projects/blizzard/`
when working from the source checkout; `workspace:/context/workspace-layout.md` owns both shapes. The mock's mirror of
these response models is not in surface here — `blizzard-mock:unit-test`'s wire-parity guard holds it mechanically.

**Phrase declarations.** Search these exact identifiers and semantic legacy-shape phrases:

- `ExternalSubscriptionUsageView`
- `LegacySubscriptionUsageView`
- `external_subscription_usage`
- `legacy usage`
- `legacy snapshot`
- `legacy field`
- `legacy fallback`
- `one usage sample`
- `single usage sample`
- `newest usage sample`

**Classifications.** Apply these tests in order and stop at the first that matches, so every occurrence has exactly one
verdict:

1. **Out of surface** — the `[external_subscription_usage]` key in `blizzard-runner.toml` or the code and prose reading
   it, and the `external_subscription_usage.sampled` fact-kind string. These name a config table and a fact, not a wire
   response; a retirement of the response shape never touches them.
2. **Retained** — a frozen migration's restated literal (`bzh:frozen-revisions`), current per-slug storage, or a test or
   scenario name naming the fact rather than the response.
3. **Deleted** — everything else: a wire response type or field, a legacy projection, a fallback rendering path, or
   prose or a test asserting the retired and current shapes coexist.

**Steps.** Record `git rev-parse HEAD`, then search tracked content with:

```bash
pattern='(External|Legacy)SubscriptionUsageView|external_subscription_usage'
pattern="${pattern}|[Ll]egacy (usage|snapshot|field|fallback)"
pattern="${pattern}|([Oo]ne|[Ss]ingle|[Nn]ewest) usage sample"
git grep -n -E "$pattern"
```

Read every hit in its surrounding context — the phrase alone never decides a verdict — and classify each under the
ordered tests above. This is a census, not a sweep: it reads the tree and does not change it. A `deleted` occurrence is
a failure to report, not something the pass removes on its way through.

**Evidence.** Record the revision, the search expression, the total hit count, and one line per occurrence giving its
path, line, phrase, class, and the reason that class was reached. Keep it with the change under review — the pull
request or commit that claims this method — rather than in this file, which holds no per-run readings
(`../standards/prose-budget.md`).

**Passes when.** Every occurrence classifies as out-of-surface or retained, and none classifies as deleted.

### `blizzard:manual-opencode-compatibility`

**Surface.** The live CLI/provider compatibility surface for OpenCode `1.18.25` with ChatGPT `5.6 Luna`
(`openai/gpt-5.6-luna`) at `max`, covering the diagnostic's:

- `fresh_turn`, `resume`, `process_control`, `judgement`, `root_hook`, `permission`, and `model_variant`
- `usage_cost`, `takeover`, `transcript_read`, `transcript_cursor`, `child_sessions`, and `configuration_isolation`

**Procedure.** Follow the public operator procedure at `blizzard/docs/deployment/opencode-compatibility.md` for
prerequisites, invocation, live opt-in, credential and evidence handling, failure conditions, and interpretation.

**Retained evidence.** Retain the diagnostic output and the sanitized `report.json` and `runtime.json` files from the
evidence directory.

**Passes when.** The command exits zero, the output reports OpenCode version `1.18.25` and ends with
`compatibility: supported` or `compatibility: degraded`, and `report.json` records `complete: true` and
`admissible: true`. This diagnostic result is not production adapter availability or a harness-selection decision.

### `blizzard:manual-opencode-compatibility-rehearsal`

**Surface.** That `blizzard/docs/deployment/opencode-compatibility.md`'s stated offline rehearsal path — emit a
CLI-surface artifact and point `--binary` at it to exercise the whole diagnostic flow without provider quota — is itself
followable exactly as written, by an operator with no prior knowledge of the mock fleet's internals. This is distinct
from `blizzard:manual-opencode-compatibility`, which proves the pinned live contract against a real provider; this
method proves a page.

**Procedure.** Against a provisioned feature env, follow the page's stated rehearsal steps in order and no others: emit
the artifact with the documented `mock-opencode` verb, then invoke the diagnostic with `--binary` pointed at the emitted
path.

**Passes when.** The page's steps are sufficient on their own — no undocumented flag, path, or prerequisite is needed —
and the run ends the way the page says it will.

### `blizzard:manual-opencode-export-budget`

**Surface.** `OpenCodeTranscriptSource`'s wall-clock cost — one `opencode export <session-id>` shell-out plus its strict
parse — under fleet-realistic concurrency, against the cursor token-size budget
`blizzard-product:plans/adapters/opencode/spec/transcripts.md`'s Performance boundary sets. No CI tier measures
wall-clock time at all, and every component-tier test of the source binds a scripted export rather than a real
`opencode` binary, so neither the shell-out's latency nor the parser's cost at a large retained conversation is pinned
anywhere else. If the budget this reading records fails, that boundary's own contingency applies: the source moves
behind OpenCode's documented server API instead, without changing the seam.

**Blind spot.** A dev machine's `opencode export` cost is not the hosted runner host's — different disk, different CPU
class, a different concurrent-worker count. What it measures instead is the **ratio** between the export's cost at a
small retained conversation and at a large one, and between one concurrent caller and several, on the same machine — the
shape a budget decision turns on, not an absolute SLA.

**Setup.** A real `opencode` binary (or the emitted mock CLI-surface artifact, once it gains a general `export`,
standing in when a live provider is unavailable), driving one session compacted enough to carry a fleet-realistic
retained-turn count, per `blizzard-product:plans/adapters/opencode/spec/transcripts.md`'s Forward reads section.

**Steps.**

1. Grow one OpenCode session to a retained conversation of realistic size (tool calls, reasoning parts, at least one
   compaction).
2. Time a single `opencode export`, cold, then time the source's `turns_since` cursor-admit pass over the parsed result.
3. Repeat concurrently at the fleet's realistic per-host worker count, timing wall-clock elapsed for the slowest caller.
4. Record the cursor token's serialized byte size at that retained-turn count (the quantity this budget turns on).

**Passes when.** Both readings — the single-call cost and the concurrent-fleet cost — are recorded together against the
same session shape, alongside the cursor token's byte size at that shape, so the server-API contingency is decided from
a measurement rather than a guess.

**Recorded reading** (real `opencode 1.18.31`, one session grown to 122 messages / ~28k tokens over 24 real tool-using
turns in a scratch git repo — a moderate-but-real retained size; time pressure cut the run short of an explicit
compaction, so this is a smaller shape than the fleet's largest long-lived sessions, not the ceiling):

| Reading                                        | Value                         |
| ---------------------------------------------- | ----------------------------- |
| Export size at this retained shape             | 408,050 bytes                 |
| Cold `opencode export`, single caller          | 866.4ms                       |
| `turns_since` cursor-admit pass over the parse | 3.14ms (441 records admitted) |
| Cursor token byte size at this shape           | 75,846 bytes                  |
| 8 concurrent callers, wall-clock for the batch | 1618.3ms                      |
| 8 concurrent callers, slowest caller           | 1485.6ms                      |
| 8 concurrent callers, mean                     | 1269.7ms                      |

**A blocking finding, independent of the budget itself — since fixed.** `opencode export`'s own stdout write truncates
at exactly 65536 bytes (one Linux pipe buffer) when its stdout is a pipe rather than a regular file — reproduced
identically through a raw shell pipe (`opencode export <id> | wc -c`), a bare `subprocess.Popen`/`communicate()`, and
`SubprocessOpenCodeExporter`'s own `capture_output=True` call, all three truncating this same 408,050-byte export at
65,536 bytes and leaving the parser a corrupt document (`json.JSONDecodeError`). Redirecting to a regular file instead
(as this reading's own script does) reads the export whole. Every export above 64KiB — routine at this retained size,
let alone a larger one — was silently unreadable through `SubprocessOpenCodeExporter` as written at the time of this
reading; `SubprocessOpenCodeExporter.export` now redirects `opencode export`'s stdout to a scratch file and reads it
back, closing the gap this reading found.

**What the budget itself says.** Once read correctly (file-redirected), both the single-call and the 8-way concurrent
cost stay well under a second at this shape, and the cursor token — while non-trivial at 75,846 bytes — is a bounded
fraction of the 408KB export it was cut from. Nothing here forces the server-API contingency on cost grounds alone. A
follow-up reading at a genuinely large (compacted, 100k+ token) session would sharpen this — this one is real but
modest, not the ceiling case this budget ultimately needs.

### `blizzard:manual-autocompact-window`

**Surface.** The `--autocompact` flag's effect rather than its presence: a session spawned with a declared
`--autocompact <window>` compacts near that value rather than growing toward the model's own maximum context. No CI tier
can observe effective harness behavior here — [`./gaps.md`](./gaps.md#the-declared-compaction-window) owns that gap.

**Setup.** A real Claude Code CLI (`claude 2.1.234` or newer, the version its tested assumptions were measured against),
a workdir it can run non-interactively in with `-p`, and turns big enough to add tens of thousands of tokens each, so a
handful of turns crosses a low declared window.

**Steps.**

1. Mint a session with a low window near the CLI's own floor, and record the printed session id:

   ```bash
   claude --autocompact 100k -p "<turn 1>" --output-format json
   ```

2. Resume that session repeatedly with the flag reasserted each time, each turn large enough to add tens of thousands of
   tokens, until cumulative context should exceed 100k:

   ```bash
   claude --resume <session-id> --autocompact 100k -p "<turn N>" --output-format json
   ```

3. Read each turn's context size the way the runner already does — the main-chain record's
   `message.usage.input_tokens + cache_read_input_tokens + cache_creation_input_tokens` in
   `~/.claude/projects/<project>/<session-id>.jsonl`, per `ClaudeCodeTranscriptSource.context_tokens` in
   `claude_code_transcript.py`.
4. Repeat the whole run with `--autocompact` omitted, same prompts and same turn count.

**Passes when.** The declared-window run's context size drops sharply back toward a small fraction of 100k within a turn
or two of first crossing it and stays down, while the undeclared run's context size keeps climbing past 100k without
dropping. That contrast is the compaction event itself, because no other mechanism resets a session's context
mid-lineage.

### `blizzard:manual-worker-deny-list`

**Surface.** `WorkerSettings.document`'s `permissions.deny` list reaching the harness and actually closing off the
denied tools — no mock-driven tier can observe whether `claude -p` itself honors a `permissions.deny` entry, only that
the runner built and threaded the file ([`./gaps.md`](./gaps.md#the-worker-deny-list)).

**Setup.** A real Claude Code CLI (`claude 2.1.251` or newer, the version its tested assumptions were measured against)
and a scratch workdir it can run non-interactively in with `-p`.

**Steps.**

1. Write the settings document `WorkerSettings.of().json` renders to a scratch file.
2. Spawn a worker against it,
   `claude -p --settings <file> "<a prompt that would naturally reach a denied tool, e.g.
   'schedule a wakeup for 60 seconds from now'>"`,
   and confirm the denied name does not appear in the session's tool list — `ToolSearch` for it turns up nothing, and a
   direct call is refused.
3. Repeat for `TaskOutput`, `TaskStop`, and a backgrounded `Bash` invocation, confirming each still succeeds under the
   same settings file.

**Passes when.** Every name in `WorkerSettings.DENIED_TOOLS` is unreachable under the emitted settings document, and
`TaskOutput`, `TaskStop`, and backgrounded `Bash` remain reachable under the same document.

### `blizzard:manual-rollback-drill`

**Surface.** The app repo's own `docs/rollback.md`, walked verbatim against a live compose deployment stood up per
`docs/install.md`. `blizzard:unit-test`'s `tests/test_store_migrations.py::test_migrate_up_and_down` already proves
every shipped revision has a working `downgrade()`; the drill wraps the operator-facing procedure around that guarantee,
by hand because no CI tier stands up a real compose deployment. Run it at least once per DISTRIB slice landing, and
re-run it whenever `docs/rollback.md`'s commands change.

**Setup.** A running compose stack (`docker compose up -d`, `packaging/docker/compose.yaml`) on at least two published
or locally-built image tags, so a real previous tag exists to roll back to.

**Steps.** Stop the hub, run `docker compose run --rm hub blizzard-hub migrate --dir … --down <rev>`, then swap to the
previous image tag and bring the hub back up. The `--down` step runs on the still-current, newer image because that
image carries the `downgrade()` steps the older image's tree never heard of.

**Passes when.** The hub then serves at the previous tag's version — `GET /api/health` reports the older `version` — and
`GET /api/ready` reports `ready: true`, proving the store landed at exactly the older revision rather than merely some
earlier one.

### `blizzard:manual-fleet-read-latency`

**Surface.** A named hub read path's wall-clock latency at fleet scale, before and after a change to its read path —
`GET /api/chunks` for the recorded readings below, any other hub read path for a change that touches it instead. No CI
tier measures wall-clock time at all — `blizzard:component-test`'s query-count assertions pin the *shape* of the cost,
not its duration — so a read-path change reports this by hand.

**Blind spot.** A local sqlite store shares the hosted hub's own backend
([`./gaps.md`](./gaps.md#the-query-plan-assertions-never-run-under-postgres) owns which one, and why) but not its
EBS-backed volume's I/O characteristics or its EC2 host's hardware, so an absolute reading here still says nothing about
the hosted hub's own latency. What it measures instead is the **ratio** between two readings of the *same* store, before
and after the code change — a ratio those hardware differences still track proportionally. The hosted reading is
separate: operator inspection against `https://blizzard.grosscode.net` after the change has redeployed there, never a
dev surface pointed at it (`workspace:/context/project/hub-data-modes.md` owns why).

**Setup.** A fleet-scale hub store that is not the live fleet — `workspace:/context/project/hub-data-modes.md`'s mode 2
(a migrated snapshot copy) or mode 3 (seeded synthetic) — or, for a reading taken mid-change before a fresh store
exists, a scratch `tests.support.build_hub` instance seeded to the same chunk count via a throwaway script, as the
recorded reading below used.

**Steps.**

1. Seed or point at a store holding a known chunk count `N`.
2. Warm the connection (one untimed call to the read path), then time several repeated calls and record the mean.
3. Repeat step 2 against the same store, unchanged, on the other side of the code change — the "before" reading taken
   ahead of the change landing (the baseline is unmeasurable once it has), the "after" reading once it has.
4. Optional, for a change that carries a hub revision: on the same store copy, time `blizzard hub migrate`, then
   `migrate --down <prior-rev>`, then `migrate` back up, so the migration's own pause at deploy is sized alongside the
   read-path change it enables.

**Passes when.** Both readings are recorded together, against the same store and the same `N`.

**Recorded reading** (scratch `build_hub` store, N=173, 5 warmed reps, mean wall-clock and total SQL query count for one
`GET /api/chunks`):

| Reading                                                                  | Queries | Mean latency |
| ------------------------------------------------------------------------ | ------- | ------------ |
| Before (`73db0967`)                                                      | 5026    | 339.2ms      |
| After (`load_all_facts`/`load_all_routes` list read, fact-table indexes) | 40      | 10.4ms       |

A ~125x query-count reduction and ~33x latency reduction on the same local sqlite store. The hosted reading is owed
separately, by an operator, once this change has redeployed there.

**Queue-peek reading** (same method, `GET /api/queue`; scratch `build_hub` store, N=173 promoted chunks, 5 warmed reps):

| Reading                                            | Queries | Mean latency |
| -------------------------------------------------- | ------- | ------------ |
| Before (per-chunk `_status` over `list_all`)       | 4677    | 312.7ms      |
| After (`load_all_facts` bulk read in `list_ready`) | 34      | 8.9ms        |

`GET /api/backlog` and the runner's own `GET /api/fleet/queue/peek` share `list_ready`/`list_not_ready`, so the same
reading covers all three. The hosted reading is owed separately, as above.

**Hot-path indexes and spend-fold reading.** Store: an on-disk copy found at this machine's
`~/projects/blizzard-blizzard/backups/hub-20260905T175650Z.db`, of unverified provenance — nothing in `blizzard-infra`
produces a file at that path/name, so treat it as an unofficial, undocumented copy rather than a guaranteed
application-consistent one. `PRAGMA integrity_check` passed, and its `usage_facts`/`transcript_segments` row counts
(3,941 and 21,269) are large enough to exercise the hot-path indexes at realistic scale, which is why it was used here
in place of the operator-provided copy the method's Setup step asks for first — a fresh copy remains owed if this one's
provenance is ever disputed. N=282 chunks, migrated to the pre-change head
(`20260907_1000_event_log_runner_id_nullable`) for Before and to `20260913_1300_hub_store_hot_path_indexes` for After;
one warm rep then 5 timed reps, mean wall-clock and total SQL query count per call:

| Read                                       | Before queries              | Before latency | After queries | After latency |
| ------------------------------------------ | --------------------------- | -------------- | ------------- | ------------- |
| `GET /api/spend` (all-time)                | 1 (3,941 rows materialized) | 21.5ms         | 1             | 0.95ms        |
| `GET /api/spend` (30-day)                  | 1 (partial materialization) | 4.5ms          | 1             | 0.60ms        |
| `load_artifacts` (artifacts by chunk)      | 1                           | 0.53ms         | 1             | 0.28ms        |
| `GraphStore.list_all`                      | 969                         | 132.0ms        | 969           | 98.9ms        |
| `TranscriptEventStore.visible_segment_ids` | 1                           | 8.4ms          | 1             | 2.6ms         |
| `activity_facts_since`                     | 18                          | 10.2ms         | 18            | 9.9ms         |
| `pending_close_intents`                    | 3                           | 0.27ms         | 3             | 0.24ms        |
| `find_live_holder`                         | 30                          | 2.8ms          | 30            | 2.6ms         |

The spend fold is the standout: ~23x latency reduction on the all-time window, with query count unchanged at 1 (the
before reading already issued one query — the win is materializing zero `UsageFact` objects instead of 3,941).
`GraphStore.list_all`'s and `find_live_holder`'s query counts are unchanged by design — these indexes complement, and do
not substitute for, the N+1 fixes tracked separately — their latency drop reflects a cheaper per-query scan, not fewer
queries. The Bulk-read adoption reading below is what touches those two read paths next — see its own table for how each
one's count and latency actually move.

Migration duration on the same store (`blizzard hub migrate` / `--down <prior-rev>` / `migrate` again): up to
`20260913_1300_hub_store_hot_path_indexes` from the prior head, 177.7ms first pass (includes SQLite's index-build cost
against real data — this store's affected-table row counts range from single digits up to `transcript_segments`'s
21,269, with `transcript_events` (9,849), `artifacts` (4,953), `usage_facts` (3,941), `lease_facts` (2,277), and
`transitions` (2,048) the next largest); a subsequent no-op `migrate` at head, 26.7ms; `--down` back to the prior head,
89.9ms; and back up again, 127.4ms. All comfortably sub-second even at this snapshot's scale, so the revision's own
pause at deploy is not a concern at the hosted hub's current size, though a future reader scaling this number should
scale it off `transcript_segments`'s own growth, since it has no retention policy and is this store's largest affected
table by a wide margin.

**Write-side cost.** The read-latency readings above say nothing about insert cost on the two tables this migration
indexes most heavily and that see continuous, append-only writes — `transcript_segments` (4 → 6 indexes) and
`usage_facts` (1 → 3 indexes). On the same before/after store copies (`transcript_segments` 21,269 rows, `usage_facts`
3,941 rows before either bench run), 200 warmup inserts then a timed mean of 2,000 more, one row at a time, each in its
own transaction:

| Insert                    | Before  | After   | Delta |
| ------------------------- | ------- | ------- | ----- |
| `usage_facts` row         | 0.094ms | 0.096ms | +2.8% |
| `transcript_segments` row | 0.141ms | 0.140ms | -1.3% |

Both deltas are within this measurement's own noise band — sqlite's per-row index-maintenance cost for two or three
small non-unique B-tree indexes on tables already carrying one is not observable at this row count. The store's
single-writer WAL/`busy_timeout` posture means the risk this reading answers is contention duration, not per-row cost,
and neither moved measurably.

**Bulk-read adoption reading.** Store: a scratch `build_hub` sqlite store seeded via a throwaway script — N=225 chunks:
200 raw-seeded (`tests.support.seed_chunk`) across 20 minted graphs of 6 real nodes each, every one holding a
`default`-source work ref (`ChunkWorkRefsStore.add_work_refs`) so pointer-liveness fan-out spans every graph; 15
promoted `default`-source ingests and 10 hub-issued work items, both landing on the hub's own auto-minted default graph
— 21 distinct graphs total. No hub-store migration lands between the two commits (`git diff` over
`src/blizzard/hub/store` is empty apart from the internal adapters below), so one seeded `hub.db` copy served both
sides: Before at `096b1c49` (the commit immediately before this bulk-read adoption began), After at `284ece8c` (this
bulk-read adoption's tip; the later repair commit `8b2c3449` touches no store read, so the measured counts still hold);
one warm rep then 5 timed reps, mean wall-clock and total SQL query count per call:

| Read                  | Before queries | Before latency | After queries | After latency |
| --------------------- | -------------- | -------------- | ------------- | ------------- |
| `GET /api/chunks`     | 561            | 161.0ms        | 37            | 21.2ms        |
| `GET /api/graphs`     | 207            | 45.2ms         | 2             | 5.2ms         |
| `GraphStore.list_all` | 206            | 30.9ms         | 106           | 28.2ms        |
| `find_live_holder`    | 30             | 4.8ms          | 30            | 6.6ms         |
| `live_work_refs`      | 6078           | 1431.8ms       | 24            | 12.0ms        |

`GET /api/chunks`, `GET /api/graphs`, and `live_work_refs` see the query-count win this bulk-read adoption was built for
— ~15x, ~104x, and ~253x fewer statements respectively, tracked by roughly matching latency drops (~7.6x, ~8.7x, ~119x).
`GraphStore.list_all`'s own count nearly halves (206 → 106) from batching per-node choices inside `_reify`, but stays
proportional to graph count rather than bounded — `list_all`'s own per-graph reification loop is untouched — so its
latency drop is correspondingly modest (~1.1x). `find_live_holder`'s query count is unchanged (30 → 30) and its latency
is flat within this measurement's noise: this call's win lives in `live_holders`' cross-pointer batching, which a single
pointer with one candidate holder — this reading's own isolated `find_live_holder` call — never exercises; the fan-out
win shows up instead in `live_work_refs` and in `GET /api/chunks`'s own bulk `live_holders` resolution above.

**Derive-once read-sweep reading.** Store: a scratch `build_hub` sqlite store seeded via a throwaway script — N=173
chunks, each ingested and promoted to ready (`tests.support.ingest`). One warm rep then 5 timed reps, mean wall-clock
and total SQL query count per call, both sides on the same seeded store:

| Read               | Before queries (`3c96c0d4`) | Before latency | After queries (`8fdb7577`) | After latency |
| ------------------ | --------------------------- | -------------- | -------------------------- | ------------- |
| `GET /api/queue`   | 56                          | 10.5ms         | 28                         | 7.8ms         |
| `GET /api/backlog` | 56                          | 9.2ms          | 28                         | 6.9ms         |

A 2x query-count reduction on both routes, tracked by a roughly proportional latency drop: dropping the per-request
`load_all_facts` bulk read once `ChunkRecordStore`/`QueueService` take an already-derived `statuses` map instead of
deriving it from facts internally removes that read's own statement cost entirely, not just its per-chunk shape — the
count was already flat in fleet size before this change, per the queue-peek reading above. The hosted reading is owed
separately, by an operator, once this change has redeployed there.

### `blizzard:manual-sweep-pass-cost`

**Surface.** One `EventDerivationReconciler.sweep()` pass's wall time, statement count, and bytes `zlib.decompress`
processes, on a steady-state store — a store already converged, so the pass has nothing left to derive or drop. No CI
tier measures wall-clock time or decompression volume; `blizzard:component-test`'s query-count assertions pin the
*shape* of the cost, not its duration or byte volume.

**Blind spot.** A local sqlite store shares the hosted hub's own backend
([`./gaps.md`](./gaps.md#the-query-plan-assertions-never-run-under-postgres) owns which one, and why) but not its
EBS-backed volume's I/O characteristics or its EC2 host's CPU throttle ceiling, so an absolute reading here says nothing
about the hosted hub's own latency. What it measures instead is the **ratio** between two readings of the *same* store
and corpus shape, before and after the code change. The hosted reading is separate: the sweep's own elapsed-time log
line, read by an operator after the change has redeployed there, never a dev surface pointed at the hosted hub
(`workspace:/context/project/hub-data-modes.md` owns why).

**Setup.** A scratch `tests.support.build_hub` store seeded to the production shape — ≈2,500 visible segments, ≈27,500
records, content sized to ≈175 MB compressed — through a throwaway script, then swept once (untimed) so the store
reaches steady state (every segment carries a current marker) before the timed pass.

**Steps.**

1. Seed the scratch store to the shape above.
2. Sweep once, untimed, so the store converges.
3. Sweep once more, timed: wall-clock elapsed, total SQL statement count (`tests.support.count_queries`'s technique),
   and bytes `zlib.decompress` returns across the pass (a wrapped `zlib.decompress` counts them).
4. Repeat step 3 on the other side of the code change, against the same store shape.

**Passes when.** Both readings are recorded together, against the same corpus shape.

**Recorded reading** (scratch store, 2,500 segments / 27,500 rows, one steady-state pass). The before and after rows are
two independent seedings of the same corpus shape — row and segment counts match, but each seeding draws its own random
row content, so the two compressed-byte totals differ while the shape stays fixed:

| Reading                                                  | Statements | Wall time | Bytes decompressed                        |
| -------------------------------------------------------- | ---------- | --------- | ----------------------------------------- |
| Before (`f75916df`, 175.9 MB compressed)                 | 5003       | 2.81s     | 301.4 MB (27,500 `zlib.decompress` calls) |
| After (`330ae7c4`, 119.6 MB compressed), same reconciler | 1          | 0.002s    | 0                                         |
| After (`330ae7c4`), fresh reconciler (restart shape)     | 4          | 0.07s     | 0                                         |

A steady-state pass before this change re-decodes every visible segment's content in full to compare fingerprints. After
the digest-based candidacy read and the derivation change probe, a repeated pass over an unchanged store costs one
statement — the probe's own aggregate read — and decodes nothing. A fresh reconciler's first pass, which never consults
the in-memory probe (the shape a process restart or crash recovery sees), still runs the real candidacy read: four
statements, no content decoded, well under the 60s interval either way. The hosted reading is owed separately, by an
operator, once this change has redeployed there.
