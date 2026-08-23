# Blizzard test-tier command detail (`bzh:matrix-command-tiers`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` headings, every test-filename code span, and each `mise run` name with its paired command span are machine-checked registrations — keep them verbatim, inside their own sections. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:unit-test

`uv run pytest -m unit` — one class or function in isolation. Bare `uv run pytest` runs the unit-plus-component default
suite; the tier roster is [`../tier-rules.md`](../tier-rules.md#test-tiers).

The git-commit declare-and-verify round trip (`test_artifacts_storage.py`, plus the `_verify_and_collect_git_commits`
coverage in `test_runner_loop.py`/`test_runner_gates.py`) pins the worker-declares/runner-verifies split: a fake
`IWorktreeGit.verify` drives ADVANCE's collection — a verified declaration becomes a `GIT_COMMIT` `SubmittedArtifact`
carrying its manifest-named origin, and an unverified one is dropped and reported as a `command-failed` the worker can
act on — and `GitCommitArtifact`/`ArtifactRow` round-trip losslessly with `forge` carried. Reporting rather than only
dropping the unverified declaration is deliberate: a silent drop lets a chunk reach `done` having delivered nothing.

The produces-coverage agreement guard (`test_produces_coverage_agreement.py`) drives the hub's backstop
(`check_produces`) and the runner's nudge check (`_missing_produces`) over one scenario matrix and asserts both return
the same, and the expected, verdict — the anti-drift guard on the shared `wire.completion.produces_coverage` predicate.
Neither side's own tests can observe a disagreement — `test_produces_auth.py` sees only the hub, and the component
tier's `test_runner_nudge.py` only the runner — and the expected-verdict assertions also catch identical re-forks.

Four sweep guards are each the mechanical signature of a defect class otherwise caught only by hand in review:

- `test_config_keys_reach_a_gating_tier.py` fails on any key of an operator-written config dataclass — the
  `RunnerConfig`/`HubConfig` roots and the nested blocks a `[[work_source]]` or `[[auth.oauth.provider]]` binds — that
  no gating-tier test names (`bzh:gating-tier-pins-production-paths`). That is a floor; `test_runner_loop_build.py` pins
  the actual threading of the keys it covers.
- `test_no_duplicate_test_bodies.py` fails on two cases sharing a body, module constants folded into the key so two
  files reading their own same-named constant are not duplicates (`bzh:case-pins-its-own-name`).
- `test_openapi_descriptions.py` scans both committed specs, and the `wire/` models no spec reaches, for prose an
  external API consumer cannot resolve (`bzh:comment-locality`'s generated-docstring clause).
- `test_web_test_targets.py` pins that every Angular `test` target excludes `**/*.shell-sweep.spec.ts` — the premise
  `web:structural-gate`'s real-timer scoping rests on; a missing exclude would run a real-Chromium spec inside the merge
  gate while exempting it from the sweep.

The packaged-prompt declaration guard (`test_packaged_prompts_attach.py`): for every packaged graph
(`src/blizzard/hub/graphs/*/graph.yaml`), every runner node declaring `produces:` must have its inlined prompt name the
kind-appropriate declaration verb — `blizzard runner artifact create --name <that-exact-name>` for an `asset` entry,
`blizzard runner artifact commit` for a `git_commit` entry — and no packaged prompt may name the deprecated
`blizzard runner attach` alias. The guard exists because a prompt is opaque prose to the parser: a dropped or mistyped
declaration instruction, or a revert to `attach`, fails no graph-load or validation test.

The packaged graph-artifact guard (`test_adw_docket.py`) covers the same `src/blizzard/hub/graphs/*` surface on the
graph-scope half: the adv-dwf `graph.yaml` declares its `docket` under the top-level `artifacts:` map, not as a node
facet; the `PACKAGED` loader bakes the referenced file's text into the doc verbatim, and every prompt restating a slice
of the findings-docket format also names `blizzard runner artifact get docket --scope graph`. The docket guard's prompt
set is a vocabulary match against raw prompt text, not an authored list — a prompt growing docket vocabulary without the
pointer goes red — and `test_the_docket_vocabulary_census_is_exactly_ten_files` pins the matched set by name, the guard
on the guard against a pattern that silently stops matching. No docket assertion reaches content agreement: editing the
docket format obliges re-checking each restatement against `docket.md` by hand.

### blizzard:component-test

`uv run pytest -m component` — a domain slice wired with real internal collaborators, doubles only at the seams.

The checks-gate agreement guard (`test_checks_gate_agreement.py`) applies the same anti-drift shape as the
produces-coverage guard to the `requires_checks` gate: both real decision sites — the runner's local gate at worker exit
and the hub's completion backstop — must reach the same, expected, accept/reject verdict over one scenario matrix, so
re-deriving "is a gated choice red?" inline instead of calling the shared `wire.completion.checks_gate_violated`
predicate fails.

The fleet spend-since read (`test_fleet_spend_api.py`) proves `GET /api/spend?since=` sums usage facts by `recorded_at`
across every chunk — distinct from a chunk's own derived total: facts recorded before `since` are excluded, cost-absent
rows give a lower bound with `cost_partial`, and a malformed `since` 422s.

### blizzard:service-test

`BLIZZARD_SERVICE=1 uv run pytest tests/service/` (`mise run service-test`) — a running hub or runner daemon's HTTP API
exercised from outside the process against a mock counterpart, seams bound to the mock fleet. It needs the sibling
provisioned `blizzard-mock` worktree (its venv ships the mock-fleet console scripts, the stub IdP, and
`mock-claude-code`) plus a winter source, and skips cleanly without `BLIZZARD_SERVICE=1`. It is distinct from
`blizzard:e2e`, which drives the loop in-process one tick at a time and, in the e2e tier's `test_board_browser_e2e.py`
and `test_board_cost_live_e2e.py`, drives the served board through a real browser.

Hub against mock runner plus mock forge: a claim then a completion advances the chunk over the wire
(`test_claim_and_completion_advance_the_chunk_over_the_wire`), stale-epoch rejection, and route-token authz under
`route_token_mode=enforce`. Runner against mock hub: `unreachable` buffers, `drop_ack` proves idempotency, and a
`stale_envelope` is tolerated — the chunk still lands because the runner fences on its own lease epoch, not the envelope
it was handed (`test_stale_envelope_is_tolerated_and_the_chunk_still_lands`).

Produces-artifact authz under `produces_mode=enforce`: a completion for a node declaring `produces:` is fenced out over
the wire, chunk unadvanced, unless every declared name carries an explicit `attached=True` artifact, while a
fallback-only completion still applies under the default `warn`.
`test_git_commit_covered_produces_name_is_accepted_under_enforce_over_the_wire` pins the accept end of the coverage
agreement (its unit-tier sibling is `test_produces_coverage_agreement.py`): a name covered by a pushed commit carries
`attached=False` and is accepted. `test_advance_harvests_git_commits_from_every_bound_environment` pins that the harvest
spans every bound environment — two environments deliver both, the loss a `bindings[0]` read made silent.

Hub SSE live fan-out is proven at this tier only: a subscriber connected to `GET /api/events/stream` before the act
receives `queue-changed` the instant a cross-graph migration re-queues a chunk, and exactly one frame across the
migration and its duplicate-delivery replay (the mock runner's `replay` lever) — failing at 0 if the publish drops, at 2
if the replay guard does. The component tier can only assert an event was recorded, off the broker's replay tail; the
publish-to-subscriber-queue-to-wire leg a live board depends on is real only here, via the `sse_tap` helper in
`tests/service/support.py`.

The operational event feed (`test_event_log_service.py`) rides the same fan-out: the mock runner's
`/_drive/report-event` drives one `event.recorded` fact, a pre-connected subscriber receives `event-logged` exactly
once, the folded event reads back off the live `GET /api/events`, and a fixed-seq replay pins idempotency; the real
runner's own emission and buffering is proven at the unit/component tiers.

Runner SSE live fan-out has the same shape over the runner's own stream and vocabulary, all in
`tests/service/test_runner_service.py`:

- `test_runner_stream_delivers_live_and_replays_from_last_event_id` proves live delivery to a pre-connected subscriber
  and resume from `Last-Event-ID` across a reconnect.
- `test_runner_stream_resumes_live_after_a_restart_reset_the_broker_ids` covers what a single-instance reconnect never
  presents — a second daemon instance behind the same port, its broker minting ids from zero, resuming a cursor the
  first minted; the clamp itself is pinned at the unit tier by `tests/test_foundation_events.py`.
- `test_runner_stream_replays_a_restarted_brokers_buffered_tail_past_a_stale_cursor` covers the half that one misses —
  the fresh broker already holds buffered events at reconnect, so the stale cursor reaches the replay read; unresolved,
  it silently empties the tail rather than merely dropping live frames.
- `test_runner_sigterm_returns_promptly_with_a_client_parked_on_the_stream` proves a signal-driven shutdown still
  returns `server.run()` with a client held open.

`blizzard:e2e`'s `test_runner_panel_live_e2e` scenario
([`../e2e-scenarios/runner-panel.md`](../e2e-scenarios/runner-panel.md)) carries fan-out one tier further: a real
`blizzard-runner host` subprocess observed through a real browser on the served panel — the one end-to-end fan-out chain
with nothing stubbed.

Usage over the wire (`test_usage_service.py`) runs both directions: runner-to-mock-hub, a real runner's `usage.recorded`
facts ride the store-and-forward buffer, survive a hub outage, and flush exactly once; mock-runner-to-live-hub, usage
pushed through the real `POST /api/fleet/events` becomes per-node-step usage plus the derived chunk total
(`cost_partial` on absent cost) read off the live `GET /api/chunks/{id}` and `GET /api/chunks`, idempotent on a replayed
seq.

Queue shaping over the wire: `test_queue_shaping_group_and_reorder_reflected_in_peek` drives
`POST /api/chunks/{id}/group` and `PUT /api/queue` against the running hub and reads the result off `GET /api/queue`,
failing a shaping the domain applies but the wire does not surface; its component-tier sibling
`tests/test_queue_shaping.py` asserts the same shaping without the wire.

`test_transcript_is_read_back_through_the_runner_http_api` drives a chunk through the real fleet, then reads
`GET /api/leases` and `GET /api/leases/{lease_id}/transcript` back through the runner's own local HTTP API, asserting
real turn kinds with `tool_output` populated, the `Bash` turn's output cross-checked against the real commit sha off the
bare origin — unsatisfiable by a fixture. `test_a_closed_leases_transcript_resolves_to_the_hub_through_the_runner_api`
walks the route's three provenance homes against a real `build_hosted_app` daemon: `"local"` while the lease is open;
`"archived"` once the mock hub holds its segments — still `"archived"` after the local file is deleted mid-run; and
`hub_unreachable: true` once the mock-hub subprocess is gone. It is the only real-counterpart drive of the runner's
outbound fleet-plane read — the unit tier binds a stubbed transport, and `test_transcript_segments_service.py` drives
the hub-side route with raw httpx.

`test_graph_scoped_artifact_reads_from_the_runners_own_pin_with_the_hub_unreachable` is the first service-tier exercise
of a lease-token-authorized worker-lane read route: a `--scope graph` read resolves from the runner's own mint-time
mirror with the mock hub down while the same lease's node-scope read still 503s (the `_worker_credential` seam).

The OAuth login dance (`test_auth_login_service.py`) is proven at this tier only: a running hub under
`auth.mode = "oauth"` whose `authorize` 302s to the `blizzard-mock` stub IdP (`tool:mock-fleet`, `blizzard-mock-idp` —
both provider shapes at one origin) and whose `callback` exchanges the stub's code over the real wire, ending in a
resolving `bz_session` cookie and a working `GET /api/me`, for both the `oidc` and `github` conformers. Also there: a
two-provider hub lists both from `GET /api/auth/providers`; `POST /api/auth/logout` deletes the session row so `/api/me`
401s; and the stub's `refuse_callback` lever surfaces as `login_failed` over the wire. The component tier
(`test_auth_login_api.py`) drives the same routes against an in-repo fake provider — bad `state`, the `login_failed`
fact, the linking rule, the no-token-cookie shape; only the service method exercises a real HTTP
authorize/token/userinfo exchange.

CLI login (`test_cli_login_service.py`) proves the `blizzard hub login` PKCE code exchange at this tier only: a running
hub serves the `client=cli` authorize branch (mandatory S256 PKCE) to a browserless scripted "browser" that captures the
single-use code from both the loopback-redirect form (a 302 query-string code, never a token) and the paste-code page,
then redeems it with its verifier at `POST /api/auth/cli/token` for a hub-minted session token, never a runner-style
JWT. A bare bearer client — the CLI's own shape — authenticates `GET /api/me` off that token alone, and
`POST /api/auth/logout` with the same bearer revokes it server-side so a byte-identical retry 401s; the CLI never
contacts the stub IdP, only the hub's own routes. The exchange's rejection matrix — wrong or missing verifier,
unregistered redirect form, replayed code, expired code — is pinned at the component tier (`test_cli_login_api.py`); the
loopback listener and paste-code mechanics sit at the unit tier (`test_cli_login_mechanics.py`,
`test_hub_cli_login.py`).

Runner SSO federation's JWT/JWKS wire leg (`test_idp_federation_service.py`) is the browserless companion to e2e's
`test_runner_federation_e2e.py`: a real hub delivers a hub-signed, audience-bound JWT via `response_mode=form_post` to a
real `blizzard runner host`'s `POST /api/auth/callback` — the whole chain real over localhost — ending in a
`bz_runner_session` cookie and an unlocked human-lane route. A second federation scenario rotates the hub signing key
(`POST /api/auth/rotate-signing-key`) and drives a fresh bounce minted under the just-rotated `kid`, proving the live
runner's JWKS cache refetches with no restart. The runner's three-lane gating split — human-lane 401, worker-hook/socket
ungated — is pinned at the unit and component tiers (`test_runner_route_gating.py`, `test_runner_federation.py`).

### blizzard:crash-sweep

`BLIZZARD_CRASH_SWEEP=1 uv run pytest -m crash_sweep tests/crash/` (`mise run crash-sweep`) — the FULL kill-9 sweep
([`../../../architecture/crash-correctness.md`](../../../architecture/crash-correctness.md)). It enumerates the
crash-point registry (`blizzard.foundation.crash.discover_crash_points`) and, per point, runs the hub and runner as real
subprocesses over the mock fleet, arms the point so its owning daemon `SIGKILL`s itself there, then asserts the
invariant checker (`blizzard dev check-invariants`) is green over both stores and the chunk still lands exactly once
after an unarmed restart — startup is REAP. It needs the sibling `blizzard-mock` worktree and a winter source, and is
skipped without `BLIZZARD_CRASH_SWEEP=1`.

The registry's boundary families are `resume.`, `abandon.`, `pause.`, `hubnode.` (the generic hub command node's
per-step and pending-poll windows — `bzh:crash-point-registry`,
[`../../../architecture/crash-correctness.md`](../../../architecture/crash-correctness.md)), `migrate.`, `attach.`,
`nudge.`, `checks.`, and `preempt.`, plus ungrouped generic build-to-deliver points that mostly fire in the runner loop.
No case count is kept — the predicate is the membership test, not a number that drifts. `claim.` — the route-claim
boundary between persisting the route with its capability-token fact and the runner reading the plaintext token back —
is the first ungrouped point armed on the hub, recovered generically by the runner's interrupted-claim adoption rather
than a dedicated scenario.

- `migrate.` — the cross-graph migration window, armed on the hub — is swept by `test_kill9_at_migrate_crash_point`: a
  kill right after the atomic re-pin loses only the `MIGRATED` response; the runner's replay re-derives it via the
  `accepted_migration` probe, the migration invariants green. Its hub-landing sibling
  `test_kill9_at_migrate_crash_point_landing_on_a_hub_node` drives a migration onto a hub-executed node, where the route
  is retained, not released: the replay returns `HUB_NODE_TAKEN`, the holding runner keeps its envs, and its ADVANCE
  poll drives the landed hub node to `done` instead of the chunk wedging at `delivering`. The per-chunk intended
  migration is swept on the same point by `test_kill9_at_migrate_crash_point_for_an_intended_migration`; its coverage at
  the component and unit tiers is `tests/test_intended_migration_apply.py`, `tests/test_chunk_edit_api.py`, and
  `tests/test_hub_cli_chunk.py`, since e2e's `test_migration_e2e.py` exercises only the authored-choice migration.
- `attach.` — the worker artifact-attach durability window, armed on the runner — is swept by
  `test_kill9_at_attach_crash_point`: the runner's local `POST /api/leases/{id}/attachments` records the attachment in
  one committed txn, the kill lands in the after-record-before-response window, and the durable row with full provenance
  is still readable via `attachments_for_lease` after an unarmed restart. `attach.` is an out-of-band HTTP write no loop
  step drives, so its scenario stands up a real runner daemon alone — no hub, no forge — seeding a parked lease and its
  capability token, the invariant checker running over the runner store only.
- `nudge.` — the produces-unmet nudge-once window, armed on the runner — is swept by `test_kill9_at_nudge_crash_point`
  over both of its members: a `produces:` name with neither commit nor attachment gets exactly one resumed nudge in
  `_advance_exited_worker`, gated on a durable `(lease, epoch)` fact recorded before the resume it guards, so
  at-most-once is structural — recovery consults the fact, never the resume's outcome. This window fires inside ADVANCE,
  so a real hub stands up too.
- `checks.` — the checks-at-exit windows, armed on the runner — is swept by `test_kill9_at_checks_crash_point` over both
  of its members: the runner runs a node's `checks:` at worker exit, recording each result row then a `checks_ran`
  marker; a kill before the marker leaves it unset and recovery re-runs the checks with latest-wins overwrite, while
  after the marker recovery reads the recorded results back and judges. The bounded-CI representative is the
  recovery-critical `checks.after-results.before-marker`.
- `preempt.` — the operator-restart teardown window, armed on the runner — is swept by
  `test_kill9_at_preempt_crash_point`: an operator restarts a running chunk and the runner dies between killing the
  displaced worker and recording the `preempted` closure; recovery re-derives the same preempt off the hub's
  still-standing fence — the lease closes `preempted`, never `reaped` or `failed`, which would spend the retry budget
  the move exists to protect.

Whole-process cases round it out — `tests/crash/test_kill9_sweep.py`'s own unparametrized test functions signal a whole
daemon process or process group, a graceful SIGTERM qualifying as readily as a `kill -9`: an external runner kill
mid-flight both before and after the worker's commit is durably declared, daemon restarts re-attaching an in-flight
session in place, and a `killpg` of the hub process group mid-delivery between repo pushes, both land graphs swept.

In CI the `pr` and `push` workflows run the bounded CI profile —
`BLIZZARD_CRASH_SWEEP=1 BLIZZARD_CRASH_SWEEP_CI=1 uv run pytest -m crash_sweep tests/crash/` (`mise run crash-sweep-ci`)
— one representative point per boundary family plus the whole-process cases and the recovery-critical windows, roughly
75 seconds on a GitHub runner. Both workflows run it as a real gate over a multi-repo checkout — `blizzard`,
`blizzard-mock`, and the public `blizzard-workspace` (the winter source) as siblings, `BLIZZARD_MOCK_WINTER_SOURCE`
pointed at the last. The bounded subset is intersected with the live registry and asserts each named point still exists
(`bzh:crash-point-registry`), so a rename fails loudly; the FULL sweep stays the documented local command
(`mise run crash-sweep`) and runs in the tag `release` workflow.
