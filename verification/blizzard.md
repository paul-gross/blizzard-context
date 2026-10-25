# Verifiability matrix — blizzard (`bzh:verifiability-matrix`)

Each entry below is one way a skill or agent may assert a blizzard change is correct; the document conforms to the canon
concept at `winter-canon:/verifiability-matrix.md`, and method ids follow its scheme
(`winter-canon:/verifiability-matrix.md#method-identifiers`). The scopes here: `blizzard` for the app repo's Python QA
and the daemon-level tiers, `web` for the Angular workspace — its checks, and its two apps driven in a browser — and
`blizzard-mock` for the mock-fleet repo.

A `*(more)*` marker on a row flags that a spoke carries the row's fuller detail:
[`./blizzard/commands.md`](./blizzard/commands.md) for Commands rows — what each runs, asserts, and cannot see — and
[`./blizzard/tools.md`](./blizzard/tools.md) for Tools rows — the route when standing up the state a verification needs.
Full detail lives under `./blizzard/`, one file per reader question.

| Spoke                                                         | Read when…                                                                                                                                                                                                                    |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`tier-rules.md`](./blizzard/tier-rules.md)                   | Choosing the proof a change owes, placing or writing a test at a tier, or diagnosing a test's isolation-guard refusal                                                                                                         |
| [`service-tests.md`](./blizzard/service-tests.md)             | Writing or reviewing a Playwright service spec — fixtures, clients, isolation, waits, state, and profiles                                                                                                                     |
| [`e2e-scenarios.md`](./blizzard/e2e-scenarios.md)             | Adding, renaming, or reading a `blizzard:e2e` scenario — what each one proves                                                                                                                                                 |
| [`markers.md`](./blizzard/markers.md)                         | A row carries a `P3`–`P7` or **Gap** marker, or its method does not exist yet                                                                                                                                                 |
| [`evidence.md`](./blizzard/evidence.md)                       | Judging whether a green run actually pins the behavior its name claims, or planning the claims a change falsifies or newly owes                                                                                               |
| [`mutation-survivors.md`](./blizzard/mutation-survivors.md)   | A `blizzard:mutation` run reported survivors — sorting each into the class that names its remedy, and when one may be suppressed                                                                                              |
| [`companion-changes.md`](./blizzard/companion-changes.md)     | A `tests/e2e/` case or a hub↔runner wire surface changed — each owes a companion landing                                                                                                                                      |
| [`pre-push.md`](./blizzard/pre-push.md)                       | Before pushing — the sweeps that stand in for what a local gate cannot reach                                                                                                                                                  |
| [`acceptance-criteria.md`](./blizzard/acceptance-criteria.md) | Which method proves which MVP acceptance criterion                                                                                                                                                                            |
| [`gaps.md`](./blizzard/gaps.md)                               | Tempted to add a tier for something no tier covers, a change adds a store migration or a keyed column, or one closes, narrows, or extends a listed gap — what stands in for one, why, and how a change keeps the list current |

## Commands

A command method passes when its command exits 0.

