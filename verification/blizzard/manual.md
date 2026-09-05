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
against a stubbed transport, and this probe is what ties that stub back to what the provider actually returns. A
runner with no `[[subscription]]` declared has exactly one slug to name, the legacy `anthropic` slug (Claude Code); one
with declarations names any of its own slugs instead, and none of them is guaranteed to be `anthropic`.

**Setup.** The runner machine's own real OAuth credentials for the slug under test (`~/.claude/.credentials.json` for
`anthropic`) and a working `blizzard runner` binary.

**Steps.** Run `blizzard runner external-usage probe <slug>` (e.g. `probe anthropic`), a read-only diagnostic
subcommand, then separately read that provider's own usage view for the same account (Claude Code's own `/usage`
command, for `anthropic`), and compare the two.

**Passes when.** The probe's parsed utilization percentages and reset times match what the provider's own usage view
reports for the same account, within the natural few-second sampling skew.

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

**Surface.** `GET /api/chunks` wall-clock latency at fleet scale, before and after a change to its read path
(blizzard#421). No CI tier measures wall-clock time at all — `blizzard:component-test`'s query-count assertions pin the
*shape* of the cost, not its duration — so a read-path change reports this by hand.

**Blind spot.** A local sqlite store does not reproduce the hosted postgres deployment's per-query network round trip,
so an absolute reading here says nothing about the hosted hub's own latency. What it measures instead is the **ratio**
between two readings of the *same* store, before and after the code change — a ratio a sqlite round trip's smaller,
proportionally-similar per-query cost still tracks. The hosted reading is separate: operator inspection against
`https://blizzard.grosscode.net` after the change has redeployed there, never a dev surface pointed at it
(`workspace:/context/project/hub-data-modes.md` owns why).

**Setup.** A fleet-scale hub store that is not the live fleet — `workspace:/context/project/hub-data-modes.md`'s mode 2
(a migrated snapshot copy) or mode 3 (seeded synthetic) — or, for a reading taken mid-change before a fresh store
exists, a scratch `tests.support.build_hub` instance seeded to the same chunk count via a throwaway script, as
`blizzard:manual-fleet-read-latency`'s own blizzard#421 baseline used.

**Steps.**

1. Seed or point at a store holding a known chunk count `N`.
2. Warm the connection (one untimed `GET /api/chunks`), then time several repeated calls and record the mean.
3. Repeat step 2 against the same store, unchanged, on the other side of the code change — the "before" reading taken
   ahead of the change landing (the baseline is unmeasurable once it has), the "after" reading once it has.

**Passes when.** Both readings are recorded together, against the same store and the same `N`.

**blizzard#421 reading** (scratch `build_hub` store, N=173, 5 warmed reps, mean wall-clock and total SQL query count for
one `GET /api/chunks`):

| Reading                                                                  | Queries | Mean latency |
| ------------------------------------------------------------------------ | ------- | ------------ |
| Before (`73db0967`)                                                      | 5026    | 339.2ms      |
| After (`load_all_facts`/`load_all_routes` list read, fact-table indexes) | 40      | 10.4ms       |

A ~125x query-count reduction and ~33x latency reduction on the same local sqlite store. The hosted postgres reading is
owed separately, by an operator, once this change has redeployed there.

**Queue-peek reading** (same method, `GET /api/queue`; scratch `build_hub` store, N=173 promoted chunks, 5 warmed reps):

| Reading                                            | Queries | Mean latency |
| -------------------------------------------------- | ------- | ------------ |
| Before (per-chunk `_status` over `list_all`)       | 4677    | 312.7ms      |
| After (`load_all_facts` bulk read in `list_ready`) | 34      | 8.9ms        |

`GET /api/backlog` and the runner's own `GET /api/fleet/queue/peek` share `list_ready`/`list_not_ready`, so the same
reading covers all three. The hosted reading is owed separately, as above.
