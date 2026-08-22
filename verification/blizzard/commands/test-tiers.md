# Blizzard test-tier command detail (`bzh:matrix-command-tiers`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->

The pytest tiers' detail — what each command runs, what its named guards assert, and what they cannot see. Read
[`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to every other method's detail.

### blizzard:unit-test

`uv run pytest -m unit` — the unit tier: one class or function in isolation ([tiers](../../blizzard.md#test-tiers)).
Bare `uv run pytest` runs the unit + component default suite. **The packaged-prompt declaration guard**
(`test_packaged_prompts_attach.py`) is the criterion-7 prompt-content check: for every packaged graph
(`src/blizzard/hub/graphs/*/graph.yaml`), every runner node declaring a `produces:` entry must have its inlined prompt
text name the **kind-appropriate** current declaration verb — an `asset` entry names
`blizzard runner artifact create --name <that-exact-name>`, a `git_commit` entry (the build nodes, now that the worker
pushes and declares its own commits) names `blizzard runner artifact commit` — and **no** packaged prompt may name the
deprecated `blizzard runner attach` alias. So a prompt edit that drops or mistypes the declaration instruction, or
reverts to the deprecated `attach` spelling (silently defeating the declare→completion-assembly path in favour of the
git-commit fallback), fails here rather than shipping green, a regression no graph-load or validation test catches
because the prompt is opaque prose to the parser. **The packaged graph-artifact guard** (`test_adw_docket.py`) is that
same species over the same `src/blizzard/hub/graphs/*` surface, aimed at the graph-scope half rather than the
`produces:` one: for the adv-dwf graph it pins that `graph.yaml` declares its `docket` under the top-level `artifacts:`
map — a sibling of `nodes:`/`sessions:`, not a node facet — that the loader `PACKAGED` exercises bakes the referenced
file's text into the doc verbatim rather than leaving the path as the content, and that every prompt restating a slice
of the findings-docket format also names `blizzard runner artifact get docket --scope graph`, so a restatement that
drops the pointer to the full docket fails here. The prompt set is a vocabulary match against raw prompt text rather
than an authored list, which makes a prompt that grows docket vocabulary without the pointer red rather than silently
out of scope, and `test_the_docket_vocabulary_census_is_exactly_ten_files` fixes that matched set by name — the guard on
the guard, since a vocabulary pattern that stopped matching would otherwise let the parametrized case pass vacuously.
What no assertion here reaches is agreement of *content*: editing the docket format obliges re-checking each restatement
against `docket.md` by hand. **The produces-coverage agreement guard** (`test_produces_coverage_agreement.py`) drives
the hub's backstop (`check_produces`) and the runner's nudge check (`_missing_produces`) over **one** scenario matrix
and asserts the two return the same verdict for every scenario — the anti-drift guard on the shared
`wire.completion.produces_coverage` predicate, which calls the internal name-coverage helper `satisfied_produces_names`.
It exists because the bug it closes was a *disagreement*, not a wrong answer on either side alone (the hub rejecting a
git-commit-covered name under `produces_mode=enforce` that the runner already treated as satisfied), and neither side's
own tests can observe one: `test_produces_auth.py` sees only the hub, `test_runner_nudge.py` only the runner. Each
scenario also asserts the *expected* verdict, so two sides that re-forked into the same wrong answer fail too rather
than agreeing with each other. **The git-commit declare-and-verify round trip** (issue #143 Phase 4,
`test_artifacts_storage.py` + the `_verify_and_collect_git_commits` coverage in
`test_runner_loop.py`/`test_runner_gates.py`) pins the worker-declares/runner-verifies split: a fake
`IWorktreeGit.verify` drives ADVANCE's collection (verified → a `GIT_COMMIT` `SubmittedArtifact` carrying the origin the
environment's repo manifest named; unverified → dropped *and* reported as a `command-failed` the worker can act on,
still feeding the Phase-2 nudge), and `GitCommitArtifact`/`ArtifactRow` round-trip losslessly with `forge` carried (and
a legacy null-`forge` row reading back as `""`). The harvest spans **every** bound environment, not just the first —
`test_advance_harvests_git_commits_from_every_bound_environment` pins that a chunk holding two environments delivers
both, the loss a `bindings[0]` read made silent. Reporting an unverified declaration rather than only dropping it is
deliberate: non-coverage alone was the whole backstop until the coverage check could not see the `git_commit` spec, at
which point nothing was left to notice and a chunk reached `done` having delivered nothing. **Four sweep guards** landed
with the 2608 gardening epic, each the mechanical signature of a class review had been catching by hand:
`test_openapi_descriptions.py` (issue #278) scans both committed specs — and the `wire/` models no spec reaches — for
prose an external API consumer cannot resolve (`bzh:comment-locality`'s generated-docstring clause);
`test_no_duplicate_test_bodies.py` (issue #275) fails on two cases sharing a body, module constants folded into the key
so two files reading their own same-named constant are not duplicates (`bzh:case-pins-its-own-name`);
`test_config_keys_reach_a_gating_tier.py` (issue #276) fails on a key of **any** operator-written config dataclass — the
`RunnerConfig`/`HubConfig` roots and the nested blocks a `[[work_source]]` or `[[auth.oauth.provider]]` binds — that no
gating-tier test names (`bzh:gating-tier-pins-production-paths`), a floor rather than a proof, since naming a key is
weaker than pinning its threading, which `test_runner_loop_build.py` does case by case for the keys it covers; and
`test_web_test_targets.py` (issue #275) pins that every Angular `test` target excludes `**/*.shell-sweep.spec.ts`, the
premise `web:structural-gate`'s real-timer scoping rests on — a project missing that exclude would run a real-Chromium
spec inside the merge gate *and* be exempt from the sweep at the same time.

### blizzard:component-test

`uv run pytest -m component` — a domain slice wired with real internal collaborators, doubles only at the seams
([tiers](../../blizzard.md#test-tiers)). **The fleet spend-since read** (epic #57 / #60, `test_fleet_spend_api.py`)
proves `GET /api/spend?since=` sums usage facts by `recorded_at` **across every chunk** — distinct from a chunk's own
derived total (`ChunkUsageTotalView`, covered under the usage-over-the-wire coverage in the `blizzard:service-test` row
below): the fleet-wide sum spans multiple chunks, a fact recorded before `since` is excluded, the cost-absent
lower-bound + `cost_partial` flag, and a malformed `since` 422s. **The checks-gate agreement guard** (issue #114,
`test_checks_gate_agreement.py`) is the same anti-drift shape as the produces-coverage agreement guard, applied to the
`requires_checks` gate: it drives **both** real decision sites — the runner's local gate at worker exit and the hub's
completion backstop — over one scenario matrix and asserts they reach the same accept/reject verdict (and the expected
one), so a future edit re-deriving "is a gated choice red?" inline on either side rather than calling the shared
`wire.completion.checks_gate_violated` predicate fails here.

### blizzard:service-test

`BLIZZARD_SERVICE=1 uv run pytest tests/service/` (`mise run service-test`) — the service tier: a **running** hub or
runner daemon's HTTP API exercised from outside the process (HTTP against a mock counterpart), seams bound to the mock
fleet — distinct from `blizzard:e2e`, which drives the loop in-process one tick at a time (and, in
`test_board_browser_e2e.py` and `test_board_cost_live_e2e.py`, drives the served board through a real browser). The
runner runs against the **mock hub**:

- `unreachable` → buffered, and `drop_ack` → idempotent.
- `stale_envelope` → **tolerated**: the chunk still lands, because the runner fences on its own lease epoch rather than
  on the envelope it was handed (`test_stale_envelope_is_tolerated_and_the_chunk_still_lands`).
- `test_transcript_is_read_back_through_the_runner_http_api` drives a chunk through the real fleet, then reads
  `GET /api/leases` and `GET /api/leases/{lease_id}/transcript` back through the runner's own local HTTP API, asserting
  an `env` turn, `Edit`/`Bash` tool turns with `tool_output` populated, and an `asst` verdict turn, with the `Bash`
  turn's `tool_output` cross-checked against the real commit sha read independently off the bare origin — unsatisfiable
  by a fixture.
- `test_a_closed_leases_transcript_resolves_to_the_hub_through_the_runner_api` walks that same route's three provenance
  homes in one run against a real `build_hosted_app` daemon: `provenance: "local"` while the lease is open, `"archived"`
  once it closes and the mock hub holds its segments — with the shipped `thinking` turn read back intact, the loss a
  narrowing read would show (still `"archived"` after the local file is deleted mid-run, the rotation criterion), and
  `hub_unreachable: true` once the mock-hub subprocess is gone and local cannot answer either — the runner's
  **outbound** fleet-plane read, whose URL and headers no other tier drives against a real counterpart, since the unit
  tier binds a stubbed transport and `test_transcript_segments_service.py` drives the hub-side route with raw httpx.
- `test_graph_scoped_artifact_reads_from_the_runners_own_pin_with_the_hub_unreachable` is the first service-tier
  exercise of a lease-token-authorized worker-lane **read** route, proving a `--scope graph` read resolves from the
  runner's own mint-time mirror with the mock hub down while the same lease's node-scope read still 503s, over a
  reusable worker-credential seam (`_worker_credential`, minting and storing a lease token directly against the store
  rather than intercepting a spawned worker's environment).

The hub runs against the **mock runner** + **mock forge** (a claim followed by a completion **advances the chunk** over
the wire (`test_claim_and_completion_advance_the_chunk_over_the_wire`), stale-epoch rejection, **queue shaping over the
wire** — `test_queue_shaping_group_and_reorder_reflected_in_peek` drives `POST /api/chunks/{id}/group` and
`PUT /api/queue` against the running hub and reads the result back off `GET /api/queue`, so a grouping or reorder that
the domain applies but the wire does not surface fails here; its component-tier sibling `tests/test_queue_shaping.py`
asserts the same shaping without the wire — route-token authz under `route_token_mode=enforce`, and **produces-artifact
authz** under `produces_mode=enforce`: a completion for a node declaring `produces:` is fenced out over the wire, chunk
unadvanced, unless it carries an explicit `attached=True` artifact for every declared name, while a fallback-only
completion still applies under the default `warn`, driven by the mock runner's `/_drive/complete` `artifacts` field —
the produces analogue of the route-token levers; a **git-commit-covered** name is likewise **accepted** under `enforce`
(`test_git_commit_covered_produces_name_is_accepted_under_enforce_over_the_wire`), the accept end of the hub/runner
coverage agreement its unit-tier sibling `test_produces_coverage_agreement.py` pins — a name covered by a pushed commit
carries `attached=False`, and the hub once fenced exactly that shape out over the wire even though the runner's nudge
already treated it as satisfied). **Hub SSE live fan-out** (issue #107) is proven at this tier and only at this tier: a
subscriber connected to `GET /api/events/stream` *before* the act receives `queue-changed` the instant a fresh
cross-graph migration re-queues a chunk, and receives **exactly one** across that migration and its duplicate-delivery
replay (the mock runner's `replay` lever submits the byte-identical completion twice, so both land in one live window —
the single count assertion fails at 0 if the publish is dropped and at 2 if the replay guard is). The component tier
asserts publication by reading the broker's *replay tail*, which shows an event was **recorded**, not **delivered**; the
publish → subscriber-queue → wire leg a live board depends on is real only here, via the `sse_tap` helper in
`tests/service/support.py`. **Runner SSE live fan-out** has the same shape at the same tier, over the runner's own
stream and its own event vocabulary: `test_runner_stream_delivers_live_and_replays_from_last_event_id` proves a
subscriber connected before a lease-mutating call receives the frame live and resumes from `Last-Event-ID` across a
reconnect; `test_runner_stream_resumes_live_after_a_restart_reset_the_broker_ids` covers the reconnect shape that one
cannot — a **second** daemon instance behind the same port, its own broker minting ids from zero, resuming a cursor the
first instance minted, which a single-instance reconnect never presents (the clamp it exercises is pinned in isolation
at the unit tier by `tests/test_foundation_events.py`; this is its route wiring, with the cursor arriving as a real
`Last-Event-ID` header); `test_runner_stream_replays_a_restarted_brokers_buffered_tail_past_a_stale_cursor` covers the
half *that* one misses — the fresh broker already holds buffered events when the reconnect arrives, so the stale cursor
reaches the **replay** read rather than only the live-dedup watermark, and an unresolved one silently empties the tail
instead of merely dropping live frames; and `test_runner_sigterm_returns_promptly_with_a_client_parked_on_the_stream`
proves a signal-driven shutdown still returns `server.run()` with a client held open — all in
`tests/service/test_runner_service.py`, the runner counterpart of the hub proof above, not a re-derivation of it.
`blizzard:e2e`'s `test_runner_panel_live_e2e` scenario ([registry](../e2e-scenarios.md)) carries the same fan-out one
tier further: a *real* `blizzard-runner host` subprocess, its own reconciliation loop actually minting and closing
leases, observed through a real browser on the served panel — the one place the publish → stream → `local-panel`'s
live-updates registry → re-read chain runs end to end with nothing stubbed on either side. The **operational event
feed** (issue #125, `test_event_log_service.py`) rides the same fan-out: the mock runner's `/_drive/report-event` verb
drives one `event.recorded` fact, a subscriber connected before the act receives `event-logged` **exactly once**, and
the folded event reads back off the live `GET /api/events` (mock-runner→live-hub); a direct fixed-seq replay pins the
fold's per-runner-seq idempotency. The real runner's own emission of these facts (and its store-and-forward buffering
through a hub outage) is the runner's job, proven at the unit/component tiers where it lands. **Usage over the wire**
(epic #57 / #59, `test_usage_service.py`) is proven in both directions: runner→mock-hub, a real runner's
`usage.recorded` facts ride the store-and-forward buffer, survive a hub outage, and flush exactly once;
mock-runner→live-hub, usage facts pushed through the hub's real `POST /api/fleet/events` become per-node-step usage +
the derived chunk total (`ChunkUsageView` / `ChunkUsageTotalView`, `cost_partial` when a row's cost is absent) read back
off the live `GET /api/chunks/{id}` and `GET /api/chunks`, idempotent on a replayed seq. **OAuth login dance** (epic #89
/ issue #92, `test_auth_login_service.py`) is proven at this tier and only at this tier: a running hub under
`auth.mode = "oauth"` whose `authorize` 302s to the `blizzard-mock` **stub IdP** (`tool:mock-fleet`, `blizzard-mock-idp`
— both provider shapes at one origin) and whose `callback` exchanges the stub's code over the real wire, ending in a
resolving `bz_session` cookie and a working `GET /api/me`, for **both** the `oidc` (issuer discovery + RS256 `id_token`
verification) and `github` (code flow + `/user` + verified primary email) conformers; a two-provider hub lists both from
`GET /api/auth/providers`; `POST /api/auth/logout` deletes the session row so `/api/me` 401s; and the stub's
`refuse_callback` lever surfaces as the `login_failed` response over the real wire. The component tier
(`test_auth_login_api.py`) drives the same routes against an in-repo fake provider (bad `state` + `login_failed` fact,
the linking rule, the no-token-cookie shape); this method is the only one exercising a **real HTTP
authorize→token→userinfo exchange**. **Runner SSO federation — the JWT/JWKS wire leg** (epic #89 / issue #95,
`test_idp_federation_service.py`) is the browserless service-tier companion to e2e's `test_runner_federation_e2e.py`: a
real hub (`auth.mode = "oauth"`, its session established through the same `blizzard-mock` stub IdP dance) delivers a
hub-signed, audience-bound JWT via `response_mode=form_post` to a real `blizzard runner host`'s
`POST /api/auth/callback` — the whole chain (provider dance → hub session → IdP `authorize` → runner callback) real over
localhost — ending in a runner-domain `bz_runner_session` cookie and an unlocked human-lane route; a second scenario
rotates the hub signing key (`POST /api/auth/rotate-signing-key`) and drives a fresh bounce whose token is minted under
the just-rotated `kid`, proving the **live** runner's JWKS cache refetches it with no restart. It proves the wire leg
the browser scenario also exercises without the browser's cost; the runner's own three-lane gating split (human-lane 401
vs worker-hook/socket ungated) is pinned at the unit/component tiers (`test_runner_route_gating.py`,
`test_runner_federation.py`). **CLI login — the `blizzard hub login` PKCE code exchange** (epic #89 / issue #96,
`test_cli_login_service.py`) is proven at this tier and only at this tier: a running hub (`auth.mode = "oauth"`, its
session established through the same `blizzard-mock` stub IdP dance) serves the `client=cli` authorize branch (mandatory
S256 PKCE) to a browserless scripted "browser" — the same `httpx.Client` carrying the hub session cookie,
`follow_redirects=False` — which captures the delivered single-use code from **both** the ephemeral
`127.0.0.1:<port>/callback` loopback-redirect form (a 302 query-string *code*, never a token) and the out-of-band
paste-code page, then redeems it with its PKCE verifier at `POST /api/auth/cli/token` for a hub-minted **session token**
(never a runner-style JWT); a bare bearer client with no cookie jar — the CLI's own shape, exactly what
`blizzard hub status` sends — then authenticates `GET /api/me` off that token alone, and `POST /api/auth/logout`
presenting the same bearer (the `blizzard hub logout` path) **revokes it server-side** so a byte-identical retry 401s,
proving AC 4's "the hub session stops resolving" over the real wire rather than a mere local file delete. The CLI never
contacts the stub IdP — only the hub's own authorize/token/logout routes. The exchange's rejection matrix (a
wrong/missing PKCE verifier, an unregistered redirect form, a single-use replayed code, an expired code) is pinned at
the component tier (`test_cli_login_api.py`) and the loopback listener + paste-code mechanics at the unit tier
(`test_cli_login_mechanics.py`, `test_hub_cli_login.py`); this method is the only one exercising the whole
code→token→bearer→revoke chain against a **running** hub. Local-only like `blizzard:e2e` — needs the sibling provisioned
`blizzard-mock` worktree (its venv ships `blizzard-mock-hub` / `-runner` / `-forge` / `-fixture` / `-idp` /
`mock-claude-code`) and a local winter source, and skips cleanly without `BLIZZARD_SERVICE=1`. **In CI** both the `pr`
and `push` workflows run it as a real gate over a multi-repo checkout — `blizzard` + `blizzard-mock` + the public
`blizzard-workspace` (the winter source) laid out as siblings, `BLIZZARD_MOCK_WINTER_SOURCE` pointed at the last.

### blizzard:crash-sweep

`BLIZZARD_CRASH_SWEEP=1 uv run pytest -m crash_sweep tests/crash/` (`mise run crash-sweep`) — the FULL kill-9 sweep
([../../architecture/crash-correctness.md](../../../architecture/crash-correctness.md)): a pytest runner enumerating the
crash-point registry (`blizzard.foundation.crash.discover_crash_points`) and, for each point, running the hub + runner
as real subprocesses over the mock fleet, arming the point so its owning daemon `SIGKILL`s itself there, then asserting
the invariant checker (`blizzard dev check-invariants` / `blizzard.foundation.store.invariants`) is green over both
stores and the chunk still lands **exactly once** after an unarmed restart (startup = REAP). Whole-process cases round
it out: `tests/crash/test_kill9_sweep.py`'s own unparametrized test functions — a sweep case that signals a whole daemon
process or process group rather than arming a single registry crash point, a graceful SIGTERM qualifying as readily as a
`kill -9`. They cover an external kill of the runner mid-flight (both after the worker's commit is durably declared and
before it, the pre-declaration window arming `LAND_STEP`'s empty-delivery refusal), a graceful and an involuntary daemon
restart re-attaching an in-flight session in place, and a `killpg` of the hub process group mid-delivery between repo
pushes (the authored default and fast-forward land graphs each swept). No count is kept here — the predicate is the
membership test, not a number that drifts as cases are added. The registry's boundary families are `resume.`,
`abandon.`, `pause.`, `hubnode.` (the generic hub command node's per-step and pending-poll windows —
[../../architecture/crash-correctness.md](../../../architecture/crash-correctness.md) `bzh:crash-point-registry`), and
`migrate.` (the cross-graph migration window, #90 — armed on the **hub**, swept by `test_kill9_at_migrate_crash_point`:
a `kill -9` right after the atomic re-pin loses only the `MIGRATED` response, and the runner's replay re-derives it via
the `accepted_migration` probe, `hub:one-migration-per-node-epoch` + `hub:migration-pin-consistent` green; its
**hub-landing** sibling `test_kill9_at_migrate_crash_point_landing_on_a_hub_node` (#111) drives a migration onto a
hub-executed node, where the route is **retained** not released — the replay returns `HUB_NODE_TAKEN` so the holding
runner keeps its envs and its ADVANCE poll drives the landed hub node to `done` rather than the chunk wedging at
`delivering`, with `hub:migration-route-released` exempting the intended retention; the per-chunk intended migration,
#124, is swept on the same `migrate.` point by `test_kill9_at_migrate_crash_point_for_an_intended_migration` — its
component- and unit-tier coverage is `tests/test_intended_migration_apply.py`, `tests/test_chunk_edit_api.py`, and
`tests/test_hub_cli_chunk.py`, since e2e's `test_migration_e2e.py` exercises only the #90 authored-choice migration),
and `attach.` (the worker artifact-attach durability window — armed on the **runner**, swept by
`test_kill9_at_attach_crash_point`: the runner's local `POST /api/leases/{id}/attachments` records the attachment in one
committed txn, then `kill -9`s in the after-record-before-response window, and the durable row — with full provenance —
is still readable via `attachments_for_lease` against the same store after an unarmed restart, the fact completion
assembly / the recovering ADVANCE tick re-derives (criterion 3). Unlike the loop-driven families this is an out-of-band
HTTP write no loop step drives, so its scenario stands up a real runner daemon alone — no hub, no forge — seeding a
parked lease + its capability token, since the durability property is loop-independent; the invariant checker runs over
the runner store only), and `nudge.` (the produces-unmet nudge-once window — armed on the **runner**, swept by
`test_kill9_at_nudge_crash_point` over both members `nudge.after-fired-fact.before-resume` and
`nudge.after-resume.before-reassemble`: a `produces:` name with neither a git commit nor an attachment gets exactly one
resumed nudge in `_advance_exited_worker`, gated on a durable `(lease, epoch)` fact recorded **before** the resume it
guards so at-most-once is structural — a `kill -9` after the fact is durable can never re-nudge on recovery because the
next ADVANCE pass consults the fact alone, never the resume's outcome; unlike `attach.` this window fires inside the
runner's own ADVANCE step, so its scenario stands up a real hub too, and `runner:nudge-at-most-once` is green after each
recovery with the chunk landing exactly once — criterion 5), and `checks.` (the checks-at-exit windows, #114 — armed on
the **runner**, swept by `test_kill9_at_checks_crash_point` over both members `checks.after-results.before-marker` and
`checks.after-marker.before-judge`: the runner runs a node's `checks:` at worker exit and records each result row then a
`checks_ran` marker, so a `kill -9` in the fired-before-marker window leaves the marker unset and recovery re-runs the
checks (latest-wins overwrite), while after the marker recovery reads the recorded results back and judges —
`runner:checks-recorded-when-marked` green after each recovery, the chunk landing exactly once; its bounded-CI
representative is the recovery-critical `checks.after-results.before-marker`), and `preempt.` (the operator-restart
teardown window, #370 — armed on the **runner**, swept by `test_kill9_at_preempt_crash_point`: an operator restarts a
running chunk and the runner `kill -9`s between killing the displaced worker and recording the `preempted` closure, so
recovery must re-derive the same preempt off the hub's still-standing fence — the lease closes `preempted`, never
`reaped` or `failed`, which would spend the retry budget the move exists to protect, and the chunk lands exactly once)
alongside the ungrouped generic `build → deliver` sweep points, most of which fire in the runner loop — `claim.` (the
route-claim boundary between persisting the route + its capability-token fact and the runner reading the plaintext token
back) is the first of those ungrouped points armed on the **hub** process instead, recovered generically by the runner's
own interrupted-claim adoption rather than a dedicated scenario. Local-only like `blizzard:e2e` — needs the sibling
`blizzard-mock` worktree and a winter source; skipped without `BLIZZARD_CRASH_SWEEP=1`. **In CI** both the `pr` and
`push` workflows run the **bounded CI profile** —
`BLIZZARD_CRASH_SWEEP=1 BLIZZARD_CRASH_SWEEP_CI=1 uv run pytest -m crash_sweep tests/crash/`
(`mise run crash-sweep-ci`): one representative crash point per boundary family plus the whole-process cases and the
recovery-critical windows, ~75s on a GitHub runner, so the sweep is a real gate at bounded runtime. The subset is
intersected with the live registry and asserts each named point still exists (`bzh:crash-point-registry`), so a rename
fails loudly. The FULL sweep stays this method's documented local command (`mise run crash-sweep`) and runs in the tag
`release` workflow.
