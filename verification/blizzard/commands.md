# Blizzard command detail (`bzh:matrix-command-detail`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->

Full per-method detail for the [../blizzard.md](../blizzard.md) Commands table rows marked *(more)* — one
`### <method-id>` section per row, in table order, except `blizzard:e2e` ([its own registry](./e2e-scenarios.md)). Read
[../blizzard.md](../blizzard.md) first for the short command and the method-id inventory.

### blizzard:unit-test

`uv run pytest -m unit` — the unit tier: one class or function in isolation ([tiers](../blizzard.md#test-tiers)). Bare
`uv run pytest` runs the unit + component default suite. **The packaged-prompt declaration guard** (issue #113 phase 6,
kind-branched by issue #143 Phase 5, `test_packaged_prompts_attach.py`) is the criterion-7 prompt-content check: for
every packaged graph (`src/blizzard/hub/graphs/*/graph.yaml`), every runner node declaring a `produces:` entry must have
its inlined prompt text name the **kind-appropriate** current declaration verb — an `asset` entry names
`blizzard runner artifact create --name <that-exact-name>`, a `git_commit` entry (the build nodes, now that the worker
pushes and declares its own commits) names `blizzard runner artifact commit` — and **no** packaged prompt may name the
deprecated `blizzard runner attach` alias. So a prompt edit that drops or mistypes the declaration instruction, or
reverts to the deprecated `attach` spelling (silently defeating the declare→completion-assembly path in favour of the
git-commit fallback), fails here rather than shipping green, a regression no graph-load or validation test catches
because the prompt is opaque prose to the parser. **The produces-coverage agreement guard** (issue #113,
`test_produces_coverage_agreement.py`) drives the hub's backstop (`check_produces`) and the runner's nudge check
(`_missing_produces`) over **one** scenario matrix and asserts the two return the same verdict for every scenario — the
anti-drift guard on the shared `wire.completion.produces_coverage` predicate, which calls the internal name-coverage
helper `satisfied_produces_names`. It exists because the bug it closes was a *disagreement*, not a wrong answer on
either side alone (the hub rejecting a git-commit-covered name under `produces_mode=enforce` that the runner already
treated as satisfied), and neither side's own tests can observe one: `test_produces_auth.py` sees only the hub,
`test_runner_nudge.py` only the runner. Each scenario also asserts the *expected* verdict, so two sides that re-forked
into the same wrong answer fail too rather than agreeing with each other. **The git-commit declare-and-verify round
trip** (issue #143 Phase 4, `test_artifacts_storage.py` + the `_verify_and_collect_git_commits` coverage in
`test_runner_loop.py`/`test_runner_gates.py`) pins the worker-declares/runner-verifies split: a fake
`IWorktreeGit.verify` drives ADVANCE's collection (verified → a `GIT_COMMIT` `SubmittedArtifact` carrying the origin the
environment's repo manifest named; unverified → dropped *and* reported as a `command-failed` the worker can act on,
still feeding the Phase-2 nudge), and `GitCommitArtifact`/`ArtifactRow` round-trip losslessly with `forge` carried (and
a legacy null-`forge` row reading back as `""`). The harvest spans **every** bound environment, not just the first —
`test_advance_harvests_git_commits_from_every_bound_environment` pins that a chunk holding two environments delivers
both, the loss a `bindings[0]` read made silent. Reporting an unverified declaration rather than only dropping it is
deliberate: non-coverage alone was the whole backstop until the coverage check could not see the `git_commit` spec, at
which point nothing was left to notice and a chunk reached `done` having delivered nothing. **The docket-fold agreement
guard** (issue #259, `test_packaged_docket_fold.py`) pins advanced-development-workflow's findings docket against the
prompts that restate it: `docket.md`, `build.from-review.md`, and `plan.from-plan-review.md` agree that a superseded
round's undisposed findings are abandoned by design, and `docket.md` and `retrospective.md` agree the fold closes an
unmatched finding whose target is an immutable artifact `accepted-wont-fix` rather than filing it — so an edit that
drops either agreement from one restating file without the other fails here rather than shipping a silent contradiction.
**Four sweep guards** landed with the 2608 gardening epic, each the mechanical signature of a class review had been
catching by hand: `test_openapi_descriptions.py` (issue #278) scans both committed specs — and the `wire/` models no
spec reaches — for prose an external API consumer cannot resolve (`bzh:comment-locality`'s generated-docstring clause);
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
([tiers](../blizzard.md#test-tiers)). **The fleet spend-since read** (epic #57 / #60, `test_fleet_spend_api.py`) proves
`GET /api/spend?since=` sums usage facts by `recorded_at` **across every chunk** — distinct from a chunk's own derived
total (`ChunkUsageTotalView`, covered under the usage-over-the-wire coverage in the `blizzard:service-test` row below):
the fleet-wide sum spans multiple chunks, a fact recorded before `since` is excluded, the cost-absent lower-bound +
`cost_partial` flag, and a malformed `since` 422s. **The checks-gate agreement guard** (issue #114,
`test_checks_gate_agreement.py`) is the same anti-drift shape as the produces-coverage agreement guard, applied to the
`requires_checks` gate: it drives **both** real decision sites — the runner's local gate at worker exit and the hub's
completion backstop — over one scenario matrix and asserts they reach the same accept/reject verdict (and the expected
one), so a future edit re-deriving "is a gated choice red?" inline on either side rather than calling the shared
`wire.completion.checks_gate_violated` predicate fails here.

### blizzard:sse-contract

`mise run sse-contract` — gates the SSE frame shape contract (issue #235) against the golden corpus `contracts/sse/`
(`manifest.json`, `README.md`'s forward-compatibility policy, and one `<kind>.json` per frame kind with named cases
pinning field optionality): first the Python producer+parse half (`tests/test_sse_contract.py`,
`blizzard:component-test`) — every case drives the real `EventBroker.publish_*` helper and asserts
`json.loads(event.data) == payload` (a producer-side field rename/add/drop goes red), then validates the same golden
against its `blizzard.wire.sse` model (`extra="forbid"`, so an undeclared field also goes red) and round-trips it
losslessly; then the board's half (`web/projects/fleet/src/lib/sse/sse-contract.spec.ts`, `web:unit-test`) — a stubbed
`fetch` feeds every golden, framed exactly as the hub frames it (plus the reserved comment and an interleaved
keepalive), through the **real** `SseService`/`FetchEventSource` byte-stream reader, asserting on what reaches
`SseHandle.events` rather than a hand-parsed object; a compile-time `FRAME_FIELD_SPECS` descriptor (keyed off the six
exported per-kind interfaces in `fleet-live.ts`) also fails to compile the moment an interface field is renamed or
dropped, and its runtime half cross-checks each golden's key set against it. Both suites read the **same physical
files** — no per-side copy — so moving a golden reddens whichever side has not caught up, and changing a side's shape
without moving the golden reddens that side; the closure assertions on both sides (`contracts/sse/`'s on-disk kind set
== `manifest.json`'s kind list == the broker's `EVENT_TYPES` tuple on the Python side, == `HUB_EVENT_TYPES` on the TS
side) catch a new kind added without a golden. `blizzard:manual-sse-probe` remains the method for what only a live
socket proves — framing and timing, not field shape.

### blizzard:restatement-sweep

```bash
uv run python scripts/restated_invariants.py check --strict --owners --context-root ../blizzard-context src tests docs README.md web/projects ../blizzard-mock/src
```

The check (`mise run restatement-check` for short) fails when a fact in the committed census
`scripts/restated-invariants.json` is stated at a site the census does not declare (`new`), when a declared site is no
longer observed (`stale`), when a declared non-owner site carries no reason, or when a designated owner does not state
its fact ([../../standards/one-prose-home.md](../../standards/one-prose-home.md)). A `new`/`stale` finding is refreshed
with `measure --write-sites` (rewrites `sites[]` to the observed tree, never by hand) plus a `reason` on any new
non-owner site; `measure --write-sites` itself refuses to run against a partial scan (a file skipped as unreadable or
unparsable), unless `--force`; `check` instead reports a skipped file as an informational `skipped` finding beside its
verdict without failing, so a `restatement sweep: clean` next to a `skipped:` line claims only the files that were
scanned. Local-only in its `--context-root` half: the sweep also reads the sibling `../blizzard-mock` checkout, but that
one is already a CI sibling the upper-tiers workflow checks out for other tiers; `../blizzard-context` is not checked
out anywhere in CI, which is the actual local-only cause. An unresolved `--context-root` refuses a green rather than
skipping silently.

### blizzard:gate

`mise run gate` (`./scripts/ci-gate.sh`) — the local reproduction of the shared `gate` job the `pr` and `push` workflows
both call: ruff format --check + ruff check + pyright + pytest, the OpenAPI spec-drift check, then eslint + vitest + the
structural gate (`web:structural-gate`) + generated-client drift over `web/`. **Stage any regenerated `openapi/` or
`web/` client output first**: the drift checks are a working-tree-vs-index `git diff`, so a staged-but-uncommitted
regeneration passes and an unstaged one fails the gate (`web:client-drift`). It is **not** the full master merge gate:
this command does not run `blizzard:service-test` or the bounded `blizzard:crash-sweep` CI profile
(`mise run crash-sweep-ci`); the `pr` workflow runs both as separate real gate jobs alongside `gate`, the same jobs the
`push` workflow runs, so a PR that breaks either tier fails its own check before it can merge. Run both locally too
before pushing for faster feedback than waiting on CI. The `bzh:sweep-release-only-tiers` tier rule (in
[tier rules](../blizzard.md#tier-rules)) names which surfaces this blind spot actually bites.

### blizzard:wheel

`mise run build` (`./scripts/build-wheel.sh`) — the one build entrypoint: builds both Angular apps into
`src/blizzard/static/{hub,runner}`, builds the single wheel (`uv build --wheel`) embedding those assets plus both
migration trees, then installs it into a clean **node-free** venv and runs `blizzard --version` — proving the released
artifact needs no Node. `BLIZZARD_VERSION` overrides the wheel version (dev builds / tag releases).

### blizzard:wheel-smoke

The exit-criterion serve smoke on the built wheel (node-free venv): `blizzard hub init <dir>` (idempotent, store
migrated to head) then `blizzard hub host --dir <dir> --port <p>` serves the embedded mission-control board (`GET /` →
the Angular `index.html` + hashed JS bundles, deep routes fall back to it) with `GET /api/health` → `200`; the same for
`blizzard runner init`/`host` (the local-panel shell). This is the **P5 exit criterion**.

### blizzard:image-smoke

`mise run image-smoke` (`./scripts/image-smoke.sh`) — builds the wheel then the hub container image
(`packaging/docker/Dockerfile`) and boots it on an **empty** data volume, asserting what a docker-free unit test cannot:
the container runs as a non-root uid, `git` resolves on `PATH`, `import psycopg` succeeds (the `postgres` extra), the
store is migrated to head **before** the daemon begins serving (`bzh:manual-migrations` — the entrypoint's own ordered
`init`-if-absent → `migrate` → `exec host`, never folded into the daemon's own startup path), and a live
`GET /api/health` → `200` / `GET /api/ready` → `ready: true`. Errors with a clear message rather than a docker CLI stack
trace when no docker daemon is reachable. **Local-only** — CI does build and push the multi-arch image (every `master`
push and every tag), so a build-level break is caught remotely, but it never *boots* what it publishes; no CI image
smoke exists yet, a named fast follow (issue #189's plan), not invented around. The docker-free static contract (`USER`,
the `git` install, the migrate-before-host ordering, the `ENV` defaults, the documented mount path) is pinned separately
at `blizzard:unit-test` (`tests/test_container_image.py`), so packaging rot fails the default gate on a machine with no
docker at all.

### blizzard:compose-smoke

`mise run compose-smoke` (`./scripts/compose-smoke.sh`) — stands up the reference compose deployment
(`packaging/docker/compose.yaml`: hub + postgres + Caddy) against a locally-built image on the localhost http-only
evaluation profile, asserting what a docker-free unit test cannot: `GET /api/ready` through the Caddy proxy port reports
`ready: true`, the hub's resolved `BZ_HUB_DB_URL` is the postgres one (proving #188's driver AC over a real connection —
hub `depends_on` postgres's health, so it never migrates against a database that isn't up), and `docker compose down`
(no `-v`) followed by `up` loses nothing (a durable artifact written directly into the postgres volume before the
restart is still readable after it). Errors with a clear message when no docker daemon / `docker compose` plugin is
reachable. **Local-only** — no CI compose smoke exists yet, the same named-gap pattern as `blizzard:image-smoke`. The
docker-free static contract — every durable path a named volume, the postgres health dependency, `trusted_proxies`
matching the declared network subnet, the hub naming a postgres `BZ_HUB_DB_URL`, and
(`test_hub_has_no_published_ports_only_reachable_through_the_proxy`) that the hub publishes no port of its own — is
pinned separately at `blizzard:unit-test` (`tests/test_compose_deployment.py`).

### blizzard:ci

`gh run watch --repo paul-gross/blizzard <run-id> --exit-status` — watch a GitHub Actions run (the `push` merge-gate on
master, or the `pr` gate on a PR) to completion and exit non-zero if it failed; the authoritative remote gate. List runs
with `gh run list --repo paul-gross/blizzard`; inspect a failure with
`gh run view --repo paul-gross/blizzard <run-id> --log-failed` (the workflows and this watch loop are documented in the
`blizzard` app repo's `docs/ci.md`).

### blizzard:service-test

`BLIZZARD_SERVICE=1 uv run pytest tests/service/` (`mise run service-test`) — the service tier: a **running** hub or
runner daemon's HTTP API exercised from outside the process (HTTP against a mock counterpart), seams bound to the mock
fleet — distinct from `blizzard:e2e`, which drives the loop in-process one tick at a time (and, in
`test_board_browser_e2e.py` and `test_board_cost_live_e2e.py`, drives the served board through a real browser). The
runner runs against the **mock hub** (`unreachable`→buffered, `drop_ack`→idempotent, `stale_envelope` → **tolerated**,
the chunk still landing because the runner fences on its own lease epoch rather than on the envelope it was handed
(`test_stale_envelope_is_tolerated_and_the_chunk_still_lands`), and a fourth scenario —
`test_transcript_is_read_back_through_the_runner_http_api` — drives a chunk through the real fleet, then reads
`GET /api/leases` and `GET /api/leases/{lease_id}/transcript` back through the runner's own local HTTP API, asserting an
`env` turn, `Edit`/`Bash` tool turns with `tool_output` populated, and an `asst` verdict turn, with the `Bash` turn's
`tool_output` cross-checked against the real commit sha read independently off the bare origin — unsatisfiable by a
fixture; and a fifth — `test_a_closed_leases_transcript_resolves_to_the_hub_through_the_runner_api` (blizzard#249) —
walking that same route's three D1 homes in one run against a real `build_hosted_app` daemon: `provenance: "local"`
while the lease is open, `"archived"` once it closes and the mock hub holds its segments — with the shipped `thinking`
turn read back intact, the loss a narrowing read would show (still `"archived"` after the local file is deleted mid-run,
the rotation criterion), and `hub_unreachable: true` once the mock-hub subprocess is gone and local cannot answer either
— the runner's **outbound** fleet-plane read, whose URL and headers no other tier drives against a real counterpart,
since the unit tier binds a stubbed transport and `test_transcript_segments_service.py` drives the hub-side route with
raw httpx); the hub against the **mock runner** + **mock forge** (a claim followed by a completion **advances the
chunk** over the wire (`test_claim_and_completion_advance_the_chunk_over_the_wire`), stale-epoch rejection, **queue
shaping over the wire** — `test_queue_shaping_group_and_reorder_reflected_in_peek` drives `POST /api/chunks/{id}/group`
and `PUT /api/queue` against the running hub and reads the result back off `GET /api/queue`, so a grouping or reorder
that the domain applies but the wire does not surface fails here; its component-tier sibling
`tests/test_queue_shaping.py` asserts the same shaping without the wire — route-token authz under
`route_token_mode=enforce`, and — issue #113 phase 5 — **produces-artifact authz** under `produces_mode=enforce`: a
completion for a node declaring `produces:` is fenced out over the wire, chunk unadvanced, unless it carries an explicit
`attached=True` artifact for every declared name, while a fallback-only completion still applies under the default
`warn`, driven by the mock runner's `/_drive/complete` `artifacts` field — the produces analogue of the route-token
levers; a **git-commit-covered** name is likewise **accepted** under `enforce`
(`test_git_commit_covered_produces_name_is_accepted_under_enforce_over_the_wire`), the accept end of the hub/runner
coverage agreement its unit-tier sibling `test_produces_coverage_agreement.py` pins — a name covered by a pushed commit
carries `attached=False`, and the hub once fenced exactly that shape out over the wire even though the runner's nudge
already treated it as satisfied). **SSE live fan-out** (issue #107) is proven at this tier and only at this tier: a
subscriber connected to `GET /api/events/stream` *before* the act receives `queue-changed` the instant a fresh
cross-graph migration re-queues a chunk, and receives **exactly one** across that migration and its duplicate-delivery
replay (the mock runner's `replay` lever submits the byte-identical completion twice, so both land in one live window —
the single count assertion fails at 0 if the publish is dropped and at 2 if the replay guard is). The component tier
asserts publication by reading the broker's *replay tail*, which shows an event was **recorded**, not **delivered**; the
publish → subscriber-queue → wire leg a live board depends on is real only here, via the `sse_tap` helper in
`tests/service/support.py`. The **operational event feed** (issue #125, `test_event_log_service.py`) rides the same
fan-out: the mock runner's `/_drive/report-event` verb drives one `event.recorded` fact, a subscriber connected before
the act receives `event-logged` **exactly once**, and the folded event reads back off the live `GET /api/events`
(mock-runner→live-hub); a direct fixed-seq replay pins the fold's per-runner-seq idempotency. The real runner's own
emission of these facts (and its store-and-forward buffering through a hub outage) is the runner's job, proven at the
unit/component tiers where it lands. **Usage over the wire** (epic #57 / #59, `test_usage_service.py`) is proven in both
directions: runner→mock-hub, a real runner's `usage.recorded` facts ride the store-and-forward buffer, survive a hub
outage, and flush exactly once; mock-runner→live-hub, usage facts pushed through the hub's real `POST /api/fleet/events`
become per-node-step usage + the derived chunk total (`ChunkUsageView` / `ChunkUsageTotalView`, `cost_partial` when a
row's cost is absent) read back off the live `GET /api/chunks/{id}` and `GET /api/chunks`, idempotent on a replayed seq.
**OAuth login dance** (epic #89 / issue #92, `test_auth_login_service.py`) is proven at this tier and only at this tier:
a running hub under `auth.mode = "oauth"` whose `authorize` 302s to the `blizzard-mock` **stub IdP** (`tool:mock-fleet`,
`blizzard-mock-idp` — both provider shapes at one origin) and whose `callback` exchanges the stub's code over the real
wire, ending in a resolving `bz_session` cookie and a working `GET /api/me`, for **both** the `oidc` (issuer discovery +
RS256 `id_token` verification) and `github` (code flow + `/user` + verified primary email) conformers; a two-provider
hub lists both from `GET /api/auth/providers`; `POST /api/auth/logout` deletes the session row so `/api/me` 401s; and
the stub's `refuse_callback` lever surfaces as the `login_failed` response over the real wire. The component tier
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
(decision D6 — never a runner-style JWT); a bare bearer client with no cookie jar — the CLI's own shape, exactly what
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
([../../architecture/crash-correctness.md](../../architecture/crash-correctness.md)): a pytest runner enumerating the
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
[../../architecture/crash-correctness.md](../../architecture/crash-correctness.md) `bzh:crash-point-registry`), and
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
and `attach.` (the worker artifact-attach durability window, #113 — armed on the **runner**, swept by
`test_kill9_at_attach_crash_point`: the runner's local `POST /api/leases/{id}/attachments` records the attachment in one
committed txn, then `kill -9`s in the after-record-before-response window, and the durable row — with full provenance —
is still readable via `attachments_for_lease` against the same store after an unarmed restart, the fact Phase 3's
completion assembly / the recovering ADVANCE tick re-derives (criterion 3). Unlike the loop-driven families this is an
out-of-band HTTP write no loop step drives, so its scenario stands up a real runner daemon alone — no hub, no forge —
seeding a parked lease + its capability token, since the durability property is loop-independent; the invariant checker
runs over the runner store only), and `nudge.` (the produces-unmet nudge-once window, #113 Phase 4 — armed on the
**runner**, swept by `test_kill9_at_nudge_crash_point` over both members `nudge.after-fired-fact.before-resume` and
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
representative is the recovery-critical `checks.after-results.before-marker`) alongside the ungrouped generic
`build → deliver` sweep points, most of which fire in the runner loop — `claim.` (the route-claim boundary between
persisting the route + its capability-token fact and the runner reading the plaintext token back) is the first of those
ungrouped points armed on the **hub** process instead, recovered generically by the runner's own interrupted-claim
adoption rather than a dedicated scenario. Local-only like `blizzard:e2e` — needs the sibling `blizzard-mock` worktree
and a winter source; skipped without `BLIZZARD_CRASH_SWEEP=1`. **In CI** both the `pr` and `push` workflows run the
**bounded CI profile** — `BLIZZARD_CRASH_SWEEP=1 BLIZZARD_CRASH_SWEEP_CI=1 uv run pytest -m crash_sweep tests/crash/`
(`mise run crash-sweep-ci`): one representative crash point per boundary family plus the whole-process cases and the
recovery-critical windows, ~75s on a GitHub runner, so the sweep is a real gate at bounded runtime. The subset is
intersected with the live registry and asserts each named point still exists (`bzh:crash-point-registry`), so a rename
fails loudly. The FULL sweep stays this method's documented local command (`mise run crash-sweep`) and runs in the tag
`release` workflow.

### web:client-drift

`npm run generate:client` in `web/` (openapi-ts codegen from `openapi/{hub,runner}.openapi.json`), then fail on any
unstaged diff in `web/` ([../../standards/frontend.md](../../standards/frontend.md), `bzh:generated-client`). The check
is a working-tree-vs-index `git diff`, not a working-tree-vs-`HEAD` one — a regeneration already `git add`ed passes. The
Python half regenerates the specs via `uv run blizzard-export-openapi --out-dir openapi` and fails the same way on an
unstaged diff in `openapi/`.

### web:structural-gate

`npm run structural-gate` in `web/` (`web/scripts/structural-gate.js`) — each check below is **live**:

- a `max-lines` ceiling over every Angular component file (the ~400-line cap,
  [../../architecture/frontend-structure.md](../../architecture/frontend-structure.md)
  `bzh:frontend-container-presentational`);
- a grep sweep asserting the retired chrome blocks appear only under `fleet/lib/kit/` — which classes those are is
  [../../architecture/frontend-structure.md](../../architecture/frontend-structure.md) `bzh:frontend-kit-floor`'s
  Detect, reached from the toolchain side by `bzh:frontend-kit`;
- an empty-state-without-the-kit sweep (blizzard#181,
  [../../architecture/frontend-structure.md](../../architecture/frontend-structure.md) `bzh:frontend-empty-state-gated`)
  — a component outside `fleet/lib/kit/` rendering a `*-empty` `data-testid` must also reference `fleet-kit-async-state`
  in the same file, unless named in `EMPTY_STATE_EXEMPT_FILES` alongside the one-line reason the view is reachable only
  after a parent's own triad has already resolved;
- a real-timer sweep (issue #275) over the specs the `test` target actually runs, failing a `setTimeout`/`setInterval`
  whose delay is a **non-zero integer literal** — a real second spent inside the merge gate, and a window guessed rather
  than chosen. A delay held in a variable or expression is outside the pattern; `setTimeout(…, 0)` is the
  macrotask-flush idiom and is deliberately not matched; `*.shell-sweep.spec.ts` is out of scope (a real-Chromium frame
  wait is `web:shell-sweep`'s method); a genuinely time-driven spec is named in `REAL_TIMER_EXEMPT_FILES` with its
  reason, today only `demo-director.spec.ts`, whose waits poll a real router harness at the kiosk tour's own measured
  cadence. The tree is clean of the shape today, so this check alone would pass with its detector deleted — it carries a
  fixture self-test (`assertRealTimerDetectorWorks`, must-catch and must-pass shapes including a nested call in the
  callback) that refuses to run the gate at all if the detector stops classifying them, which is what keeps it a guard
  rather than a decoration (`bzh:case-pins-its-own-name`). The remaining checks fire on real files today and need no
  equivalent.

The `max-lines` half armed in phase 3 of the WEBARCH epic (blizzard#77) once the chunk-detail decomposition (#79) and
the panel splits (#80) brought every in-scope component file under the cap. `board-shell.ts` was the one named script
exemption — over the cap but outside both #79's and #80's file lists, a standing gap rather than a silent pass — and
**#137 closed it**: extracting `board-card.ts` and `board-column.ts` as presentational children brought the file under
the cap and deleted its `MAX_LINES_EXEMPT_FILES` entry, so the `max-lines` half now covers every in-scope component file
with **no exemptions**.

### web:shell-sweep

`npm run shell-sweep` in `web/` (`web/scripts/shell-sweep.js`) — the tooled proof behind the narrow-viewport tier rule
(`bzh:narrow-viewport-tier-rule`, [tier rules](../blizzard.md#tier-rules)) for components reachable from the mobile
shell's bottom nav. jsdom (`web:unit-test`'s environment) parses `@container`/media-query rules without evaluating them
and never actually lays out or clamps text, so no jsdom spec can prove a real collapse; this method runs its specs under
`@angular/build:unit-test`'s real-browser mode instead (`--browsers=ChromiumHeadless`, backed by the
`@vitest/browser-playwright` + `playwright` dev dependencies, pinned to the same `1.61.x` release the Python
`tests/e2e/` tier already caches a Chromium build for), where layout, `@container`/media-query collapse, line-clamping,
and hit-testing are all genuine. Each spec — named `*.shell-sweep.spec.ts` and excluded from its project's default
`ng test` run (`web/angular.json`'s per-project `test.exclude`), since jsdom cannot run it — mounts a real component
tree.

`app-nav-menu.shell-sweep.spec.ts` and `local-panel-layout.shell-sweep.spec.ts` cover the app's two shared header shells
(`hub`'s `BoardHeader` + `AppNavMenu`, `local-panel`'s `LocalPanelLayout`) and, for every combination of viewport width
(1400 down to 320px, straddling every breakpoint the header declares) and — for the runner shell only, the one with a
content-dependent header width — signed-in username length (authless through 64 characters), assert the profile menu
trigger sits fully inside the viewport, `elementFromPoint` at the menu's own center hit-tests inside it, the header
itself carries no horizontal overflow, and no page error fired. Proven able to fail (issue #171): reverting
`BoardHeader`'s `.trailing` shrink fix (`flex: 0 1 auto; min-width: 0`, `board-header.ts`) reproduces the exact
off-screen-menu symptom the historical fix (issue #163) was for; restoring it passes again. The sweep's own first real
run surfaced a second, narrower instance of the same defect class — the hub shell's stat strip and trailing cluster
shared an equal flex-shrink priority, so a busy header (both spend cells shown) let the menu absorb a few px of squeeze
right above the strip's own 1150px breakpoint — closed by giving the stat strip (which already clips via
`overflow: hidden`) an outsized `flex-shrink` so it absorbs a narrowing header before the trailing cluster gives up
anything (`board-header.ts`'s `.stats` rule and its own comment).

`local-panel-mobile.shell-sweep.spec.ts` (issue #176) covers the runner's mobile chunk list — `LocalPanelMobile` →
`ChunkCard`, the component the rule actually names (`local-panel.ts`'s `mode()` mounts `LocalPanelMobile` beneath the
persistent `MobileTabBar`, the rule's "mobile shell's bottom nav"; the desktop `LocalPanelLayout` → `ChunkRow` pair
`local-panel-layout.shell-sweep.spec.ts` covers is never reached below the mobile breakpoint). It mounts a chunk card
carrying five work items and, at 390px and 320px, asserts the five per-line `-webkit-line-clamp: 2` `.wi` lines actually
stack — five distinct `getBoundingClientRect().top` values — with no horizontal overflow (`scrollWidth <= clientWidth`)
and no page error. Proven able to fail: forcing `.wi` back to `display: inline` inside a `white-space: nowrap` container
collapses all five lines onto one (`tops were 322, 322, 322, 322, 322: expected 1 to be 5`); restoring the per-line
clamp passes again.

`chunk-page-layout.shell-sweep.spec.ts` (blizzard#203) covers the hub's chunk detail page — reachable from the mobile
board's glance row, the rule's "mobile shell's bottom nav" — specifically its General tab (`ChunkGeneralTab`), whose
`@media (min-width: 720px)` grid places work item and issues in a shared left column with node history beside them. It
mounts the tab with a fixture chunk and, at 390px and 320px, asserts the work-item/issues/node-history panels genuinely
stack — three distinct `getBoundingClientRect().top` values at a common `left` — with no horizontal overflow; at 1024px
it asserts node history's `left` sits at or past the work-item column's `right` (genuinely beside it, not below), while
work item and issues keep two distinct `top`s in that shared column. Proven able to fail: moving node history's explicit
grid placement into the work-item/issues column (`grid-column: 1; grid-row: 3`) collapses the 1024px case:

```text
node history's left (8) is not beside the work-item column (right edge 508): expected 8 to be greater than or equal to 508
```

Restoring its own column passes again. The same spec's fourth case (blizzard#251) mounts a `needs_human` chunk carrying
both a runner-composed wrapped takeover command and its raw resume fallback — realistically long strings, an absolute
runtime dir and worktree path apiece. The tab's no-horizontal-overflow half is structural — `fleet-kit-panel`'s body
clips horizontally (`kit-panel.ts` `overflow-x: hidden`), so no takeover CSS can widen it — which makes the load-bearing
claim the opposite one: at 320px, each command wider than the viewport must be **reachable by scrolling its own box**
(`scrollLeft` round-trips past 0), or the panel clip silently amputates the tail of the string the operator must paste
whole — asserted for the wrapped primary and, expanded, for the raw fallback, with the tab's no-overflow guard kept
before and after. Proven able to fail on both halves: dropping `overflow-x: auto` from `.takeover .cmd` fails the
collapsed half ("wrapped command is clipped, not scrollable: expected 0 to be greater than 0"), dropping it from
`.raw-fallback .cmd` fails the expanded half the same way; restoring each passes again. The same spec's fifth case
(blizzard#248) covers the same page's Transcripts tab (`ChunkTranscriptsTab`), whose nav-beside-viewer split collapses
to a stack below `@media (min-width: 720px)`: it mounts the tab with one stubbed segment already open and, at 390px,
asserts the step nav's `top` sits above the segment body's own (genuinely stacked, not beside it) with no horizontal
overflow. Proven able to fail: forcing `.tx-tab`'s base `flex-direction` to `row` (the wide-viewport rule with no
narrow-viewport collapse) fails the stacking assertion; restoring the narrow-first default passes again.

The same spec's sixth and seventh cases (blizzard#248, `review:F1`/`F2`) cover the same tab through its **composed
chain** — `ChunkPage` → `ChunkTranscriptsContainer` → `ChunkTranscriptsTab`, routed for real via `RouterTestingHarness`
under a stand-in for `App`'s own height-capped `.layout`. They exist because the fifth case mounts the tab standalone
via `TestBed.createComponent`, which never assembles the container's own box into the chain, and so could not see either
round-2 regression. The sixth serves a 60-turn segment at 390×700 and asserts the tab's own box stays bounded by the
viewport (a definite height reached it) and that `.tx-view` is a genuine scroll container (`scrollTop` round-trips
past 0) — proven able to fail by deleting `ChunkTranscriptsContainer`'s `:host { display: contents }`:

```text
the tab's own box is unbounded (5331.125px) — the flex/height chain never reached it: expected 5331.125 to be less than or equal to 700
```

Restoring it passes again. The sixth waits on its own bounded `pumpUntil` rather than the shared `settle()` helper, and
that difference is load-bearing rather than incidental: its segment-content read is second-order — enabled only once the
*index* query has resolved and named the segment's finality — and a TanStack query enabled that late, after the app has
already reported stable once, registers a pending task Angular's zoneless stability never retires. `whenStable()` then
waits forever even though change detection has gone quiet and the DOM has rendered, which is what hung this case before.
Established by removing the gate so the read fires immediately, which makes the same case pass under `settle()`
unchanged — a one-off diagnostic, not a standing test. No layout claim is relaxed by waiting the other way — `pumpUntil`
throws if the content never renders. The seventh renders the D9 permission notice and asserts its absolutely-centered
status line centers on the **tab's** box rather than the browser viewport's — measured as which of the two centers it
sits nearer, since containment alone cannot tell them apart (the host fills the tab body, so the viewport's own center
falls inside it too) and since `.status` is a `<p>` whose un-reset user-agent top margin offsets it from either center
by a line. Proven able to fail by deleting `chunk-transcripts-tab.ts`'s own `:host { position: relative }`:

```text
status line centered on 463, nearer the viewport's center (450) than the tab's own (506.5) — it has no positioned ancestor: expected 43.5 to be less than 13
```

Restoring it passes again. That mutation is why the case is measured this way: against the containment assertion it
originally shipped with, deleting `position: relative` left all seven cases green.

`runner-view.shell-sweep.spec.ts` (blizzard#218) covers the runner registry's rate-limit pace bars (`RunnerPanelView`):
a row carrying two sampled windows (`5h`, `7d`), each rendering a stacked utilization/elapsed bar pair. At the board
right rail's own ~390px width it asserts the two bars for both windows are genuinely stacked (two distinct rows, not
overlapping) and stay within the fleet panel's own width, with no horizontal overflow and no page error — the class of
claim jsdom cannot make good on, since it lays out flex children without ever checking whether they actually clip.

`transcript-panel.shell-sweep.spec.ts` (blizzard#249) covers the runner's transcript panel (`TranscriptPanel`),
reachable from the mobile chunk-detail screen (`local-panel-mobile.spec.ts`'s `data-testid="detail-transcript"`) —
specifically its two new closed-lease-from-hub states. At 390px and 320px it mounts a truncated archived read and
asserts both the archived badge (`transcript-archived-badge`) and the truncation banner (`transcript-truncated`) render
with no horizontal overflow on either element or the panel as a whole, then mounts a hub-unreachable read
(`hub_unreachable: true`, no local answer) and asserts its degrade banner (`transcript-hub-unreachable`) renders with no
panel overflow. Proven able to fail: adding `white-space: nowrap` to `.degrade-banner` reproduces exactly that overflow
at both widths (`555 > 390`/`555 > 320`); restoring it passes again.

### blizzard:journey

`BLIZZARD_JOURNEY=1 uv run pytest -m journey tests/journey/` (`mise run journey`) — the **capstone acceptance-journey
rehearsal**: the whole MVP acceptance journey as one committed, repeatable test over **real host daemons**
(`blizzard hub host` + `blizzard runner host`, the systemd units' `ExecStart`). Five issues are filed across both
fixture repos and ingested by id; two are **grouped** into one chunk (`POST /chunks/{id}/group`) and the riskiest
**reordered** to the top (`POST /queue/reorder`) — the same board controls the operator uses. One shared
`build → review → deliver` graph drives four different journeys by reading each chunk's work item **through the hub
pass-through** (`blizzard runner work-items`) and branching on a directive in the issue body: a clean **multi-repo**
land (grouping + serial delivery, criteria 11/13), a **review-fail** loop carrying its findings asset +
`prompt_addendum` back into build (criterion 9), an **ask** that parks `waiting_on_human` and is answered with
`blizzard hub answer` (criterion 7), and a **genuine failure** that escalates to `needs_human` whose takeover command,
run **verbatim**, resumes the stuck session (criterion 6) — its `wrapped_takeover_command` shape-checked alongside,
proving what [`blizzard:e2e`'s `test_escalation_e2e`](./e2e-scenarios.md#test_escalation_e2e) cannot:
[`test_escalation_e2e`](./e2e-scenarios.md#test_escalation_e2e) already resolves its own runner's runtime directory for
real (a genuine `tmp_path`, resolved the same way), so what only the journey adds is the **process boundary** — the
command is composed by a runner running as its own spawned OS process (`blizzard runner host`'s real `ExecStart`), not
by the loop's tick function called directly inside the test process the way `test_escalation_e2e` drives it. Mid-run
**both daemons are `SIGKILL`ed and restarted** through the migrate-then-host path — the invariant checker is green the
instant after, and every chunk resumes at exactly the node the hub last recorded (the exhaustive per-boundary proof
stays `blizzard:crash-sweep`). The morning-after assertions are taken verbatim from the journey: succeeded chunks merged
to bare `main`, full history + artifacts at the hub API, the asked chunk resumed **without** takeover, nothing worked
twice (each landed file reachable from bare `main` exactly once), no environment orphaned
(`blizzard dev check-invariants` clean), and `blizzard hub status` truthful for every chunk. Local-only like
`blizzard:e2e` / `blizzard:crash-sweep` — needs the sibling provisioned `blizzard-mock` worktree and a local winter
source; skipped without `BLIZZARD_JOURNEY=1`. Deterministic (every phase gates on a latched hub state, not on timing) —
run it twice, it is green twice. The one behaviour the capstone deliberately does **not** stress is a *simultaneous*
hub-and-runner crash landing inside a build's base turn (before the commit is submitted): the reboot is timed to a
latched fleet so no chunk is mid-build, and the exhaustive single-daemon per-boundary recovery stays
`blizzard:crash-sweep`.

### blizzard-mock:unit-test

`uv run pytest` — the default suite: unit + component coverage of the mock forge (issues, PRs, real-git merges, every
lever, and — issue #179/#180 — repo and issue label routes: create/list, the 422-on-duplicate, add/remove idempotency,
and the `labels=` list-issues filter composing with `state=all`), the fixture-workspace scaffold, the mock
coding-harness engine + façades, the mock-data CLI, and the **stub OAuth IdP** (`test_idp.py` — the `blizzard-mock-idp`
oidc + github surfaces and its `/_levers` control plane, issue #92) (component tiers drive real git and a real
`winter ws init`). **The wire-parity guard** (`tests/test_wire_parity.py`, issue #277) is the mock side of
`bzh:wire-change-extends-mock`: it maps every mock-hub response model to the hub schema it mirrors and diffs the field
sets against the committed `blizzard/openapi/hub.openapi.json`, each model's deliberate omissions declared inline so a
**new** real field fails rather than passing unnoticed; requires every mirror model to be mapped or explicitly declared
unschemaed (`RouteClaimConflict`, whose real 409 body no route declares a response model for, is the one entry);
separately maps the transcript lane's five request-**body** mirrors (blizzard#246), which live in `mock_hub.api.deps`
and are invisible to the response-model sweep above — they otherwise rest their whole rename defense on being typed and
required, which `ToolCallSegmentBody.input_truncated` no longer is; diffs the batched `/events` fact vocabulary against
`blizzard/src/blizzard/wire/facts.py`'s constants, so a real-side kind the mock never learned fails here instead of
being silently rejected at runtime; and sweeps the mirror service entry points for two adjacent same-typed positional
parameters, which transpose silently at a call site. **Local-only, and fail-closed**: it reads the sibling `blizzard`
worktree (`$BLIZZARD_SOURCE` overrides the default sibling path) and *fails* rather than skipping when it cannot resolve
one — parity it never checked is not a green. `blizzard-mock` runs no CI, so this gates the local command only.