| Method                           | Command                                                                                                                                                                                                                     |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `blizzard:build`                 | `uv sync` from the repo root — installs the `blizzard` project and its `dev` group                                                                                                                                          |
| `blizzard:lint`                  | `uv run ruff check .`                                                                                                                                                                                                       |
| `blizzard:format`                | `uv run ruff format --check .`                                                                                                                                                                                              |
| `blizzard:markdown-format`       | `mise x dprint@0.55.2 -- dprint check` — the markdown format gate `dprint.json` declares                                                                                                                                    |
| `blizzard:typecheck`             | `uv run pyright`                                                                                                                                                                                                            |
| `blizzard:structural-gate`       | `uv run ast-grep scan --error=unused-suppression .` then `uv run ast-grep test` — the ast-grep structural channel gate (`contracts/ast-grep/`)                                                                              |
| `blizzard:unit-test`             | `uv run pytest -m unit` — one class or function in isolation *(more)*                                                                                                                                                       |
| `blizzard:component-test`        | `uv run pytest -m component` — a domain slice, doubles only at the seams *(more)*                                                                                                                                           |
| `blizzard:service-test`          | `mise run playwright -- --project='service-*'` and `mise run service-test` — daemon HTTP behavior in Playwright, remaining Python external-tool bindings in pytest *(more)*                                                 |
| `blizzard:e2e`                   | `mise run e2e` — the standing full-stack smoke suite                                                                                                                                                                        |
| `blizzard:winter-binding`        | `mise run winter-binding` — the winter workspace provider against the real winter CLI; local-only *(more)*                                                                                                                  |
| `blizzard:journey`               | `mise run journey` — the capstone acceptance-journey rehearsal over real host daemons *(more)*                                                                                                                              |
| `blizzard:rehearsal`             | `mise run rehearsal` — each supported release's real hub and runner host upgraded to the candidate, then walked back *(more)*                                                                                               |
| `blizzard:store-baseline`        | `mise run store-baseline` — a folded baseline revision against the history it replaced, each tree on SQLite and Postgres *(more)*                                                                                           |
| `blizzard:crash-sweep`           | `mise run crash-sweep` — the full kill-9 sweep over the crash-point registry *(more)*                                                                                                                                       |
| `blizzard:sse-contract`          | `mise run sse-contract` — the SSE frame shape against the golden corpus `contracts/sse/` *(more)*                                                                                                                           |
| `blizzard:cli-contract`          | `uv run pytest tests/test_cli_surface_contract.py` — the CLI command tree against `contracts/cli/`; a change to it owes a note, held by `blizzard:change-notes` *(more)*                                                    |
| `blizzard:store-contract`        | `uv run pytest tests/test_store_contract.py` — a head-migrated store, reflected, against `contracts/store/` *(more)*                                                                                                        |
| `blizzard:config-contract`       | `uv run pytest tests/test_config_contract.py` — each daemon's config registry against `contracts/config/`; a change to it owes a note, held by `blizzard:change-notes` *(more)*                                             |
| `blizzard:trace-contract`        | `uv run pytest tests/test_trace_contract.py` — the assembled span shape against `contracts/traces/`; a change to it owes a note, held by `blizzard:change-notes` *(more)*                                                   |
| `blizzard:egress-contract`       | `uv run pytest tests/test_egress_contract.py` — the exported `steps`, `invocations` and `events` datasets and their views against `contracts/egress/`; a change to it owes a note, held by `blizzard:change-notes` *(more)* |
| `blizzard:restatement-sweep`     | `mise run restatement-check` — the one-home census *(more)*                                                                                                                                                                 |
| `blizzard:mutation`              | `mise run mutation <scope>` — scoped, resumable mutation testing over `src/blizzard` *(more)*                                                                                                                               |
| `blizzard:prose-ratchet`         | `mise run prose-check` — the per-root prose ratchet                                                                                                                                                                         |
| `blizzard:exemplar-check`        | `mise run exemplar-check` — the web exemplars under `exemplars/web/` held to the hub app's gates                                                                                                                            |
| `blizzard:gate`                  | `mise run gate` — the local reproduction of CI's shared `gate` job *(more)*                                                                                                                                                 |
| `blizzard:process-ref-lint`      | `mise run process-ref-lint` — Vale's process-reference and change-history prose gate over the surface `.vale.ini` configures *(more)*                                                                                       |
| `blizzard:compat`                | `mise run compat` — holds HEAD's committed contract documents to the supported releases (`bzh:released-surface-additive`) *(more)*                                                                                          |
| `blizzard:change-notes`          | `mise run change-notes` — `blizzard-change-notes check` (the notes against the format `changes/README.md` documents) and `owed --against origin/master` (the range adds the notes it owes) *(more)*                         |
| `blizzard:ci`                    | `gh run watch --repo paul-gross/blizzard <run-id> --exit-status` — the authoritative remote gate *(more)*                                                                                                                   |
| `blizzard:wheel`                 | `mise run build` — both Angular apps, then the one wheel, node-free *(more)*                                                                                                                                                |
| `blizzard:wheel-smoke`           | The serve smoke on the built wheel in a node-free venv — the **P5 exit criterion** *(more)*                                                                                                                                 |
| `blizzard:gate-full`             | `mise run gate-full` — the local reproduction of the unconditional pull-request tiers: the gate, then every upper tier *(more)*                                                                                             |
| `blizzard:image-smoke`           | `mise run image-smoke` — the hub image booted on an empty data volume *(more)*                                                                                                                                              |
| `blizzard:compose-smoke`         | `mise run compose-smoke` — the reference compose deployment on a local image *(more)*                                                                                                                                       |
| `blizzard:ci-workflows`          | `mise x actionlint@1.7.12 -- actionlint`                                                                                                                                                                                    |
| `blizzard:collector-config`      | `mise run collector-config-check` — the example collector config validated by the pinned `otelcol-contrib` *(more)*                                                                                                         |
| `web:lint`                       | `npm run lint` in `web/` — eslint over the Angular workspace, including the `max-lines` ceiling *(more)*                                                                                                                    |
| `web:typecheck`                  | `npm run build` in `web/` — a real AOT compile of both Angular apps *(more)*                                                                                                                                                |
| `web:unit-test`                  | `npm run test` in `web/` — vitest, the frontend unit/component tier                                                                                                                                                         |
| `web:structural-gate`            | `npm run structural-gate` in `web/` — the static sweeps `web/scripts/structural-gate.js` runs over the Angular workspace *(more)*                                                                                           |
| `web:shell-sweep`                | `npm run shell-sweep` in `web/` — the real-Chromium proof for what jsdom cannot evaluate *(more)*                                                                                                                           |
| `web:story-render`               | `npm run story-render` in `web/` — type-checks the stories, builds the workshop, and renders every story in headless Chromium *(more)*                                                                                      |
| `web:bundle-composition`         | `npm run bundle-check` in `web/` — each app's initial chunk resolved from esbuild's metafile, failing on a forbidden feature module *(more)*                                                                                |
| `web:client-drift`               | `npm run generate:client` in `web/`, then fail on any unstaged diff (`bzh:generated-client`) *(more)*                                                                                                                       |
| `blizzard-mock:build`            | `uv sync` in the `blizzard-mock` repo                                                                                                                                                                                       |
| `blizzard-mock:lint`             | `uv run ruff check .`                                                                                                                                                                                                       |
| `blizzard-mock:format`           | `uv run ruff format --check .`                                                                                                                                                                                              |
| `blizzard-mock:typecheck`        | `uv run pyright`                                                                                                                                                                                                            |
| `blizzard-mock:unit-test`        | `uv run pytest` — the mock fleet's own unit + component suite, plus the wire-parity guard *(more)*                                                                                                                          |
| `blizzard-mock:e2e`              | `uv run pytest -m e2e` — the fleet acceptance proof, and the **P4 exit criterion** *(more)*                                                                                                                                 |
| `blizzard-mock:gate`             | `mise run gate` — the local reproduction of blizzard-mock's own `gate.yml` checks, plus the process-reference Vale rule *(more)*                                                                                            |
| `blizzard-mock:process-ref-lint` | `mise exec -- vale --output=line .` — the process-reference prose gate over `.py` and `.md` *(more)*                                                                                                                        |
| `blizzard-mock:ci`               | `gh run watch --repo paul-gross/blizzard-mock <run-id> --exit-status` — the authoritative remote gate *(more)*                                                                                                              |
| `blizzard-mock:ci-workflows`     | `mise x actionlint@1.7.12 -- actionlint`                                                                                                                                                                                    |

