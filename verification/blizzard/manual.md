# Performing a `blizzard:` manual method (`bzh:matrix-manual-detail`)

<!-- One flat `###` section per method id — the shape this file's sibling spokes share. -->
<!-- rumdl-disable MD001 -->

Full detail for the `blizzard:` manual methods named in [`../blizzard.md`](../blizzard.md)'s Manual testing table, one
section per row, in that table's order. The `web:` methods live in [`./manual-web.md`](./manual-web.md) and the
`blizzard-mock:` methods in [`./manual-mock.md`](./manual-mock.md).

### `blizzard:manual-hub`

**Surface.** A running hub driven by hand from outside the process — its HTTP API under `/api/`, and the operator CLI
(`blizzard hub …`), itself a client of that API — for behavior a change makes observable on a live daemon: a route's
response, a verb's effect on the fleet view, a transition's derived status. A narrower `blizzard:manual-*` row whose
claim is the changed behavior wins over this one, and auth-gated behavior is `blizzard:manual-standing-idp`'s, because
the hub this method stands up serves everything unauthenticated.

**Setup.** `tool:service-up` stands the stack up, run from the workspace root; the sourced band is what sets
`$BZ_HUB_URL` and points the shell at the env's own hub:

```bash
winter provision <env>
winter service up <env> --wait
source <(winter env <env>)
curl -fs "$BZ_HUB_URL/api/health"
```

Run the CLI as `uv run blizzard hub <verb>` from `<env>/blizzard`, so the client under exercise is the worktree's own
rather than an installed one; it reads `$BZ_HUB_URL`, so no `--hub-url` is needed. Drive only the env's own hub — never
the hosted one, whose standing rule `workspace:/context/project/hub-data-modes.md` owns. Put the store in the state the
change needs with `tool:mock-data`, or through the real ingest path when ingest itself is under exercise;
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) owns that choice and both routes' preconditions.

**Steps.**

1. State the changed behavior as an observable before driving anything: this request or verb, against this state, yields
   this response or output.
2. Seed or drive the hub into that state.
3. Drive the behavior with `curl` against `$BZ_HUB_URL/api/…` or with the CLI verb. The app repo's
   `openapi/hub.openapi.json` carries every route and its shapes, and `blizzard hub --help` the verb tree.
4. Confirm it through a second surface, so the observation is the hub's state rather than one surface's own echo: an API
   write read back through `blizzard hub status` or `blizzard hub chunk show`, a CLI write through the route that serves
   it, a read compared against the seed or the drive that put the state there.
5. Keep the commands run and their output with the change under verification.

When the behavior under exercise rides the acceptance loop — ingest, acquire, commit, deliver, landed — walk the loop
against the live stack rather than seeding past it:

1. `uv run blizzard-mock-fixture reset --env <env>`, from `<env>/blizzard-mock`.
2. Drop the harness fence marker in the fixture's `workspace/`.
3. File a forge issue.
4. `POST /api/chunks`, so the env's runner ticks the chunk to `done`.

`blizzard:e2e` runs this same loop as a tier, and the `mise run e2e` source is the exact in-process sequence to read
when a by-hand step is unclear. Walking it by hand exercises a change on the loop while watching it; it never stands in
for the tier.

**Passes when.** The stated observable holds on the running hub, confirmed through a second surface — and, for a loop
walk, the chunk lands in the bare origin and the hub's facts derive `done`, with no tokens and no network.

### `blizzard:manual-runner`

