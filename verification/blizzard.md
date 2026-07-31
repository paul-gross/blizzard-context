# Verifiability matrix — blizzard (`bzh:verifiability-matrix`)

An inventory of the verification methods for the blizzard ecosystem — each entry one way a skill or agent may assert a blizzard change is correct.
Conforms to the canon concept at `winter-canon:/verifiability-matrix.md`.

Method ids follow the canon's scheme at `winter-canon:/verifiability-matrix.md#method-identifiers`: commands and manual methods are `<scope>:<method>` (a manual method's method name is `manual`); tools are unscoped under a flat `tool:`.
Scopes here: **`blizzard`** for the app repo's Python QA and the daemon-level tiers, **`web`** for the Angular workspace checks, **`blizzard-mock`** for the mock-fleet repo.

Every row below states a live command; none carries a Gap marker. Should a new row again precede its code, restore the bootstrap convention: state the intended command, mark **Gap (phase N)**, and drop the marker in the change that lands the method.

Bootstrap phases, referenced as `P3`–`P7` throughout the rows and spokes below: **P3** service manifests, **P4** `blizzard-mock` fleet, **P5** `blizzard` scaffold, **P6** the walking-skeleton acceptance loop, **P7** the feature build (engine completeness — review + fail cycle, escalation, heartbeats, store-and-forward, fencing; the board + fleet ops; then the running-daemon service tier and the kill-9 crash sweep, all real as of wave 4).

The MVP acceptance journey's thirteen criteria are exercised end to end by named methods: criteria 2/3/4 (exactly-once, zombie fencing, kill-9) by `blizzard:crash-sweep` + the invariant checker; 6/7/9/11/12 by `blizzard:e2e`'s scenarios and `blizzard:journey`; 1 (pass-through) by `blizzard:journey`'s every-chunk work-item read; and 13 (delivery-conflict reconcile) by the component-tier partial-land test plus `blizzard:journey`'s clean multi-repo grouped land.

**Gap.** The tag `release` workflow's full-suite tiers reuse the push-verified multi-repo setup but have not yet been exercised under a real `v*` tag.

Full per-method detail lives in three spokes, one `### <method-id>` section per row marked *(more)* below, in table order:

| Spoke | Holds |
|-------|-------|
| [./blizzard/commands.md](./blizzard/commands.md) | Full detail for the Commands table rows below, except `blizzard:e2e` |
| [./blizzard/e2e-scenarios.md](./blizzard/e2e-scenarios.md) | The standing e2e scenario registry — the single authoritative list of all sixteen `blizzard:e2e` scenarios |
| [./blizzard/tools.md](./blizzard/tools.md) | Full detail for the Tools table rows below |

## Commands

Verification that runs as a single command — exit 0 is the pass signal.

