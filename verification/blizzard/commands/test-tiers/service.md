# `blizzard:service-test` detail (`bzh:matrix-tier-service`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading, every test-filename code span, and each `mise run` name with its paired command span are machine-checked registrations — keep them verbatim, inside the section. -->

The service spoke of the test-tier hub [`../test-tiers.md`](../test-tiers.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### blizzard:service-test

The tier command is `BLIZZARD_SERVICE=1 uv run pytest tests/service/` (`mise run service-test`) — a running hub or
runner daemon's HTTP API exercised from outside the process against a mock counterpart, seams bound to the mock fleet.
It is distinct from `blizzard:e2e`, which drives the loop in-process one tick at a time and drives the served board
through a real browser. It needs the sibling provisioned `blizzard-mock` worktree (its venv ships the mock-fleet console
scripts, the stub IdP, and `mock-claude-code`) plus a winter source, and skips cleanly without `BLIZZARD_SERVICE=1`.

**Hub against mock runner plus mock forge.** A claim then a completion advances the chunk over the wire
(`test_claim_and_completion_advance_the_chunk_over_the_wire`), stale epochs are rejected, and route-token authz runs
under `route_token_mode=enforce`. Under `produces_mode=enforce` a completion for a node declaring `produces:` is fenced
out over the wire, chunk unadvanced, unless every declared name carries an explicit `attached=True` artifact; a
fallback-only completion still applies under the default `warn`.
`test_git_commit_covered_produces_name_is_accepted_under_enforce_over_the_wire` pins the accept end of the coverage
agreement (unit-tier sibling `test_produces_coverage_agreement.py`): a name covered by a pushed commit carries
`attached=False` and is accepted. `test_queue_shaping_group_and_reorder_reflected_in_peek` drives
`POST /api/chunks/{id}/group` and `PUT /api/queue` against the running hub and reads the result off `GET /api/queue`,
failing a shaping the domain applies but the wire does not surface; its component-tier sibling
`tests/test_queue_shaping.py` asserts the same shaping without the wire.

**Runner against mock hub.** `unreachable` buffers, `drop_ack` proves idempotency, and a `stale_envelope` is tolerated —
the chunk lands because the runner fences on its own lease epoch, not the envelope
(`test_stale_envelope_is_tolerated_and_the_chunk_still_lands`).
`test_advance_harvests_git_commits_from_every_bound_environment` pins that the harvest spans every bound environment —
the loss a `bindings[0]` read makes silent.
`test_graph_scoped_artifact_reads_from_the_runners_own_pin_with_the_hub_unreachable` is the first service-tier exercise
of a lease-token-authorized worker-lane read route: a `--scope graph` read resolves from the runner's own mint-time
mirror with the mock hub down while the same lease's node-scope read still 503s (the `_worker_credential` seam).

**Usage over the wire** (`test_usage_service.py`) runs both directions. Runner-to-mock-hub, a real runner's
`usage.recorded` facts ride the store-and-forward buffer, survive a hub outage, and flush exactly once.
Mock-runner-to-live-hub, usage pushed through the real `POST /api/fleet/events` becomes per-node-step usage plus the
derived chunk total (`cost_partial` on absent cost) read off the live `GET /api/chunks/{id}` and `GET /api/chunks`,
idempotent on a replayed seq.

**Hub SSE live fan-out** is proven only at this tier: the component tier can only assert an event was recorded, off the
broker's replay tail, while the publish-to-subscriber-queue-to-wire leg a live board depends on is real only here, via
the `sse_tap` helper in `tests/service/support.py`. A subscriber on `GET /api/events/stream` before the act receives
`queue-changed` the instant a cross-graph migration re-queues a chunk, and exactly one frame across the migration and
its duplicate-delivery replay (the mock runner's `replay` lever) — 0 if the publish drops, 2 if the replay guard fails.
The operational event feed (`test_event_log_service.py`) rides the same fan-out: the mock runner's
`/_drive/report-event` drives one `event.recorded` fact, a pre-connected subscriber receives `event-logged` exactly
once, the folded event reads back off the live `GET /api/events`, and a fixed-seq replay pins idempotency; the real
runner's own emission and buffering is proven at the unit and component tiers.

**Runner SSE live fan-out** has the same shape over the runner's own stream and vocabulary, all in
`tests/service/test_runner_service.py`:

- `test_runner_stream_delivers_live_and_replays_from_last_event_id` proves live delivery to a pre-connected subscriber
  and resume from `Last-Event-ID` across a reconnect.
- `test_runner_stream_replays_a_restarted_brokers_buffered_tail_past_a_stale_cursor` covers the fresh broker already
  holding buffered events at reconnect, so the stale cursor reaches the replay read — unresolved, it silently empties
  the tail rather than merely dropping live frames.
- `test_runner_stream_resumes_live_after_a_restart_reset_the_broker_ids` covers a second daemon instance behind the same
  port, its broker minting ids from zero, resuming a cursor the first minted; the clamp is pinned by the unit-tier
  `tests/test_foundation_events.py`.
- `test_runner_sigterm_returns_promptly_with_a_client_parked_on_the_stream` proves a signal-driven shutdown still
  returns `server.run()` with a client held open.

`blizzard:e2e`'s `test_runner_panel_live_e2e` scenario
([`../../e2e-scenarios/runner-panel.md`](../../e2e-scenarios/runner-panel.md)) carries the fan-out one tier further — a
real `blizzard-runner host` subprocess observed through a real browser on the served panel, nothing stubbed.

**Transcripts.** `test_transcript_is_read_back_through_the_runner_http_api` drives a chunk through the real fleet, then
reads `GET /api/leases` and `GET /api/leases/{lease_id}/transcript` off the runner's own local HTTP API — real turn
kinds with `tool_output` populated, the `Bash` turn's output cross-checked against the real commit sha off the bare
origin, unsatisfiable by a fixture. `test_a_closed_leases_transcript_resolves_to_the_hub_through_the_runner_api` walks
the route's three provenance homes against a real `build_hosted_app` daemon: `"local"` while the lease is open,
`"archived"` once the mock hub holds its segments — still `"archived"` after the local file is deleted mid-run — and
`hub_unreachable: true` once the mock-hub subprocess is gone. That closed-lease walk is the only real-counterpart drive
of the runner's outbound fleet-plane read; the unit tier binds a stubbed transport, and
`test_transcript_segments_service.py` drives the hub-side route with raw httpx.

**The OAuth login dance** (`test_auth_login_service.py`) is proven only at this tier: a running hub under
`auth.mode = "oauth"` whose `authorize` 302s to the `blizzard-mock` stub IdP (`tool:mock-fleet`, `blizzard-mock-idp` —
both provider shapes at one origin) and whose `callback` exchanges the stub's code over the real wire, ending in a
resolving `bz_session` cookie and a working `GET /api/me`, for both the `oidc` and `github` conformers. Also here: a
two-provider hub lists both from `GET /api/auth/providers`, `POST /api/auth/logout` deletes the session row so `/api/me`
401s, and the stub's `refuse_callback` lever surfaces as `login_failed` over the wire. The component-tier
`test_auth_login_api.py` drives the same routes against an in-repo fake provider — covering bad `state`, the
`login_failed` fact, the linking rule, and the no-token-cookie shape; only the service method exercises a real HTTP
authorize/token/userinfo exchange.

**CLI login** (`test_cli_login_service.py`) proves the `blizzard hub login` PKCE code exchange only at this tier: the
hub's `client=cli` authorize branch (mandatory S256 PKCE) serves a browserless scripted "browser" that captures the
single-use code from both the loopback-redirect form (a 302 query-string code, never a token) and the paste-code page,
then redeems it with its verifier at `POST /api/auth/cli/token` for a hub-minted session token, never a runner-style
JWT. A bare bearer client — the CLI's own shape — authenticates `GET /api/me` off that token alone, and
`POST /api/auth/logout` with the same bearer revokes it server-side so a byte-identical retry 401s; the CLI never
contacts the stub IdP, only the hub's own routes. The exchange's rejection matrix — wrong or missing verifier,
unregistered redirect form, replayed code, and expired code — is pinned by the component-tier `test_cli_login_api.py`;
the loopback listener and paste-code mechanics sit with the unit-tier `test_cli_login_mechanics.py` and
`test_hub_cli_login.py`.

**Runner SSO federation's JWT/JWKS wire leg** (`test_idp_federation_service.py`) is the browserless companion to e2e's
`test_runner_federation_e2e.py`: a real hub delivers a hub-signed, audience-bound JWT via `response_mode=form_post` to a
real `blizzard runner host`'s `POST /api/auth/callback` — the whole chain real over localhost — ending in a
`bz_runner_session` cookie and an unlocked human-lane route. A second federation scenario rotates the hub signing key
(`POST /api/auth/rotate-signing-key`) and drives a fresh bounce under the just-rotated `kid`, proving the live runner's
JWKS cache refetches with no restart. The runner's three-lane gating split — human-lane 401, worker-hook and socket
ungated — is pinned at the unit-tier and component-tier by `test_runner_route_gating.py` and
`test_runner_federation.py`.
