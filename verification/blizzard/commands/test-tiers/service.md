# `blizzard:service-test` detail (`bzh:matrix-tier-service`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading, every test-filename code span, and each `mise run` name with its paired command span are machine-checked registrations — keep them verbatim, inside the section. -->

A running hub or runner daemon's HTTP API exercised from outside the process against a mock counterpart. Spoke of the
[test-tier hub](../test-tiers.md).

Read [`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

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
([`../../e2e-scenarios/runner-panel.md`](../../e2e-scenarios/runner-panel.md)) carries fan-out one tier further: a real
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