The lint, format, and typecheck rows of the `blizzard` and `blizzard-mock` scopes are governed by
[`../standards/python.md`](../standards/python.md), and `web:lint` and `web:unit-test` by
[`../standards/frontend.md`](../standards/frontend.md); the one-home census is governed by
[`../standards/one-prose-home.md`](../standards/one-prose-home.md), the prose ratchet by
[`../standards/prose-budget.md`](../standards/prose-budget.md), and the exemplar check by
[`../exemplars/conformance.md`](../exemplars/conformance.md).
[`../architecture/crash-correctness.md`](../architecture/crash-correctness.md) owns the daemon requirements
`blizzard:crash-sweep` exercises, and `blizzard:e2e`'s scenario registry is
[`./blizzard/e2e-scenarios.md`](./blizzard/e2e-scenarios.md).

For the statement guards' tier mechanics and isolation scenarios, see
[`./blizzard/tier-rules.md`](./blizzard/tier-rules.md); their refusals belong to `bzh:tenant-scoped-store` and
`bzh:runner-scoped-store`.

`blizzard:ci-workflows` and `blizzard-mock:ci-workflows` scan `.github/workflows/` by default (run from each repo's own
root) and are local-only — neither is wired into that repo's own `gate.yml`. The Python exemplars under
`exemplars/python/` ride `blizzard:lint`, `blizzard:format`, `blizzard:typecheck`, and the pytest tiers like any other
tree, and `blizzard:exemplar-check` runs in `gate.yml` as its own job.

