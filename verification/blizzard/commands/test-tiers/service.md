# `blizzard:service-test` detail (`bzh:matrix-tier-service`)

<!-- the `###` section below is machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` heading, every test-filename code span, and each `mise run` name with its paired command span are machine-checked registrations — keep them verbatim, inside the section. -->

The service spoke of the test-tier hub [`../test-tiers.md`](../test-tiers.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### blizzard:service-test

The daemon-HTTP half runs `npx playwright test` (`mise run playwright`), selecting service projects with
`mise run playwright -- --project='service-*'` from the repo root. New daemon behavior tests live in that package under
`tests/service/`, in three folders that each run as their own project: `hub/` as `service-hub` and one
`service-hub-<profile>` per profile subfolder; `runner/` as `service-runner`, a real runner host on the test's own mock
hub with no setup; and `fleet/` as `service-fleet`, a real runner host enrolled in a tenant of the test's own on the
shared real hub, with a `service-fleet-<profile>` for each subfolder named after a hub profile. One `service-*`
selection reaches all of them; its authoring rules are [service-tests.md](../../service-tests.md). The existing Python
half runs `BLIZZARD_SERVICE=1 uv run pytest -n auto tests/service/` (`mise run service-test`), retaining its described
daemon cases until ported and the external-tool bindings whose subject is Python itself. Both exercise a running daemon
from outside against the mock fleet. This differs from `blizzard:e2e`, which drives the loop in-process and the served
board in a real browser. The Python half needs the sibling provisioned `blizzard-mock` worktree (its venv ships the
mock-fleet scripts, stub IdP, and `mock-claude-code`) and skips cleanly without `BLIZZARD_SERVICE=1`.

The same tier also binds a whole-CLI external-tool fake the mock fleet emits (`bzh:external-cli-fake-is-service-tier`).

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

**A finding's exits and a routine's trend** (`finding-exits.spec.ts`) is the tier's only two-edge finding proof:
findings are minted the way a routine mints them — a real routine run, promoted, then the mock runner submitting the
run's `delta` artifact over the wire, then the hub's own `POST /api/chunks/{id}/garden-delivery` — and every exit verb
plus `reopen` is then driven twice, once as raw HTTP and once through the real `blizzard hub finding` binary against the
running daemon. It pins what an in-process client cannot: the note requirement refusing at both edges (a blank note is
422 on the wire and a non-zero exit in the CLI), one call exiting many ids, a later delta op naming an exited finding
rejected while a `gone`-flagged one is still a live target, the `GET /api/routines/trend` per-period created/exit counts
with their outflow-vs-withdrawn roll-ups and introduced-age cut rendered identically by `blizzard hub routine trend`,
and delivery-triggered closure end to end — an accepted garden proposal's minted item, landed by a `merged/` marker,
closing that proposal's findings to `delivered` through one requested pass of the daemon's close-intent drain.

**Runner against mock hub.** `unreachable` buffers, `drop_ack` proves idempotency, and a `stale_envelope` is tolerated —
the chunk lands because the runner fences on its own lease epoch, not the envelope
(`tests/service/runner/runner.spec.ts::test_stale_envelope_is_tolerated_and_the_chunk_still_lands`).
`test_advance_harvests_git_commits_from_every_bound_environment` pins that the harvest spans every bound environment —
the loss a `bindings[0]` read makes silent.
`tests/service/runner/runner.spec.ts::test_graph_scoped_artifact_reads_from_the_runners_own_pin_with_the_hub_unreachable`
is the first service-tier exercise of a lease-token-authorized worker-lane read route: a `--scope graph` read resolves
from the runner's own mint-time mirror with the mock hub down while the same lease's node-scope read still 503s (the
worker's call takes the spawn credential the mock harness recorded — `mock-claude-code` records the `BLIZZARD_*` lease
token, lease id and runner URL its runner exported — not a minted one). A seeded chunk driven to `stopped` over
`POST /_seed/stop` exercises PULL's two terminal-fact paths over a real hub response rather than `FakeHub`:
`tests/service/runner/runner.spec.ts::test_pull_abandons_the_active_lease_when_the_hub_reports_the_chunk_stopped` and
`tests/service/runner/runner.spec.ts::test_pull_closes_the_local_escalation_when_the_hub_reports_the_chunk_stopped`. A
peek carrying a marked head and an unmarked entry behind it is driven under both of a runner's selection policies
against a real mock hub:
`tests/service/runner/runner.spec.ts::test_fill_reaches_past_a_marked_head_by_default_against_a_real_mock_hub` claims
the unmarked entry while the marked one stays `ready`, and
`tests/service/runner/runner.spec.ts::test_fill_strict_holds_at_a_marked_head_against_a_real_mock_hub`
(`[queue] strict`) claims neither.

**Usage over the wire** runs both directions. Runner-to-mock-hub
(`tests/service/runner/usage.spec.ts::test_runner_buffers_usage_facts_through_a_hub_outage_and_flushes_once`), a real
runner's `usage.recorded` facts for the chunk stay unacknowledged through an attempted flush during a hub outage, then
reach the hub once, summing to the genuine worker's recorded usage. Mock-runner-to-live-hub
(`tests/service/hub/usage.spec.ts`), usage pushed through the real `POST /api/fleet/events` becomes per-node-step usage
plus the derived chunk total read off the live `GET /api/chunks/{id}` and `GET /api/chunks`, idempotent on a replayed
seq — a pushed `estimated_cost_usd` reads back on both the per-step row and the total, kept apart from `cost_usd`, and
`cost_partial` flags a row only when it carries neither amount.

**The forge-status projection** (`tests/service/fleet/forge-status.spec.ts::test_forge_status_projection_e2e`) runs on a
fresh hub of its own with `annotation_interval_seconds = 1` and a real runner host, every `forge_status` pass stepped.
The hub spec `tests/service/hub/forge-status.spec.ts` proves only an opted-in source's issues are labelled. The case
proves ingest shows `blizzard:ingested`, a worker held at a checkpoint shows `blizzard:in-progress`, and done clears
both. A chunk stopped before any runner claims it has its marker cleared on the next pass. A hand-deleted label comes
back only once the full-pass floor (five intervals) elapses, because the hub holds only in-memory probe state. A forge
outage, stood in by the forge's own `unreachable` lever, since a process kill would wipe the forge's issue and label
state, records one `forge-status-source-skipped` event naming the source id in `GET /api/events`, leaves chunk reads
served, and the label is intact once the lever clears.

**The exported events**
(`tests/service/fleet/egress-events.spec.ts::test_the_exported_events_agree_with_the_hubs_own_counts`) runs on a fresh
hub exporting NDJSON, with a real runner host shipping transcripts, every hub and host pass stepped. One forge, hub and
runner carry two chunks: a Claude Code build and an OpenCode review, whose workers read files, invoke a skill and spawn
an agent whose child session reads a file, and an ask answered by a person, which extends its transcript through the
resumed session. The case proves `events_current` grouped by file, skill, agent type and node equals
`blizzard hub analytics summary counts-{files,skills,agent-types,nodes}`, with paths made relative to the worker's
working directory; the docs' files-a-station-read-last-week recipe names the review node's reads, the child session's
included; no row, manifest or schema carries the planted prompt, tool input or output, key, question or working
directory, or an event's payload; and after a forced `blizzard hub analytics re-derive` and a real
`blizzard runner transcript reship` the export holds a `dropped` row for the superseded segment and the counts still
equal the hub's.

**A night of chunks, exported** (`tests/service/fleet/egress-night.spec.ts`) runs the night once, on one held stack,
under eight titled tests that each read the directories back the way a warehouse would. One forge, one hub and one
runner carry six chunk shapes, stepped throughout: a plain build, a review bounce, a human gate, an ask answered by a
person, a delivery conflict from the forge's `merge_conflict` lever and an escalation, across two graphs that both name
a `build` and a `deliver` node. The runner host's repository is the forge's own, so a landing merges the branch the
worker pushed. The hub exports it live as NDJSON, is restarted over the same record with a changed configuration and
exports it live again as Parquet into a second directory after the real `blizzard hub egress reset`, and
`blizzard hub egress backfill` writes a third copy over the night's window, given as `Z` instants.

- `test_both_live_exports_hold_the_same_newest_rows` — the NDJSON and Parquet live newest-copy row sets are equal
  excluding `exported_at`, and neither dataset is empty.
- `test_both_exports_hold_the_hubs_record` — every step in the chunks' history and every usage fact on the
  `spend-chunks` surface, tokens and billed cost, is in both exports.
- `test_both_exports_name_the_runner_by_its_minted_id_and_its_name` — every step the runner ran and every invocation
  carries, in both formats, the `rn_` id the hub minted for the runner beside its configured name.
- `test_nothing_planted_leaves` — a scan of the rows, manifests and schemas finds none of the planted "what never
  leaves" values, the lease tokens the runner exported to the workers among them.
- `test_a_backfill_of_the_window_equals_the_live_export` — the backfill of the night's window writes rows equal to the
  live newest copies, excluding `exported_at`.
- `test_recipes_agree_with_the_hubs_analytics` — the docs' cost recipe matches
  `blizzard hub analytics summary spend-nodes` over the same window per station, in both formats, and the
  slowest-station recipe names the station built to be slowest on its own graph, held at a checkpoint across a clock
  poll.
- `test_cost_by_node_splits_a_shared_node_name_by_graph` — the cost recipe keeps `build` and `deliver` as a distinct
  station on each graph that names them.
- `test_published_newest_views_return_the_newest_copies` — the dictionary's published newest-copy views return the
  identities the rows' own newest copies name, in both formats.

**Runner release policy** (`tests/service/runner/release.spec.ts`) exercises two runners spending distinct sampled
subscriptions on one stepped host. A utilization line crossed during a checkpointed build releases the next node to an
admitting neighbour; when both decline, their completed passes leave the chunk ready and unheld until either gate opens.
A usage-limited worker books its real invocation usage before its lease closes `released`, and the neighbour takes a
fresh lease at the start of `build`. The host environment, lease usage and runner brake reads, with the mock hub's chunk
and decline registrations, are the public observations of these transitions.

**The one dollar figure** (`tests/service/runner/spend-figure.spec.ts`) drives both spend controls off an estimate
alone: a real runner's OpenCode turns run under a subscription-billed `mock-opencode`
(`BLIZZARD_MOCK_OPENCODE_BILLED_ZERO=1`), priced off a `models.json` the host's `runnerModelPrices` option writes into
its `XDG_CACHE_HOME`, passed through to the worker.
`test_runner_ceiling_pauses_on_an_estimated_spend_with_a_tilde_led_reason` sets `runner_ceiling_usd` under the lease's
estimate and reads the engaged local pause's `~$`-led reason off the runner's own `GET /api/runner`;
`test_chunk_cap_escalates_on_an_estimated_chunk_cost_with_a_tilde_marked_detail` seeds an estimate-only chunk total past
`chunk_cap_usd` on the mock hub and reads the `spend-cap` escalation's `~`-marked detail back off it.

**Hub SSE live fan-out** is proven only at this tier: the component tier can only assert an event was recorded, off the
broker's replay tail, while the publish-to-subscriber-queue-to-wire leg a live board depends on is real only here, via
`tests/service/hub/hub.spec.ts`, reading the stream through the Playwright `events` fixture in
`tests/harness/events.ts`. A subscriber on `GET /api/events/stream` before the act receives `queue-changed` the instant
a cross-graph migration re-queues a chunk, and exactly one frame across the migration and its duplicate-delivery replay
(the mock runner's `replay` lever) — 0 if the publish drops, 2 if the replay guard fails. The operational event feed
(`event-log.spec.ts`) rides the same fan-out: the mock runner's `/_drive/report-event` drives one `event.recorded` fact,
a pre-connected subscriber receives `event-logged` exactly once, the folded event reads back off the live
`GET /api/events`, and a fixed-seq replay pins idempotency; the real runner's own emission and buffering is proven at
the unit and component tiers.

**Runner SSE live fan-out** has the same shape over the runner's own stream and vocabulary, all in
`tests/service/runner/runner.spec.ts`:

- `tests/service/runner/runner.spec.ts::test_runner_stream_delivers_live_and_replays_from_last_event_id` proves live
  delivery to a pre-connected subscriber and resume from `Last-Event-ID` across a reconnect.
- `tests/service/runner/runner.spec.ts::test_runner_sigterm_returns_promptly_with_a_client_parked_on_the_stream` proves
  a signal-driven shutdown still returns `server.run()` with a client held open.

The runner route's restart clamp — a stale `Last-Event-ID` against a fresh broker — is proven at component tier, not
here:

- Live resumption, component tier:
  `tests/test_runner_events_stream.py::test_runner_stream_resumes_live_after_a_restart_reset_the_broker_ids`.
- Buffered replay, component tier:
  `tests/test_runner_events_stream.py::test_runner_stream_replays_a_restarted_brokers_buffered_tail_past_a_stale_cursor`.

`blizzard:e2e`'s `test_runner_panel_live_e2e` scenario
([`../../e2e-scenarios/runner-panel.md`](../../e2e-scenarios/runner-panel.md)) carries the fan-out one tier further — a
real `blizzard-runner host` subprocess observed through a real browser on the served panel, nothing stubbed.

**Transcripts.** `tests/service/runner/runner.spec.ts::test_transcript_is_read_back_through_the_runner_http_api` drives
a chunk through the real fleet, then reads `GET /runners/{runner_id}/api/leases` and
`GET /runners/{runner_id}/api/leases/{lease_id}/transcript` off the runner's own local HTTP API — real turn kinds with
`tool_output` populated, the `Bash` turn's output cross-checked against the real commit sha off the bare origin,
unsatisfiable by a fixture.
`tests/service/runner/runner.spec.ts::test_a_closed_leases_transcript_resolves_to_the_hub_through_the_runner_api` walks
the route's three provenance homes against a real `build_hosted_app` daemon: `"local"` while the lease is open,
`"archived"` once the mock hub holds its segments — still `"archived"` after the local file is deleted mid-run — and
`hub_unreachable: true` once the mock-hub subprocess is gone. That closed-lease walk is the only real-counterpart drive
of the runner's outbound fleet-plane read; the unit tier binds a stubbed transport, and
`tests/service/hub/transcript-segments.spec.ts` drives the hub-side route.

**The OAuth login dance** (`tests/service/hub/auth/auth-login.spec.ts`) is proven only at this tier: a running hub under
`auth.mode = "oauth"` whose `authorize` 302s to the `blizzard-mock` stub IdP (`tool:mock-fleet`, `blizzard-mock-idp` —
both provider shapes at one origin) and whose `callback` exchanges the stub's code over the real wire, ending in a
resolving `bz_session` cookie and a working `GET /api/me`, for both the `oidc` and `github` conformers. Also here: a
two-provider hub lists both from `GET /api/auth/providers`, `POST /api/auth/logout` deletes the session row so `/api/me`
401s, an uninvited first sign-in is refused without a session, and the stub's `refuse_callback` lever surfaces as
`login_failed` over the wire. A fresh hub also checks the configured superuser's first verified sign-in: an
authoritative provider claims the bootstrap, while a non-authoritative one refuses it. Invitations are issued through
`POST /api/invitations`, and provider listings include the profile's `stub` beside `github` when configured. The
component-tier `test_auth_login_api.py` drives the same routes against an in-repo fake provider — covering bad `state`,
the `login_failed` fact, the linking rule, and the no-token-cookie shape; only the service method exercises a real HTTP
authorize/token/userinfo exchange.

**CLI login** (`cli-login.spec.ts`) proves the `blizzard hub login` PKCE code exchange only at this tier: the hub's
`client=cli` authorize branch (mandatory S256 PKCE) serves a browserless scripted "browser" that captures the single-use
code from both the loopback-redirect form (a 302 query-string code, never a token) and the paste-code page, then redeems
it with its verifier at `POST /api/auth/cli/token` for a hub-minted session token, never a runner-style JWT. A bare
bearer client — the CLI's own shape — authenticates `GET /api/me` off that token alone, and `POST /api/auth/logout` with
the same bearer revokes it server-side so a byte-identical retry 401s; the CLI never contacts the stub IdP, only the
hub's own routes. The exchange's rejection matrix — wrong or missing verifier, unregistered redirect form, replayed
code, and expired code — is pinned by the component-tier `test_cli_login_api.py`; the loopback listener and paste-code
mechanics sit with the unit-tier `test_cli_login_mechanics.py` and `test_hub_cli_login.py`.

**Joining a runner with `blizzard runner init`** (`tests/service/fleet/runner-init.spec.ts`) is proven over the real
wire only at this tier: init runs in its own process against a real hub on `auth.mode = "none"`, adds the runner through
`POST /api/runners`, and leaves the minted token in the host's `.env`; the host then registers under the hub-minted
`rn_` id, online after a completed step. The same id survives a rename and a deleted runner store. Against a retired
runner, init refuses, names `blizzard hub runner reinstate <id>`, and leaves the held tokens unchanged. After a reset of
the hub's data, init refuses without `--allow-readd`, naming the hub URL it asked, adding nothing, and leaving the held
tokens unchanged; with the flag it adds a fresh runner and replaces the token. The cases whose list reads are
whole-tenant run at `fresh-tenant`; the hub-data reset runs at `fresh-hub`. Every in-process `runner init` at the unit
and component tiers joins the suite-wide fake hub in `tests/runner_init_fakes.py` instead.

**Ingesting a colliding runner into a host** (`test_host_ingest_service.py`) is proven over the real wire only at this
tier: two host directories hold one runner each under one host the mock hub knows, their stores colliding on the
outbound and transcript `seq`s, a `route_tokens` chunk id, a `graph_artifacts` key, and the workspace id. A real
`blizzard-runner ingest --workspace-id` moves one runner into the other's host, which then starts: both runners resume
every lease, and the hub applies every backlog fact above each runner's mark. Its refusals, resume, and collisions are
pinned at the component tier by `test_runner_ingest.py`.

**Runner SSO federation's JWT/JWKS wire leg**
(`tests/service/fleet/auth/idp-federation.spec.ts::test_the_wire_leg_ends_in_an_unlocked_runner_route`) is the
browserless companion to the UI tier's runner-federation spec: a real hub delivers a hub-signed, audience-bound JWT via
`response_mode=form_post` to a real `blizzard runner host`'s `POST /api/auth/callback` — the whole chain real over
localhost — ending in a `bz_runner_session` cookie and an unlocked human-lane route. A second federation scenario
rotates the hub signing key (`POST /api/auth/rotate-signing-key`) and drives a fresh bounce under the just-rotated
`kid`, proving the live runner's JWKS cache refetches with no restart
(`tests/service/fleet/auth/idp-federation.spec.ts::test_key_rotation_is_picked_up_by_a_live_runner_with_no_restart`). A
third, on a hub with two providers, hands the unauthenticated bounce to the `/login` chooser and resumes the pending
authorize request through the second provider
(`tests/service/fleet/auth/idp-federation.spec.ts::test_a_two_provider_bounce_resumes_through_the_login_chooser`). The
runner's three-lane gating split — human-lane 401, worker-hook and socket ungated — is pinned at the unit-tier and
component-tier by `test_runner_route_gating.py` and `test_runner_federation.py`.