| Method | Command |
|--------|---------|
| blizzard:build | `uv sync` — install the `blizzard` project and its `dev` group (run from the repo root). |
| blizzard:lint | `uv run ruff check .` ([../standards/python.md](../standards/python.md)). |
| blizzard:format | `uv run ruff format --check .` ([../standards/python.md](../standards/python.md)). |
| blizzard:typecheck | `uv run pyright` ([../standards/python.md](../standards/python.md)). |
| blizzard:unit-test | `uv run pytest -m unit` — one class or function in isolation ([tiers](#test-tiers)). Bare `uv run pytest` runs unit + component. *(more)* |
| blizzard:component-test | `uv run pytest -m component` — a domain slice with real internal collaborators, doubles only at the seams ([tiers](#test-tiers)). *(more)* |
| blizzard:gate | `mise run gate` (`./scripts/ci-gate.sh`) — the local reproduction of the shared `gate` job. Not the full master merge gate. *(more)* |
| blizzard:wheel | `mise run build` (`./scripts/build-wheel.sh`) — builds both Angular apps, then the one wheel, node-free. `BLIZZARD_VERSION` overrides the wheel version. *(more)* |
| blizzard:wheel-smoke | The exit-criterion serve smoke on the built wheel (node-free venv) — the **P5 exit criterion**. *(more)* |
| blizzard:image-smoke | `mise run image-smoke` — builds the wheel then the hub container image and boots it on an empty data volume. Local-only. *(more)* |
| blizzard:compose-smoke | `mise run compose-smoke` — stands up the reference compose deployment against a locally-built image. Local-only. *(more)* |
| blizzard:ci | `gh run watch --repo paul-gross/blizzard <run-id> --exit-status` — watch a GitHub Actions run to completion; the authoritative remote gate. *(more)* |
| blizzard:e2e | `mise run e2e` (`BLIZZARD_E2E=1 uv run pytest tests/e2e/`) — the standing e2e smoke suite, sixteen full-stack scenarios ([registry](./blizzard/e2e-scenarios.md)). |
| blizzard:service-test | `BLIZZARD_SERVICE=1 uv run pytest tests/service/` (`mise run service-test`) — a running hub or runner's HTTP API exercised from outside. *(more)* |
| blizzard:crash-sweep | `BLIZZARD_CRASH_SWEEP=1 uv run pytest -m crash_sweep` (`mise run crash-sweep`) — the FULL kill-9 sweep over the crash-point registry ([see also](#see-also)). *(more)* |
| web:lint | `npm run lint` in `web/` — eslint over the Angular workspace, all four projects ([../standards/frontend.md](../standards/frontend.md)). |
| web:unit-test | `npm run test` in `web/` — vitest, the frontend unit/component tier over all four projects ([../standards/frontend.md](../standards/frontend.md)). |
| web:typecheck | `npm run build` in `web/` — a real AOT compile of both Angular apps, the type check `web:unit-test`'s esbuild-based vitest never performs. Run after any change adding or narrowing a required field on a shared interface, or changing an exported function/method signature — the construction sites those changes can break stay green under every other web tier. |
| web:client-drift | `npm run generate:client` in `web/`, then fail on any unstaged diff (`bzh:generated-client`). *(more)* |
| web:structural-gate | `npm run structural-gate` in `web/` — a `max-lines` ceiling, a retired-chrome-class grep sweep (`bzh:frontend-kit`), and an empty-state-without-the-kit sweep (`bzh:frontend-empty-state-gated`). *(more)* |
| web:shell-sweep | `npm run shell-sweep` in `web/` — a real-Chromium proof (`@vitest/browser-playwright`), three specs: the hub board and runner local-panel shells' shared header never lets the profile menu drift off-viewport across width × signed-in username length, plus the runner's mobile chunk list (`LocalPanelMobile` → `ChunkCard`) never lets a multi-work-item card's per-line clamp fail to stack at narrow phone widths. *(more)* |
| blizzard:journey | `BLIZZARD_JOURNEY=1 uv run pytest -m journey` (`mise run journey`) — the capstone acceptance-journey rehearsal over real host daemons. *(more)* |
| blizzard-mock:build | `uv sync` in the `blizzard-mock` repo. |
| blizzard-mock:lint | `uv run ruff check .` ([../standards/python.md](../standards/python.md)). |
| blizzard-mock:format | `uv run ruff format --check .` ([../standards/python.md](../standards/python.md)). |
| blizzard-mock:typecheck | `uv run pyright` ([../standards/python.md](../standards/python.md)). |
| blizzard-mock:unit-test | `uv run pytest` — unit + component coverage of the mock forge, fixture-workspace scaffold, mock harness, mock-data CLI, and stub OAuth IdP. *(more)* |
| blizzard-mock:e2e | `uv run pytest -m e2e` — the fleet acceptance proof: a scripted prompt lands a commit the mock forge merges to bare `main` — the **P4 exit criterion**. |

## Test tiers

Four tiers, all used — each answers a different question, and none substitutes for another.
The mocks the upper tiers bind are owned by `blizzard-mock` (P4); the tier *rules* below are the standard those tests are held to.

| Tier | Method | Scope | Tooling |
|------|--------|-------|---------|
| **Unit** | `blizzard:unit-test` | One class or function in isolation. | pytest |
| **Component** | `blizzard:component-test` | A domain slice or subsystem wired with real internal collaborators, test doubles only at the seams. | pytest |
| **Service** | `blizzard:service-test` | A running hub or runner's HTTP API exercised from outside, seams bound to the mock fleet. | pytest + HTTP |
| **E2E** | `blizzard:e2e` | The full system — hub, runner, web app — through the browser and CLI, fully local with every seam bound to the mock fleet. | pytest, driving the in-process loop + a real Chromium via Playwright (scenarios 6–8, 12–14) |

### Tier rules

- **Service and e2e tests never spend real tokens and never touch the network.** The harness seam binds a mock coding harness; the work-source and delivery seams bind the mock GitHub forge; the workspace seam binds mocks or local fixtures.
- **Real-forge worker-push is covered by dogfooding, not CI (issue #143, R6).** Since Phase 4 the worker — not the runner — pushes its branch before declaring it (`blizzard runner artifact commit`); CI's `blizzard:e2e` and `blizzard:crash-sweep` rows only ever exercise that push against the `file://` mock origins the fixture workspace mints, never a real forge. A push failure specific to a real remote (auth, a real GitHub branch-protection rule, network) is therefore a gap no CI tier closes — it is exercised only by the dogfood deployment (`workspace:/context/project/local-instance.md`), whose build transcripts already show the worker pushing to real GitHub. A documented gap, not invented around: do not add a real-forge CI tier to close it.
- **Harness session stickiness is covered by evidence, not by a tier (issue #144).** The mint-only model contract — a session's model applied where the session is minted and on no resume after it — rests on the harness *restoring* a resumed session's own model. No tier asserts the **effective** model a harness ran under: the mock façade sees argv and nothing else, so `blizzard:e2e` scenario 11's sibling asserts the **flag** (mint carries a model, resumes carry none) and stops there. What backs the underlying claim is a one-time empirical observation of Claude Code CLI 2.1.220 plus source reads of opencode 1.18.8 and codex, recorded in the issue. A stickiness regression in a future CLI would therefore run a whole mechanical lineage on the wrong model with every tier green — and each harness additionally has a *configuration* that defeats stickiness (`ANTHROPIC_MODEL` env, an opencode agent model pin, a codex `config.toml` model), which is why `docs/deployment.md` states them as deployment requirements. A documented gap, not invented around: do not add a real-token tier to close it. The companion finding is that **effort is not sticky** in the same CLI — measured, not assumed — which is why effort is reasserted on every invocation while model is not.
- **One-sided service tests use the mock counterpart.** Runner service tests run against the mock hub; hub service tests against the mock runner — edge cases come from driving the mock's levers, not from contriving the real daemon into rare states.
- **A hub↔runner wire change extends the mock counterpart and the service tier in the same change (`bzh:wire-change-extends-mock`).** `blizzard-mock`'s mock hub and mock runner are that mock counterpart — a new or changed `/api/fleet/...` route, `_drive/*` verb, or wire-visible `IHubClient`/`IHubGateway` method that lands on the real daemon but not its mock leaves the counterpart silently unserved, so the service tier that exists to catch a wire regression tests nothing new. A parity guard (`tests/service/test_parity_guard.py`) covers the two directions unevenly: it mechanically diffs `IHubClient` against the mock hub's served routes, but the mock runner's `/_drive/*` drive plane is only checked against a hardcoded declared-set snapshot that flags a grown or shrunk verb — `IHubGateway` itself is never independently diffed against a real contract. This rule is that guard's human-facing companion, and it carries more of the weight on the runner/`IHubGateway` side precisely because the guard doesn't mechanically diff it there: plan and land the mock's route or verb and the service-tier test that drives it in the same change that adds the wire surface, not as a follow-up the guard is left to chase down alone.
- **Test data is set up through the mock-data CLI and fixtures** (`tool:mock-data`), not ad-hoc SQL.
- **Tests run against sqlite.** Postgres support is a configuration concern held by staying inside SQLAlchemy's portable surface (`bzh:sql-portable`), not a second test matrix.
- **Sweep the release-only tiers before you push (`bzh:sweep-release-only-tiers`).** The `blizzard:gate` row names *which* tiers that command cannot run; this is what that blind spot actually bites. Those tiers are the only ones reading two surfaces nothing else type-checks: **board `data-testid`s and `data-*` attributes** (`tests/e2e/`) and **wire field names off a live API response** (`tests/service/`). A rename of either therefore ships green and breaks them where you will not see it. Grep before pushing, then run what the change touched:

  ```bash
  grep -rn '<old-testid>\|<old-field>' tests/e2e/ tests/service/ tests/journey/ tests/crash/ web/projects/hub/src/app/demo/
  ```

  The `demo/` directory is in that list because the tiers are no longer the only readers: the board's kiosk demo mode (`?demo=true`) steers on four board handles from **production** code — `chunk-detail`/`detail-id` and `artifacts-tab-artifact`/`artifacts-tab-artifact-key`. It fails *quietly* where a scenario fails loudly (the wait times out, the scroll is skipped, the screen holds still), so each half is pinned on the producing side: the first pair by `tests/e2e/test_board_browser_e2e.py`, the second by `web/projects/hub/src/app/board/chunk/chunk-artifacts-tab.spec.ts`. Note the second pair is unreachable by grep from the component side at all — `artifacts-tab-artifact-key` is never a literal there, only synthesized as `` `${testid()}-key` `` — which is why it has a named spec rather than a sweep.

  That grep catches a handle you **removed**. A handle you **added** breaks these tiers just as hard and the grep is blind to it: a `data-testid` is only a usable locator while exactly one component renders it, so a second component claiming an existing name makes every `get_by_test_id` for it ambiguous and the scenario dies on `strict mode violation: … resolved to 2 elements`. A new component that renders a concept an existing one already renders (the same chunk's open question, in a rail *and* in the detail dock) is the case to watch — give it its own prefixed handles. Check a new handle is unique before you add it:

  ```bash
  grep -rn 'data-testid="<new-testid>"' web/projects/   # expect exactly one component
  ```

  The browser scenarios drive the **built** bundle `blizzard hub host` serves out of `src/blizzard/static/`, never the sources. `mise run e2e` therefore `depends = ["web-build"]` — do not reach past it with a bare `pytest tests/e2e/`. The hazard is not the unbuilt tree (that fails loudly, before the first assertion); it is a bundle that is **present but stale**, which fails *quietly* — the scenario exercises the previous UI and can go **green against a layout that no longer exists**, reporting coverage of a change it never loaded. This is a rule rather than a note because the same blind spot has landed three times, most recently against a board-layout rewrite whose geometry assertion would have passed against the old layout had a second, unrelated failure not tripped first.

- **A red drift check means stage the regenerated output, not the check is noisy — never substitute `lint`/`test` for it (`bzh:drift-stage-not-route-around`).** `web:client-drift` and the OpenAPI half of `blizzard:gate` diff the working tree against the index, not against `HEAD`, so `git add` the regenerated `openapi/` and `web/` output before running the gate — an *unstaged* regeneration is what fails, not an uncommitted one. `npm run lint` and `npm run test` type-check and unit-test different surfaces; neither exercises codegen, so substituting them for a red drift step reports coverage the gate never ran and leaves the drift unguarded. This is a rule rather than a note because the same blind spot has landed at least three times in one build, once as exactly that substitution.

- **A spawned daemon's output goes to a file, never to a pipe nothing drains (`bzh:daemon-stdout-to-file`).** The tiers that run real daemons — `blizzard:crash-sweep`, `blizzard:service`, `blizzard:e2e`, `blizzard:journey` — start them with `subprocess.Popen`, and `stdout=subprocess.PIPE` on a process no one reads from is a deadlock on a timer: the daemon runs until its output fills the ~64 KiB pipe buffer, then blocks in `write` forever. It does not die, so `poll()` still says alive and the port still answers `connect`; it simply stops serving mid-tick, and every wait against it times out. Pass an append-mode file instead, which has no ceiling and leaves the log readable after a failure rather than discarded with the pipe. `tests/support.py`'s `daemon_log_sink` is that file, and every daemon-running tier spawns through it — a daemon with a runtime dir logs to `daemon.log` beside its store, the mock fleet's dirless daemons to `shared_daemon_log_dir()`. `tests/test_daemon_spawn_sink.py` fails the unit tier on any new `stdout=subprocess.PIPE`, so the rule is enforced rather than remembered. This is a rule rather than a note because the symptom points nowhere near the cause: it first surfaced as the journey's *escalate* chunk sitting in `running` — a chunk whose path touched nothing the change had altered, three assertions after the ones that had already passed on the same wedged hub. Volume is what arms it, so any change that adds daemon logging shortens the fuse on a suite that was passing; suspect this before suspecting the scenario.

- **A change to a component reachable from the mobile shell's bottom nav must be exercised at ≥1 narrow width (`bzh:narrow-viewport-tier-rule`, issue #171).** Neither `web:unit-test` (jsdom parses `@container`/media-query rules without evaluating them) nor a browser e2e scenario run at Playwright's default 1280×720 can see a layout collapse — the two defect classes this rule exists for both shipped past every other tier: the profile menu pushed off-screen at a narrow header width (issues #161/#163) and the Events grid collapsing to ~104,000px of scroll below ~640px (issues #153–155). Two methods now close it: `web:shell-sweep` proves the shared header shells (hub board, runner local panel) never lose the profile menu across a real width × signed-in-username-length sweep in a real Chromium; `tests/e2e/`'s `wide_viewport`/`narrow_viewport` fixtures (`tests/e2e/conftest.py`) give any browser scenario a real ~390px page to assert against, first used by `test_event_log_e2e.py`'s narrow-viewport Events assertion. A component with no narrow-width handling of its own (this rule's whole point) is not itself a gap to fix here — it is a gap to close with a narrow-width proof in whichever of the two methods fits the surface, the same way #171 closed the two above.
- **Mutation selection: a long-comment-defended decision is a decision to mutate, an idempotent-looking write is only provably idempotent once re-read, and a mutation claim is admissible only per-assertion (`bzh:mutation-review-selection`, issues #149/#157/#158).** Reading a diff line by line cannot tell which lines the suite actually catches a regression on — mutating a candidate line (flip a condition, drop a guard, invert a comparison) and re-running the suite is the only way to find out, but mutating every line doesn't scale, so selection matters: a decision defended by a comment long enough to argue for itself is exactly the decision easiest to silently revert, so mutate it first; and a write that looks idempotent from the code alone is only provably idempotent once the suite actually performs it twice and re-reads the resulting state — inspecting the code is not a substitute for driving the write and observing what landed. Once a mutation is run, the claim it supports is only as good as the specific assertion that caught it: "the suite fails against the pre-fix code" is a claim about the aggregate exit code, and an aggregate red can be true because an unrelated assertion tripped while the one that matters keeps passing — name the assertion that fired, not the suite's exit status, or the claim is vacuous for the case it was meant to cover (#157/#158).
- **Plan against the claims a change falsifies, not only the files it touches (`bzh:falsified-claims-grep`, issue #149).** A plan's surface inventory — which files does this change touch — answers a different question than which existing claims does this change make false: a doc statement, a comment, a field name, or a test's premise can go stale in a file the change never touches directly. Enumerate the claims the change invalidates, then grep each phrasing across the app and the harness, opening every hit rather than stopping at the first:

  ```bash
  grep -rn '<falsified phrasing>' src/ docs/ openapi/ web/
  grep -rn '<falsified phrasing>' <blizzard-context worktree>   # resolve via the workspace's `# Winter Extensions` block
  ```

  This is a rule rather than a note because four of five plan rounds on issue #149 died on exactly this miss, before the plan node derived the fix — this grep — unaided.
- **Crash correctness is an orthogonal dimension, not a fifth tier** — the kill-9 sweep (`blizzard:crash-sweep`) and its four architectural requirements are [../architecture/crash-correctness.md](../architecture/crash-correctness.md). The unit tier covers each step function's idempotency in isolation; the component tier drives steps in-process against the virtual clock; the sweep is the only piece needing real subprocesses and real signals.

## Manual testing

### blizzard:manual — the acceptance loop end-to-end
Surface: the walking skeleton — one chunk traveling ingest → acquire → mock-scripted commit → deliver → landed in a bare origin, with `done` derived from facts.
Setup: a fixture-workspace env (`tool:fixture-workspace`) with the hub, the runner, and the mock fleet bound; sqlite up via each daemon's embedded store (`tool:service-up` also brings up postgres, unused in P6).
Pass: the chunk lands in the bare origin and the hub's facts derive `done`, run fully locally with no tokens and no network.
**Automated as of P6** — this loop *is* the walking skeleton and now runs (extended in P7 wave 1 to the full `build → review → deliver` shape, joined by the review-fail-cycle and escalation scenarios, in wave 2 by the ask/answer and human-gate scenarios, and in wave 3 by the browser-driven board scenario) as the standing smoke suite `blizzard:e2e` (`mise run e2e`), which self-manages the stack; run it there rather than by hand. Two live-service ways to drive it manually: (a) `winter service up <env> --wait` (forge + hub + runner), then mint a fixture (`blizzard-mock-fixture reset --env <env>`), drop the harness fence marker in its `workspace/`, file a forge issue, and `POST /api/chunks` — the hosted runner ticks it to `done`; (b) read the `mise run e2e` source for the exact in-process sequence. The P4 precursor `blizzard-mock:e2e` still exercises the ingest-less push→PR→merge→land arc with the mock fleet alone (no `blizzard` code).

### blizzard:manual-sse-probe — the live SSE wire probe
Surface: the exact frames `GET /api/events/stream` delivers to a real subscriber — distinct from what the component tier's replay-tail read shows (an event was **recorded**, not what a subscriber actually **received**) and from `blizzard:service-test`'s live-fan-out proof (count and timing of frames, not their field-level shape).
Setup: a hub hosted on a scratch port (`blizzard hub init <dir>` then `blizzard hub host --dir <dir> --port <p>`).
Steps: (1) start the hub on the scratch port; (2) hold an SSE subscription open against `GET /api/events/stream` (`curl -N` or a streaming HTTP client) before driving the act; (3) drive each publish site over HTTP — the endpoint or CLI call behind the `broker.publish_*` call under test; (4) assert the exact frame(s) received: which optional fields a given call actually omits versus sends (an omitted `by`/`reason` on `publish_runner_changed` is not the same wire shape as one sent `null`), and that the fields present agree exactly with what the board's invalidation registry keys on for that event — no extra field, no missing one it needs (issue #151).
Pass: the received frame(s) match the expected field set exactly, omission included, for every call driven.

### blizzard:manual-rollback-drill — the compose deployment's rollback promise, run for real
Surface: `docs/rollback.md` (the `blizzard` app repo's own doc) walked verbatim against a live compose deployment (`docs/install.md`, same repo) — stop the hub, `docker compose run --rm hub blizzard-hub migrate --dir … --down <rev>` on the **still-current (new)** image (it carries the `downgrade()` steps the older image's tree never heard of), then swap to the previous image tag and bring the hub back up — proving the operator-facing procedure actually works, not just that the underlying downgrade code does.
Setup: a running compose stack (`docker compose up -d`, `packaging/docker/compose.yaml`) on at least two published image tags (or two locally-built ones), so there is a real "previous" tag to roll back to.
Pass: after the drill, the hub serves at the previous tag's version (`GET /api/health` → the older `version`) and `GET /api/ready` reports `ready: true` — the store landed at exactly the older revision, not merely "some earlier one".
The downgrade mechanism itself — that every shipped revision has a working `downgrade()` — is proven mechanically and continuously by `blizzard:unit-test`'s `tests/test_store_migrations.py::test_migrate_up_and_down`; this drill is the operator-facing procedure wrapped around that guarantee, run by hand since no CI tier stands up a real compose deployment. Run it at least once per DISTRIB slice landing (issue #191/#192); re-run whenever `docs/rollback.md`'s commands change.

### blizzard-mock:manual — the live wired-service forge over a real fixture
Surface: the winter-wired mock forge (`tool:service-up`, band `+1`) fronting a real fixture workspace's per-env bare origins — the same single git truth the daemons will bind to, exercised out of process rather than in-test.
Setup — mint a fixture at the path the forge reads (`$BZ_FORGE_REPOS_DIR = ${BLIZZARD_MOCK_SCRATCH_ROOT}/${WINTER_ENV}/origins`), then bring the stack up. Run from the workspace root:
```
BLIZZARD_MOCK_SCRATCH_ROOT=/tmp/blizzard-mock/fixtures WINTER_ENV=alpha \
  sh -c 'cd alpha/blizzard-mock && uv run blizzard-mock-fixture mint --env alpha'
winter service up alpha --wait
```
The fixture's winter source resolves by walking up from the `blizzard-mock` worktree to the workspace root — **do not pass `--winter-source $PWD`**: inside a `cd … && …` subshell `$PWD` expands *after* the `cd`, so it names the `blizzard-mock` checkout (which has no `tools/winter-cli`) and minting fails. Let the walk-up default resolve it, or set `$BLIZZARD_MOCK_WINTER_SOURCE` to the workspace root explicitly.
Pass: `curl -fs localhost:${BZ_FORGE_PORT:-4421}/healthz` returns `ok`, and `curl -fs localhost:${BZ_FORGE_PORT:-4421}/repos/blizzard/toy-api` returns `200` with `"default_branch": "main"` — the live forge fronts the minted origins. Leave services down after (`winter service down alpha`; remove the fixture with `blizzard-mock-fixture destroy --env alpha`).

## Tools

Setup an agent uses to stand up the scenario a verification needs — not assertions of correctness themselves.

Full per-tool detail for the rows marked *(more)*: [./blizzard/tools.md](./blizzard/tools.md).

| Tool | Use |
|------|-----|
| tool:service-up | `winter service up <env> --wait` — the verification stack for a feature env, port-band isolated. *(more)* |
| tool:mock-fleet | The `blizzard-mock` fleet — forge, fixture-workspace scaffold, mock harness, mock hub/runner, stub OAuth IdP; every seam real. *(more)* |
| tool:mock-data | The mock-data CLI (`blizzard-mock-data`) — seed the hub/runner stores. `reset`/`create runner` work; other verbs are stubs. *(more)* |
| tool:fixture-workspace | The fixture-workspace scaffold (`blizzard-mock-fixture`) — bare `file://` origins + a disposable winter workspace. **Built (P4).** *(more)* |

## See also

- [../architecture/crash-correctness.md](../architecture/crash-correctness.md) — the four daemon requirements the `blizzard:crash-sweep` method exercises.