## Manual testing

Manual methods are verification no single command performs. Each row's full surface, setup, steps, and pass condition
live in the spoke for its scope:

- [`./blizzard/manual.md`](./blizzard/manual.md) — the `blizzard:` rows.
- [`./blizzard/manual-web.md`](./blizzard/manual-web.md) — the `web:` rows.
- [`./blizzard/manual-mock.md`](./blizzard/manual-mock.md) — the `blizzard-mock:` rows: the live forge, the seeded board
  and fleet.

`blizzard:manual-hub`, `blizzard:manual-runner`, `web:manual-board`, and `web:manual-panel` are the general exercises —
one per surface a person can drive, for a change whose behavior shows on that running surface. A change to a storied
part names `web:manual-workshop` beside the general row for its surface, since one judges the part and the other judges
the page. Every other row is a narrow probe of one named claim, and wins over the general row only where the change
under verification is to that claim — a probe whose steps merely pass through the changed surface does not.

| Method                                                    | Surface                                                                                                                                                                             |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `blizzard:manual-hub`                                     | A running hub driven by hand: its HTTP API and the operator CLI against it                                                                                                          |
| `blizzard:manual-runner`                                  | A running runner driven by hand over its HTTP API                                                                                                                                   |
| `blizzard:manual-sse-probe`                               | The live SSE wire probe: framing and timing on a real socket, hub or runner, one daemon at a time                                                                                   |
| `blizzard:manual-standing-idp`                            | Auth-gated behavior in a browser against a standing hub and stub IdP, outside any test fixture                                                                                      |
| `blizzard:manual-external-usage-probe`                    | The vendor's real OAuth-usage response shape, proven live against `claude`'s own `/usage`                                                                                           |
| `blizzard:manual-credential-renewal`                      | A live proactive OpenAI credential renewal via `codex app-server`, against a real login inside its own lead window                                                                  |
| `blizzard:manual-retired-wire-response-vocabulary-census` | Retired subscription wire-response vocabulary left behind in the app repo after a shape retirement                                                                                  |
| `blizzard:manual-opencode-compatibility`                  | An OpenCode version inside the runner's admitted range (currently `>=1.18.25,<2.0`) with ChatGPT `5.6 Luna` at `max`, live CLI/provider compatibility diagnostic                    |
| `blizzard:manual-opencode-operator-bundle`                | A real OpenCode worker launched through the production binding with an operator bundle and disposable user/project scopes                                                           |
| `blizzard:manual-opencode-compatibility-rehearsal`        | The public rehearsal procedure for the compatibility diagnostic, walked offline against an emitted CLI-surface artifact instead of a live provider                                  |
| `blizzard:manual-opencode-export-budget`                  | `opencode export`'s wall-clock cost at concurrency, against the token bound the cursor's pruning evidence sets                                                                      |
| `blizzard:manual-autocompact-window`                      | A declared `--autocompact` window compacting a real session, rather than the model's own maximum                                                                                    |
| `blizzard:manual-worker-deny-list`                        | A worker settings `permissions.deny` list actually closing off the denied tools on a live harness                                                                                   |
| `blizzard:manual-headless-permission-refusal`             | A headless worker's permission request on each harness across `normal`, `auto`, and `dangerous`: refused as a tool error or approved, never left pending                            |
| `blizzard:manual-claude-code-bundle`                      | An operator Claude Code bundle composed with the runner's wiring and loaded by a real `claude`: tools, MCP, plugins, agents, hooks, resume, subagent                                |
| `blizzard:manual-claude-code-harness-telemetry`           | A real `claude`'s settings-env precedence for `OTEL_*` names, and its metrics, logs, and traces arriving through a runner's own receivers                                           |
| `blizzard:manual-rollback-drill`                          | The compose deployment's rollback promise, walked for real against two published image tags                                                                                         |
| `blizzard:manual-store-copy-rehearsal`                    | A runner directory's store rehearsed on a WAL-consistent copy, converted to a host directory: duplicate-identity check, migrate, check invariants, downgrade and upgrade            |
| `blizzard:manual-fleet-read-latency`                      | A named hub read path's wall-clock latency, before/after a read-path change, at fleet scale                                                                                         |
| `blizzard:manual-trace-backends`                          | One hub's fleet traces fanned out by one operator collector to a self-hosted store and a hosted service, a chunk's slowest step read back in each                                   |
| `blizzard:manual-egress-warehouse`                        | A kept egress directory loaded into a warehouse and read in a BI tool: cost by node by day and the slowest station, against DuckDB over the same files                              |
| `blizzard:manual-sweep-pass-cost`                         | One derivation `sweep()` pass's wall time, statement count, and zlib bytes decompressed, steady-state                                                                               |
| `blizzard:manual-branch-protection`                       | Each protected repo's live `master` branch protection against its documented required-check set, and a fleet PR's merge-commit shape                                                |
| `blizzard:manual-postgres-migrations`                     | The hub chain driven by `blizzard hub migrate` against a throwaway local Postgres cluster: head, back to base, head again                                                           |
| `blizzard:manual-postgres-runner-migrations`              | The runner chain driven by `blizzard runner migrate --dir` against a throwaway local Postgres cluster, from the parent shape seeded off `schema.py`                                 |
| `blizzard:manual-live-routine`                            | A garden routine run end to end by a real-harness runner against an env-local hub, its lease and terminal deliveries read back                                                      |
| `blizzard:manual-live-node`                               | One packaged-graph node run by a real-harness runner against an env-local hub, its published asset and the routing it took read back                                                |
| `blizzard:manual-change-notes`                            | `blizzard-change-notes guide`, `cut`, `render`, `owed` and `mise run release-notes`, driven over a throwaway clone and tag                                                          |
| `blizzard:manual-compat`                                  | `blizzard-compat` driven over a throwaway clone with synthetic tags: each verdict, the open mark, allowances, `--json`, and `compat-breaks.json`                                    |
| `blizzard:manual-flag-lifecycle`                          | `blizzard-flag-lifecycle` driven over a throwaway clone with synthetic tags: the tombstone rules, the flip-without-note rule, and the failure when `blizzard-compat` cannot resolve |
| `blizzard:manual-store-fold`                              | `scripts/fold_store.py` driven over a throwaway clone against a published release: the baseline written, the absorbed revisions deleted, an absorbed store refused                  |
| `blizzard:manual-release-verify`                          | A published release proven by `scripts/verify-release.sh` from a machine outside GitHub's runners: image signature, attestations, attached files, install                           |
| `web:manual-board`                                        | The hub board driven in a real browser against a running hub                                                                                                                        |
| `web:manual-panel`                                        | The runner panel driven in a real browser against a running runner                                                                                                                  |
| `web:manual-workshop`                                     | A part of the board or the panel judged on its own in the workshop, in each of its states and widths                                                                                |
| `blizzard-mock:manual`                                    | The winter-wired mock forge fronting a real fixture workspace's bare origins                                                                                                        |
| `blizzard-mock:manual-seeded-board`                       | A realistic board rendered from a direct store seed: no work source configured, no hub restart                                                                                      |
| `blizzard-mock:manual-seeded-fleet`                       | A seeded runner panel beside a seeded board, coherent after the daemon's first reconciling tick                                                                                     |

## Tools

Tools are setup an agent uses to stand up the scenario a verification needs, not assertions of correctness themselves.

| Tool                     | What it stands up                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `tool:service-up`        | `winter service up <env> --wait` — the verification stack for a feature env, port-band isolated *(more)*                                         |
| `tool:mock-fleet`        | The `blizzard-mock` fleet: forge, fixture workspace, mock harness, mock hub/runner, stub IdP *(more)*                                            |
| `tool:fixture-workspace` | The fixture-workspace scaffold (`blizzard-mock-fixture`): bare `file://` origins, winter-free by default, a winter workspace on request *(more)* |
| `tool:mock-data`         | The mock-data CLI (`blizzard-mock-data`), seeding a hub or runner store into a known world *(more)*                                              |