**Surface.** A running runner driven by hand over its local HTTP API — the machine-local view and controls a change
makes observable on a live daemon: a route's response, a lease's or environment's reported state, the pause brake's
effect on the next tick. The rendered panel over that API is `web:manual-panel`'s
([`./manual-web.md`](./manual-web.md#webmanual-panel)).

**Setup.** `tool:service-up`, as for `blizzard:manual-hub` above; the same sourced band sets `$BZ_RUNNER_PORT`, the port
the runner answers on:

```bash
curl -fs "http://127.0.0.1:$BZ_RUNNER_PORT/api/health"
```

The env's runner spawns the fenced mock harness (`tool:mock-fleet`), never a real one. Seed its store with
`tool:mock-data` only after the daemon's first start, and leave a seeded runner's local pause engaged;
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) owns why on both counts.

Restart the env's runner — to pick up an edited `blizzard-runner.toml`, say — with
`winter service restart <env>/runner`, and stop a runner you launched by hand by its own pid. Never kill by a pattern
such as `pkill -f "blizzard runner host"`: it matches every runner on the machine, including a live fleet runner that
may be hosting your own session, and a runner exits cleanly on that signal, so its supervisor does not bring it back.

**Steps.**

1. State the changed behavior as an observable: this request, against this runner state, yields this response.
2. Seed or drive the runner into that state — a seed for a read, a chunk walked through the env's hub
   (`blizzard:manual-hub`'s loop walk) for behavior only a live lease shows.
3. Drive the behavior with `curl` against `http://127.0.0.1:$BZ_RUNNER_PORT/api/…`. The app repo's
   `openapi/runner.openapi.json` carries every route and its shapes.
4. Account for the tick: the daemon reconciles its store on every tick — 30 seconds by default, `tick end` in the
   runner's log — so re-read after one, and treat a row that changes across it as the daemon's doing rather than the
   request's.
5. Confirm it through a second surface — `uv run blizzard runner status --runner-url "http://127.0.0.1:$BZ_RUNNER_PORT"`
   from `<env>/blizzard`, `GET /api/dashboard`, or, for a read, the seed or the drive that put the state there — and
   keep the commands run and their output with the change under verification.

The CLI verbs whose help is labeled **Worker:** resolve their lease from a spawned worker's environment, so they are
exercised by a worker the runner spawns, not typed by hand.

**Passes when.** The stated observable holds on the running runner and still holds after the next tick, confirmed
through a second surface.

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

### `blizzard:manual-credential-renewal`

**Surface.** No CI tier can prove `codex app-server`'s `account/read` call actually renews a real OpenAI login: the tier
rules forbid service and e2e tests from touching the network or a real credential file, and `blizzard:service-test`'s
own concurrent-writer proof runs against `mock-codex app-server`, never the real binary. This method is what ties that
proof back to the real vendor CLI. The renewal seam is not accepted until this method has been run and passed at least
once, on a login whose rotation the operator accepts — forking a copy of a real login into a scratch `CODEX_HOME`
invalidates that login's own refresh token, so this method is run against a login the operator is prepared to have
rotated, never a throwaway copy.

**Setup.** A runner with an `openai`-provider `[[subscription]]` declared, whose credential file (`~/.codex/auth.json`
by default, or the declaration's own `credentials_path`) is inside the renewer's lead window — at or near its own
access-token `exp` — and a working `codex` binary the runner's environment can reach. Record the credential file's own
`tokens.refresh_token` and access-token `exp` before starting.

**Steps.** Let one of the runner's own sampling cadences fire naturally (`ExternalUsageSample` calls `renew_if_due()`
before every due sample), or drive it directly via a normal tick with the subscription's cadence already elapsed.
Optionally, run `codex` by hand at the same time (e.g. `codex login status`), so the live proof also covers the
concurrent-writer path the mock only simulates.

**Passes when.** The credential file's `tokens.refresh_token` and access-token `exp` have both changed from what was
recorded in Setup, `codex login status` (or an equivalent vendor-CLI check) still reports the login as active afterward,
and the runner's very next sample for that slug succeeds rather than reporting `credential_lapsed`.

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

**Surface.** The live CLI/provider compatibility surface for an OpenCode version inside the runner's admitted range
(currently `>=1.18.25,<2.0`) with ChatGPT `5.6 Luna` (`openai/gpt-5.6-luna`) at `max`, covering the diagnostic's:

- `fresh_turn`, `resume`, `process_control`, `judgement`, `root_hook`, `permission`, and `model_variant`
- `usage_cost`, `takeover`, `transcript_read`, `transcript_cursor`, `child_sessions`, and `configuration_isolation`

**Procedure.** Follow the public operator procedure at `blizzard/docs/deployment/opencode-compatibility.md` for
prerequisites, invocation, live opt-in, credential and evidence handling, failure conditions, and interpretation. That
page's own "Admitting a candidate version" section owns the separate procedure for admitting a candidate version — the
gates a candidate owes before this diagnostic applies to it, and when a new corpus or a widened range is owed.

**Retained evidence.** Retain the diagnostic output and the sanitized `report.json` and `runtime.json` files from the
evidence directory.

**Passes when.** The command exits zero, the output reports an OpenCode version inside the runner's admitted range
(currently `>=1.18.25,<2.0`) and ends with `compatibility: supported` or `compatibility: degraded`, and `report.json`
records `complete: true` and `admissible: true`. This diagnostic result is not production adapter availability or a
harness-selection decision.

### `blizzard:manual-opencode-operator-bundle`

**Surface.** The production OpenCode binding's effective operator bundle on a real admitted CLI, including native loader
precedence, plugin discovery and events that a mock CLI cannot establish. The compatibility diagnostic uses its own
isolated scratch configuration and does not exercise this binding.

**Setup.** Use a disposable home (`HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`) and scratch git project, all under the
lease scratch directory. Give both user and project scopes distinct benign config settings and plugins in their native
OpenCode locations (`opencode.json` and `plugins/`); place an operator `opencode/opencode.json`, a plugin in
`opencode/plugins/`, and a relative `{file:…}` companion in a test bundle. Use a real `opencode` in the runner's
admitted range and a working provider login confined to this test home. Build the effective snapshot through the
production bundle publisher and launch through `OpenCodeAdapter`, not the compatibility probe. Record the CLI version,
source paths and effective directory; redact credentials and substitution contents from retained output.

From `<env>/blizzard`, run `uv run python scripts/probe_opencode_operator_bundle.py --login <auth.json>` with
`BLIZZARD_TMPDIR` set to the lease scratch directory. The source login must have at least an hour remaining on its
access token. The script copies it into the disposable `XDG_DATA_HOME` (never symlinks it), stages all three config
scopes, launches through the production adapter and prints a sanitized result with per-invocation tool names and
plugin/heartbeat counts. It removes the disposable home on exit. Its heartbeat recorder intercepts the runner plugin's
real CLI command; the env-local runner API check below proves that command's endpoint separately.

**Steps.**

1. Inspect `opencode debug config` from the worker cwd with the adapter's exact `OPENCODE_CONFIG`,
   `OPENCODE_CONFIG_CONTENT`, and `OPENCODE_CONFIG_DIR` environment. Compare its resolved settings and plugin list to
   the source scopes; inspect the published JSON and companion paths. Relative `{file:…}` substitutions in
   `OPENCODE_CONFIG_CONTENT` use absolute snapshot paths, since OpenCode resolves them against the worker cwd. Each
   independent setting survives and the runner's `permission.question` remains `deny`.
2. Launch a fresh real worker turn that uses a permitted tool and attempts both an operator-denied tool and `question`.
   Read the tool/permission events and plugin instrumentation, including the runner heartbeat endpoint: denied calls are
   refused without waiting, each plugin loads once, and exactly one heartbeat arrives for each completed tool call.
3. Resume the same session, send a nudge, run a judgement and invoke a child `task` session. For each invocation compare
   the adapter's effective environment, resolved config, plugin execution count and heartbeat count to the tool events.
4. Introduce a collision with `question` and separately with the runner plugin in the operator bundle; attempt startup
   and confirm the error names the native source file and the previously published snapshot remains readable. Repeat
   duplicate plugin identity tests across bundle, project and user JSON entries and native plugin directories. A
   duplicate must either resolve to one explicitly selected source or fail before the worker launches with both paths.

For the separate `blizzard:manual-runner` check on a provisioned feature env, keep the standing runner's paused fixtures
untouched. From `<env>/blizzard`, source `winter env <env>` and run
`uv run python scripts/probe_opencode_bundle_runner.py --chunk-id <disposable-ready-chunk-id>`. The script starts a
disposable bundle-backed runner against that env's hub, waits for an active mock OpenCode lease, records a heartbeat,
confirms its timestamp after a later tick via the runner API and CLI, then stops the runner and detaches the test chunk
back to ready. Its local hub gateway admits only the selected chunk at queue peek and claim, regardless of other ready
chunks' positions. The caller must supply a disposable chunk that is ready before the run.

**Retained evidence.** Keep sanitized resolved-config output, the effective file's path and hash, CLI/tool events,
plugin instrumentation and per-invocation heartbeat counts alongside the change under verification.

**Passes when.** All settings and companion files load with the documented precedence, denied calls are refused, runner
and operator plugins execute once each, exactly one heartbeat is emitted per tool call through fresh, resume, nudge,
judgement and child sessions, and collisions fail with actionable paths without replacing a valid snapshot.

### `blizzard:manual-opencode-compatibility-rehearsal`

**Surface.** That `blizzard/docs/deployment/opencode-compatibility.md`'s stated offline rehearsal path — emit a
CLI-surface artifact and point `--binary` at it to exercise the whole diagnostic flow without provider quota — is itself
followable exactly as written, by an operator with no prior knowledge of the mock fleet's internals. This is distinct
from `blizzard:manual-opencode-compatibility`, which proves the admitted-version live contract against a real provider;
this method proves a page.

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

**Export capture boundary.** `opencode export` can truncate stdout at 65536 bytes (one Linux pipe buffer) when stdout is
a pipe; the 408,050-byte reading above requires a regular file for capture. `SubprocessOpenCodeExporter.export`
redirects stdout to a scratch file and reads it back so exports at this retained size remain parseable. The reading's
script uses the same file-redirection boundary.

**What the budget itself says.** With file-redirection capture, the single-call cost is under a second and the 8-way
concurrent batch takes about 1.6 seconds at this shape. The cursor token — while non-trivial at 75,846 bytes — is a
bounded fraction of the 408KB export it was cut from. Nothing here forces the server-API contingency on cost grounds
alone. A follow-up reading at a genuinely large (compacted, 100k+ token) session would sharpen this — this one is real
but modest, not the ceiling case this budget ultimately needs.

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
   `claude_code/transcript.py`.
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
4. Repeat steps 2 and 3 under each Claude Code `--permission-mode` that `[harness] autonomy` maps to — `manual`, `auto`,
   and `bypassPermissions` — adding `--permission-prompts none` under `manual`. What a call that needs approval does is
   owned by [`blizzard:manual-headless-permission-refusal`](#blizzardmanual-headless-permission-refusal).

**Passes when.** Every name in `WorkerSettings.DENIED_TOOLS` is unreachable under the emitted settings document in every
mapped permission mode, and `TaskOutput`, `TaskStop`, and backgrounded `Bash` remain reachable under the same document.

### `blizzard:manual-headless-permission-refusal`

**Surface.** What a live headless CLI does with a permission request under each `[harness] autonomy` value. OpenCode
auto-rejects an unanswered ask and the rejection ends the agent loop, so `normal` composes every ask to `deny`; no
mock-driven tier observes either CLI's handling ([`./gaps.md`](./gaps.md#headless-permission-handling)).

**Setup.** Real `opencode` in the runner's admitted range and a real `claude` with a login, from `<env>/blizzard` with
`BLIZZARD_TMPDIR` set. OpenCode runs against a deterministic loopback OpenAI-compatible stub, so its tool call is
guaranteed and it needs no credential; Claude Code runs a cheap model.

**Steps.** Run `uv run python scripts/probe_headless_permission_refusal.py` (`--skip-claude` omits Claude Code). Per
autonomy value it launches through the production adapters under a disposable home and scratch project. OpenCode cells
ask from the operator bundle, user config, project config, project `agent.build.permission`, and a built-in default (a
`.env` read). The Claude Code cell has an operator `permissions.ask` rule on a Bash command.

**Passes when.** The script exits 0. In `normal`, every OpenCode cell ends with the call refused as a tool result, a
final reply, and no `auto-rejecting` on stderr. In `auto` and `dangerous`, every OpenCode cell resolves the request
without a prompt. Every Claude Code cell refuses the `ask` rule with a `permission_denials` entry and completes the
turn. No cell times out.

### `blizzard:manual-claude-code-bundle`

**Surface.** An operator's `claude-code/` bundle published with the runner's required wiring composed in, then loaded by
a real `claude`: whether the operator's tools, MCP servers, plugins, agents, and hooks reach the worker beside the
runner's heartbeat, session-end hook, and denials. The mock tiers prove only argv threading and that the mock executes
the composed hooks ([`./gaps.md`](./gaps.md#the-claude-code-bundle)); which ambient settings the composed `--settings`
file cannot override is only measurable against the real CLI.

**Setup.** A real Claude Code CLI inside the admitted range, a scratch workdir, and a runtime directory whose
`[harness] config_dir` names a bundle holding all four entry points — a `settings.json` with an unrelated key, an
operator `permissions.deny` entry, and an operator `PostToolUse` hook that writes a marker file; an `mcp.json` with a
stdio server; an `agents.json`; and a `plugins/` folder with one plugin. Start the runner once so the snapshot is
published; `blizzard runner harness status` prints the effective settings path and the flags to reuse. Never touch the
operator's real `~/.claude`: point `CLAUDE_CONFIG_DIR` at a scratch user scope.

**Steps.**

Part (a), the CLI direct against the published snapshot:

1. Run `claude -p --output-format stream-json --verbose --include-hook-events` with the flags `harness status` prints,
   once per permission mode `[harness] autonomy` maps to. Read the `system/init` event: `tools` omits every
   runner-denied and operator-denied tool, `mcp_servers` lists the operator's server, `plugins` lists the plugin, and
   `agents` lists the agent. The operator's marker hook and the runner's heartbeat hook both execute.
2. Put an unrelated key and `disableAllHooks: true` in a scratch user-scope `settings.json`, and again in a project
   `.claude/settings.json`; repeat step 1. Hooks still fire. Record each key a user or project scope can set that the
   composed `--settings` cannot override — each is a row the ambient-conflict rule table owes.
3. Take a `--resume` turn and a judgement-shaped turn with the same flags; both keep the operator's and the runner's
   wiring.
4. Have a `Task` subagent attempt an operator-denied tool and list its MCP tools; it is refused the tool and sees the
   server.
5. Where `/etc/claude-code` is writable, place each managed rule's key in `managed-settings.json` and observe the
   effect; otherwise record managed scope as unwalked.

Part (b), through a real runner, with `blizzard:manual-live-node`'s setup and `[harness] config_dir` set:

6. Run a node. The lease's heartbeat advances, the node's judgement runs, and the transcript shows the operator-denied
   tool refused.
7. Point the runner at a managed-settings fixture holding a conflicting key through its injected search path, and read
   `GET /api/harness-health`: Claude Code is unavailable with `config_conflict`.

**Passes when.** Every step's observation holds in every mapped permission mode, and step 2's measurement is recorded
with the outcome that fixes the ambient rule table's user and project rows.

**Hazards.** As `blizzard:manual-live-node`'s: never the systemd runners' stores, and never the hosted hub.

### `blizzard:manual-claude-code-harness-telemetry`

**Surface.** Which source Claude Code honors when an `OTEL_*` destination is named in both its process env and a
settings document's `env`, and whether the telemetry it exports reaches a runner's own receivers under the scopes and
trace parenting the runner admits ([`./gaps.md`](./gaps.md#claude-code-telemetry-precedence) owns why no hermetic tier
stands in).

**Setup.** A real Claude Code CLI inside the admitted range, from `<env>/blizzard` with `BLIZZARD_TMPDIR` set. Part (a)
needs no login and spends no tokens. Part (b) uses `blizzard:manual-live-node`'s setup with
`[tracing] harness_telemetry` on and a local OTLP sink as the runner's export destination. Managed-settings precedence
is not probed: it stays the static reading (managed `env` wins per signal family) unless walked by hand.

**Steps.**

Part (a), the precedence probe:

1. Run `uv run python scripts/probe_claude_code_telemetry_precedence.py`. It points the model endpoint at a closed
   loopback port under a disposable `CLAUDE_CONFIG_DIR`, home, and project, and observes two local sinks. It runs the
   `baseline`, `flag-same-name`, `user-same-name`, `generic-in-settings`, `beta-endpoint`, `switch-off`, and
   `enable-only` cells and writes one sanitized protobuf export body per signal to
   `blizzard/tests/fixtures/claude_code_telemetry/` (`--fixtures-dir` redirects them when the walk is not meant to
   refresh the fixtures). `--fallback-model-turn` runs one cheapest-model turn only when the baseline emits nothing
   without a reply, and the output reports that it did.
2. Record the `claude` version and, per cell and signal, which sink received it: `settings` means the settings
   document's `env` beat the process env (outcome A), `process` means the process env won (outcome B).
3. Record the scope names.
4. Record whether spans parent on the `TRACEPARENT` span.
5. Record which signals the `beta-endpoint` cell's endpoint took from the documented exporters, in any encoding.
6. Record which signals reached a sink in the `switch-off` cell, which names destinations but sets neither Claude Code
   telemetry switch.
7. Record which signals reached a sink in `enable-only`, which sets only `CLAUDE_CODE_ENABLE_TELEMETRY`.

Part (b), through a real runner, with `blizzard:manual-live-node`'s setup. Give the worker a scratch user scope:
`CLAUDE_CONFIG_DIR` and `CLAUDE_CODE_OAUTH_TOKEN`, holding the current access token, which cannot refresh, in
`[worker] env_passthrough`. Mapping every tier to `haiku` in `[models.aliases]` and ingesting an already-satisfied item
into `default-delivery` ends the chunk after the one `triage` node.

8. Run one node with `harness_telemetry` on and no operator destination in the worker settings. The sink holds Claude
   Code metrics, logs, and spans under `blizzard-claude-code`, each stamped with the node's chunk, lease, and runner;
   the spans sit under the step root; a span from a `blizzard` command the worker ran parents on the step root, since
   the CLI reads only `BLIZZARD_TRACEPARENT`; `blizzard runner status` shows all three signals captured.
9. For the handoff to programs that read `TRACEPARENT`, run one `haiku` `claude -p` turn under the same switches, with a
   known `TRACEPARENT` and a traces sink, that runs `printenv TRACEPARENT` through `Bash`: the printed span id is one of
   Claude Code's spans.
10. Put one signal's exporter in the `--settings` document's `env`, and rerun. That signal reaches the operator's
    destination and `runner status` shows it as operator-configured.

**Passes when.** The probe exits 0 and its reading is recorded with the `claude` version: outcome A or B per source, the
scope names, and the parenting. Part (b)'s observations hold. Walk it again whenever the admitted range in
`blizzard/src/blizzard/runner/harness/claude_code/health.py` or the installed `claude`'s minor version moves: the
precedence is undocumented behavior.

**Hazards.** As `blizzard:manual-live-node`'s: never the systemd runners' stores, and never the hosted hub. An
operator's own `~/.claude/settings.json` `env` beats the runner's process env, so it could redirect a signal or reach a
hosted backend, and a copied credentials file could rotate the shared refresh token. Placing a `managed-settings.json`
under `/etc/claude-code` by hand is machine-wide: it also reaches the instance runners' workers on this host, so do it
only on a host with none, and remove it afterward.

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

### `blizzard:manual-trace-backends`

**Surface.** One hub's fleet traces leaving through one operator collector, running the documented config
(`packaging/otel-collector/collector.yaml` in `blizzard`) unmodified, to **two real backends at once** — a self-hosted
store and a hosted service — and a reader finding a chunk's slowest step in each. `blizzard:e2e`'s `fleet traces`
subtests prove the exported shape through a file exporter and `blizzard:collector-config` proves the config parses;
neither delivers a span to a backend or reads one back.

**Blind spot.** The self-hosted store is Jaeger all-in-one, not Tempo, which the config's comments name; both speak OTLP
gRPC, so the exporter block is the same. A backend's own query and retention behavior beyond the one chunk read here is
not measured.

**Setup.**

- Jaeger all-in-one in docker: `docker run -d -p 4317:4317 -p 16686:16686 jaegertracing/jaeger:latest` (OTLP gRPC on
  4317, UI and query API on 16686).
- Honeycomb as the hosted service. The key is the operator's own: ask for it through `blizzard runner ask`, naming only
  where it lives, never its value, and pass it to the collector as `HOSTED_TRACES_API_KEY` from that location.
- The documented collector config, the file itself unchanged, with `TRACE_STORE_ENDPOINT=127.0.0.1:4317`,
  `TRACE_STORE_INSECURE=true`, `HOSTED_TRACES_ENDPOINT=https://api.honeycomb.io` and the key. Where the machine already
  holds the config's default ports (`4318` for the receiver, `8888` for the collector's own metrics), move them with
  command-line `--set` overrides — `--set receivers.otlp.protocols.http.endpoint=127.0.0.1:<port>` and
  `--set service.telemetry.metrics.level=none` — rather than editing the file.
- A hub traced through it: an env-local hub from a feature env, never the hosted hub, started with
  `OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:<port>` and `[tracing] sweep_seconds = 1` / `settle_seconds = 0` so
  steps export as they close. `blizzard`'s e2e harness (`tests/e2e/test_acceptance_loop.py`'s `_hub`) is such a hub.

**Steps.**

1. Start Jaeger, then the collector, and confirm the collector is listening before the hub starts — the export cursor
   opens at enable time, and a failed first export backs off for minutes.
2. Drive one chunk through a bounce on the env-local hub — the delivery-conflict scenario's chunk (`merge_conflict`
   lever armed) goes build → deliver → bounce → build.
3. In Jaeger, find the chunk's traces by `blizzard.chunk.id` and read each step root's duration; the longest is the
   slowest step.
4. In Honeycomb, query the same chunk by `blizzard.chunk.id` over root spans (`parent_span_id` does not exist) and read
   `duration_ms` per step; again the longest.
5. Change nothing in `blizzard` between the two reads.

**Passes when.** Both backends show the same step roots for the chunk, each backend yields the slowest step by name and
duration, and no `blizzard` file changed between the two reads. Record each backend's slowest step with the query or
view used.

**Recorded reading** (one env-local hub driving the delivery-conflict scenario's chunk `ch_01M3WNWM92HSYBSWENAXD5WG85`
through a bounce, one collector on the unmodified documented config with both exporters live and no export errors in its
log; the receiver and metrics ports moved by `--set`, as Setup says):

| Backend              | Query or view                                                                      | Slowest step                                              |
| -------------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------- |
| Jaeger (self-hosted) | `/api/v3/traces`, service `blizzard-hub`, root spans of the chunk                  | `step build` (epoch 1), 6.408 s                           |
| Honeycomb (hosted)   | dataset `blizzard-hub`, root spans, `blizzard.chunk.id` = the chunk, `duration_ms` | longest 6.408 s, read by the operator in the Honeycomb UI |

Jaeger's other roots were `step deliver` (epoch 2) 142.7 ms, `step build` (epoch 3) 4827.5 ms and `step deliver`
(epoch 4) 125.9 ms. The Honeycomb reading is the operator's: the key at hand is an ingest key, which Honeycomb's Query
API refuses, so the readback was by eye and the step's name was not recorded there. No `blizzard` file changed between
the two reads.

### `blizzard:manual-egress-warehouse`

**Surface.** A kept fact-egress directory copied to object storage with the docs' own `rclone` recipe, loaded into a
warehouse from each manifest's file list, and read in a BI tool: cost by node by day and the slowest station of the
week, equal to the DuckDB recipes over the same directory. `blizzard:e2e`'s night module proves the files and the DuckDB
recipes; no tier proves a warehouse and a BI tool can read them from the dictionary alone.

**Blind spot.** The format read is Parquet, from the night module's second export; NDJSON is not loaded. MinIO,
ClickHouse and Grafana stand in for the operator's own bucket, warehouse and BI tool, and a loader's behavior beyond
these two reads is not measured.

**Setup.** All local docker on one user-defined network, no credentials of the operator's own.

- The directory: `BLIZZARD_E2E=1 uv run pytest tests/e2e/test_egress_night_e2e.py --basetemp <dir>`, then the
  `export-parquet` directory under it.
- MinIO (`cgr.dev/chainguard/minio`, as `minio/minio` is no longer pulled from Docker Hub) with a throwaway root key,
  and `rclone/rclone` for the copy.
- `clickhouse/clickhouse-server` and `grafana/grafana` with `GF_INSTALL_PLUGINS=grafana-clickhouse-datasource`, the
  official ClickHouse data source.

**Steps.**

1. Run the night module with `--basetemp`.
2. `rclone copy` the Parquet directory into a MinIO bucket as `docs/deployment/egress.md`
   `### Object storage with rclone` gives it, the manifests last.
3. In ClickHouse, create one `MergeTree` table per dataset from the `s3` table function over the file list the manifests
   name, then the dictionary's newest-copy view over each as `<dataset>_newest`.
4. In Grafana, add the ClickHouse data source and build two table panels over `steps_newest` from the dictionary alone:
   cost by node by day, and the station with the highest mean `duration_ms` over the last seven days.
5. Run the docs' two DuckDB recipes over the same directory and record each answer beside Grafana's. Change nothing in
   `blizzard` between the reads.

**Passes when.** Grafana's two panels give the same stations, days, billed and estimated cost and slowest station as
DuckDB over the same directory, and no `blizzard` file changed between the reads. Record both answers.

**Recorded reading** (one night run, kept with `--basetemp`; the Parquet export held a live pass and a backfill pass, so
each row existed twice and the newest-copy view collapsed 36 `steps` rows to 18 and 52 `invocations` rows to 26; the
queries ran through Grafana's data source query API, the panels' own path):

| Station (`default-delivery`) | Day        | Billed USD, Grafana | Billed USD, DuckDB | Estimated USD, Grafana | Estimated USD, DuckDB |
| ---------------------------- | ---------- | ------------------- | ------------------ | ---------------------- | --------------------- |
| `approve-gate`               | 2026-10-03 | null                | null               | null                   | null                  |
| `assemble`                   | 2026-10-03 | 0.253276            | 0.253276           | 0.125                  | 0.125                 |
| `build`                      | 2026-10-03 | 0.023736            | 0.023736           | null                   | null                  |
| `clarify`                    | 2026-10-03 | 0.005085            | 0.005085           | null                   | null                  |
| `deliver`                    | 2026-10-03 | null                | null               | null                   | null                  |
| `review`                     | 2026-10-03 | 0.009768            | 0.009768           | null                   | null                  |

The slowest station was `default-delivery` / `assemble`, mean 18494 ms, in Grafana and in DuckDB. The loader needed no
step `### A warehouse loader` leaves unstated.

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

### `blizzard:manual-branch-protection`

**Surface.** Each protected repo's live GitHub `master` branch protection, against the required-check set its own
verification doc names (`blizzard`: [`./commands/packaging.md`](./commands/packaging.md); `blizzard-mock`:
[`./commands/mock.md`](./commands/mock.md); `blizzard-context`: [`../../verifiability.md`](../../verifiability.md)). An
operator applies the protection each of those docs carries, then reads it back through this method once after landing,
and again on any later change to a repo's required-check set.

**Setup.** `gh auth status`, authenticated as an account with admin on each protected repo. Have the URL of a known
fleet-delivered PR for each repo being checked.

**Steps.**

1. Per protected repo, read back live protection: `gh api repos/<owner>/<repo>/branches/master/protection`.
2. Compare its `required_status_checks.checks[].context` list against the repo's documented required set, and its
   `enforce_admins.enabled` / `required_pull_request_reviews` against the documented `false` / unset.
3. From the known PR URL, confirm its branch matches the delivered chunk and its state is merged with
   `gh pr view <fleet-pr-number> --repo <owner>/<repo> --json state,headRefName,mergedAt,mergeCommit`.
4. Fetch in that repo's worktree with `git -C <repo-worktree> fetch origin`, then
   `git -C <repo-worktree> log -1 --format=%P <mergeCommit.oid>` reads two parents.

**Passes when.** Every protected repo's live protection matches its documented required set exactly, and the selected
fleet PR's own merge commit has two parents.

`blizzard-infra` is out of scope for this method — its own docs record why it cannot be protected on the current GitHub
plan.

### `blizzard:manual-live-routine`

**Surface.** A garden routine run end to end by a real-harness runner against an env-local hub — the path no mock
harness walks: the survey's own tool calls, a command outlasting one of them, and the lease staying live across it.
`blizzard:manual-runner` spawns only the fenced mock; this row is for a change whose claim is what a real worker does
with a routine's charge.

**Setup.** `tool:service-up` as for `blizzard:manual-hub`, then stop the env's own mock runner
(`winter service down <env>/runner`) so it cannot claim the run. The preconditions the stack does not give you:

- The hub store is at head: run `blizzard hub migrate --dir "$BZ_HUB_RUNTIME"` and restart the hub, or re-`init` a fresh
  runtime. A store left by an earlier tenant can carry a stamped revision without its columns, and delivery then fails
  with a 500 that no artifact can fix.
- The routine's graph is minted: `blizzard hub graph sync`, then `hub routine create` for the routine, plus one
  throwaway routine per extra scope slug (a scope is minted by the routine that names it) so `routine scope add` can
  link it.
- The hub has no forge configured — start it without `BZ_FORGE_URL`. With the env's mock forge, delivery resolves each
  cited commit against fixture origins that hold no real commit, and rejects every delta.
- The verification runner has its own runtime directory (`blizzard runner init`, then set `runner_id`, `workspace_envs`
  to the dedicated env, `max_agents = 1`, `[worker] path_prepend` to the mise shims, and `[opencode] enabled = false`),
  a `hub_url` at the env-local hub, `BZ_HARNESS_BINARY` set to the real harness, and `base_branch` set to the branch
  under test. It starts from a clean environment, never the env band, so no mock fence reaches the real harness. The
  runner resets the dedicated env to `base_branch` on every acquire; a branch already checked out in another env's
  worktree cannot be that base, so name a remote-tracking ref that only the verification needs
  (`git update-ref refs/remotes/origin/<name> <sha>`). A repo that lacks the ref falls back to its own main, so the ref
  is set only in the repo under test.
- The delta run needs a baseline that both carries the command under test and leaves changed functions with mutants. An
  older commit alone cannot: it may predate the command, or the range may change only functions the method cannot see.
  Build the base as an older commit with the command's own commit cherry-picked onto it, and confirm with a direct run
  of the command that the range yields a small, sortable survivor set before starting the routine.

**Steps.**

1. Start a run with `blizzard hub routine run --mode full` with the runner's `base_branch` at an older commit, and, once
   it ends, `--mode delta` with `base_branch` moved to the branch under test, so the delta has a real diff to narrow to.
2. While a run is live, read the verification runner's lease activity on its API on a cadence shorter than the staleness
   threshold; note the largest gap between heartbeats.
3. Read the terminal state, findings, proposals, and measurement back through the operator CLI (`routine sweeps`, the
   findings and proposals verbs), never the store.
4. Capture the run's transcript: the longest single tool call, and the exact arguments the survey passed to any command
   the axis routes to.
5. Record which revision of the agent context the worker read.

**Passes when.** The routine run reaches its terminal state with its findings, proposals, and measurement delivered,
read back through the operator CLI; the verification runner's lease never read `stale`; and the transcript is kept with
the verification report.

**Hazards.** Never the systemd runners' stores, and never the hosted hub —
`workspace:/context/project/hub-data-modes.md` owns which hub is safe.

### `blizzard:manual-live-node`

**Surface.** One node of a packaged graph run by a real-harness runner against an env-local hub — what a real worker
does with the node's prompt, the asset it publishes, and the edge the chunk then takes. `blizzard:manual-runner` spawns
only the fenced mock and `blizzard:manual-live-routine` walks a garden routine; this row is for a change whose claim is
a graph node's live behavior, entered by `hub chunk restart --to-graph <graph> --node <node>` so the steps before it
need not be re-walked.

**Setup.** As `blizzard:manual-live-routine`'s Setup — the store at head, the graph minted with
`blizzard hub graph sync`, no forge configured, and the verification runner's own runtime directory with the real
harness and a `base_branch` — without its delta-baseline precondition. Add:

- A hub work item for a small change, whose changed functions sit in one scope of the surface the node acts on, and a
  disposable branch pushed for it.
- A real `build` turn to declare the commit, so the node reads a declared tip; a chunk restarted onto the node with no
  declared commit tests only that path.

**Steps.**

1. Ingest the work item and let the chunk reach the node's predecessor with a real declared commit.
2. Restart it onto the node: `blizzard hub chunk restart --to-graph <graph> --node <node>`.
3. While the node runs, read the runner's lease activity on its API on a cadence shorter than the staleness threshold;
   note the largest gap between heartbeats.
4. Read the node's published asset back through the operator CLI, never the store, and check it against what the node's
   prompt owes.
5. Let the chunk take its edge, read the next node's own output for what it did with the asset, then stop the chunk.
6. Record the node's session overhead — its wall time less the wrapped command's own — and the revision of the agent
   context the worker read.

**Passes when.** The asset is present and well-formed, the chunk took the edge the node's verdict names, the downstream
node consumed the asset as its addendum directs, and the runner's lease never read `stale`.

**Hazards.** As `blizzard:manual-live-routine`'s: never the systemd runners' stores, and never the hosted hub.
