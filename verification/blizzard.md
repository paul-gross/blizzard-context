# Verifiability matrix — blizzard (`bzh:verifiability-matrix`)

<!-- This file is an index: one row per method id, the command alone in its cell. What a method runs, asserts, and cannot see goes in its detail section, never in a row — a row that grows prose widens every row of its table. -->

Each row below is one way a skill or agent may assert a blizzard change is correct; the document conforms to the canon
concept at `winter-canon:/verifiability-matrix.md`, and method ids follow its scheme
(`winter-canon:/verifiability-matrix.md#method-identifiers`). The scopes here: `blizzard` for the app repo's Python QA
and the daemon-level tiers, `web` for the Angular workspace — its checks, and its two apps driven in a browser — and
`blizzard-mock` for the mock-fleet repo.

A row holds the id and its command. Its detail — what the command runs, asserts, and cannot see — is the
`### <method-id>` section of the file named in the line above its table; [`commands.md`](./blizzard/commands.md) routes
to every command's detail by the question a reader arrives with. Beside that detail, `./blizzard/` holds one file per
reader question:

| Spoke                                                         | Read when…                                                                                                                    |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| [`tier-rules.md`](./blizzard/tier-rules.md)                   | Choosing the proof a change owes, writing a test or store helper, managing test resources, or diagnosing a test guard refusal |
| [`service-tests.md`](./blizzard/service-tests.md)             | Writing or reviewing a Playwright service spec — fixtures, clients, isolation, waits, state, and profiles                     |
| [`markers.md`](./blizzard/markers.md)                         | A row carries a **Gap** marker, or its method does not exist yet                                                              |
| [`evidence.md`](./blizzard/evidence.md)                       | Judging whether a green run pins the behavior its name claims, or planning the claims a change owes                           |
| [`mutation-survivors.md`](./blizzard/mutation-survivors.md)   | A `blizzard:mutation` run reported survivors — sorting each into its remedy, and when one may be suppressed                   |
| [`companion-changes.md`](./blizzard/companion-changes.md)     | A hub↔runner wire surface changed — it owes a companion landing                                                               |
| [`pre-release.md`](./blizzard/pre-release.md)                 | Before pushing or reproducing a red CI job — which rows a fleet node runs, and the sweeps no local gate reaches               |
| [`acceptance-criteria.md`](./blizzard/acceptance-criteria.md) | Which method proves which MVP acceptance criterion                                                                            |
| [`gaps.md`](./blizzard/gaps.md)                               | Adding a tier, a store migration, or a keyed column, or closing, narrowing, or extending a listed gap                         |

## Commands

A command method passes when its command exits 0, except where its detail states additional evidence requirements. A
command runs from the `blizzard` repo root unless its row or the line above its table says otherwise. A `<placeholder>`
is filled by the plan that binds the row: it names the paths beside the id.

### Whole-suite runs CI owns

CI runs each of these in full on every pull request. A fleet node never runs one in full: on a shared runner host none
reliably fits a node's foreground cap, and the pull request its delivery opens is where the full run happens. A plan
binds the change to the rows in the last column instead, each scoped to what the change touches.
`bzh:ci-job-local-command` ([`pre-release.md`](./blizzard/pre-release.md)) owns the rule, and when a person working by
hand runs one of these whole. Detail: `blizzard:gate` and `blizzard:gate-full` are in
[`commands/packaging.md`](./blizzard/commands/packaging.md), and each tier is in the file that holds its scoped row.

| Method                    | Command                                                                    | A fleet node binds instead                     |
| ------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------- |
| `blizzard:gate`           | `mise run gate`                                                            | The row of each gate step the change reaches   |
| `blizzard:gate-full`      | `mise run gate-full`                                                       | The scoped row of each tier the change reaches |
| `blizzard:unit-test`      | `uv run pytest -m unit`                                                    | `blizzard:unit-test-scoped`                    |
| `blizzard:component-test` | `uv run pytest -m component`                                               | `blizzard:component-test-scoped`               |
| `blizzard:service-test`   | `mise run playwright -- --project='service-*'` and `mise run service-test` | `blizzard:service-test-scoped`                 |
| `blizzard:ui`             | `mise run ui`                                                              | `blizzard:ui-scoped`                           |
| `blizzard:crash-sweep`    | `mise run crash-sweep`                                                     | `blizzard:crash-sweep-ci`                      |

### Static checks

Each finishes in about a minute or less, so a node runs it whole. Detail:
[`commands/static.md`](./blizzard/commands/static.md); `blizzard:process-ref-lint` and `blizzard:pointer-check` are in
[`commands/packaging.md`](./blizzard/commands/packaging.md).

| Method                       | Command                                  |
| ---------------------------- | ---------------------------------------- |
| `blizzard:build`             | `uv sync`                                |
| `blizzard:format`            | `uv run ruff format --check .`           |
| `blizzard:lint`              | `uv run ruff check .`                    |
| `blizzard:typecheck`         | `uv run pyright`                         |
| `blizzard:markdown-format`   | `mise x dprint@0.55.2 -- dprint check`   |
| `blizzard:process-ref-lint`  | `mise run process-ref-lint`              |
| `blizzard:structural-gate`   | `mise run structural-gate`               |
| `blizzard:pointer-check`     | `mise run pointer-check`                 |
| `blizzard:playwright-static` | `mise run playwright-check`              |
| `blizzard:exemplar-check`    | `mise run exemplar-check`                |
| `blizzard:flag-lifecycle`    | `mise run flag-lifecycle`                |
| `blizzard:ci-workflows`      | `mise x actionlint@1.7.12 -- actionlint` |

### Test tiers

Detail: [`commands/test-tiers.md`](./blizzard/commands/test-tiers.md) routes each tier to its own file, which also holds
the tier's scoped row; `blizzard:aggregate-census` is in [`commands/static.md`](./blizzard/commands/static.md) and
`blizzard:mutation` in [`commands/mutation.md`](./blizzard/commands/mutation.md). `blizzard:sqlite-test-engine-leaks`
runs the whole default suite by design, so it is a proof run by hand, never a fleet node's row.

<!-- vale Blizzard.ProcessReference = NO -->

| Method                              | Command                                                                                                                       |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `blizzard:unit-test-scoped`         | `uv run pytest -n auto -m unit <test paths>`                                                                                  |
| `blizzard:component-test-scoped`    | `uv run pytest -n auto -m component <test paths>`                                                                             |
| `blizzard:service-test-scoped`      | `mise run playwright -- --project=<service project> <spec paths>` and `BLIZZARD_SERVICE=1 uv run pytest -n auto <test paths>` |
| `blizzard:ui-scoped`                | `mise run ui -- <spec paths>`                                                                                                 |
| `blizzard:crash-sweep-ci`           | `mise run crash-sweep-ci`                                                                                                     |
| `blizzard:harness-check`            | `mise run playwright -- --project=harness --project=harness-auth --project=harness-runner --project=harness-actions`          |
| `blizzard:aggregate-census`         | `uv run python -m tests.support.aggregate_census`                                                                             |
| `blizzard:winter-binding`           | `mise run winter-binding`                                                                                                     |
| `blizzard:mutation`                 | `mise run mutation <scope>`                                                                                                   |
| `blizzard:sqlite-test-engine-leaks` | `uv run pytest -n auto`                                                                                                       |
| `blizzard:postgres-uow-concurrency` | `uv run --extra postgres python scripts/check_hub_uow_postgres.py`                                                            |

<!-- vale Blizzard.ProcessReference = YES -->

### Contracts and sweeps

Detail: [`commands/contract-sweeps.md`](./blizzard/commands/contract-sweeps.md).

| Method                       | Command                                                           |
| ---------------------------- | ----------------------------------------------------------------- |
| `blizzard:sse-contract`      | `mise run sse-contract`                                           |
| `blizzard:cli-contract`      | `uv run pytest tests/guards/test_cli_surface_contract.py`         |
| `blizzard:config-contract`   | `uv run pytest tests/guards/test_config_contract.py`              |
| `blizzard:store-contract`    | `uv run pytest tests/component/tools/test_store_contract.py`      |
| `blizzard:trace-contract`    | `uv run pytest tests/guards/test_trace_contract.py`               |
| `blizzard:egress-contract`   | `uv run pytest tests/unit/hub/egress/test_contract.py`            |
| `blizzard:docs-references`   | `uv run pytest tests/guards/test_operator_docs.py`                |
| `blizzard:openapi-drift`     | `mise run export-openapi && git diff --exit-code -- openapi/`     |
| `blizzard:contract-drift`    | `mise run export-contracts && git diff --exit-code -- contracts/` |
| `blizzard:restatement-sweep` | `mise run restatement-check`                                      |

### Release surface, packaging, and CI

Detail: [`commands/packaging.md`](./blizzard/commands/packaging.md), which also holds `blizzard:gate` and
`blizzard:gate-full`; `blizzard:journey` is in [`commands/journey.md`](./blizzard/commands/journey.md), and
`blizzard:rehearsal` and `blizzard:store-baseline` in [`commands/rehearsal.md`](./blizzard/commands/rehearsal.md). CI
runs `blizzard:journey`, `blizzard:image-smoke`, and `blizzard:compose-smoke` on every pull request, and
`blizzard:rehearsal` and `blizzard:store-baseline` only on the changes their detail names.

| Method                      | Command                                                          |
| --------------------------- | ---------------------------------------------------------------- |
| `blizzard:compat`           | `mise run compat`                                                |
| `blizzard:change-notes`     | `mise run change-notes`                                          |
| `blizzard:journey`          | `mise run journey`                                               |
| `blizzard:rehearsal`        | `mise run rehearsal`                                             |
| `blizzard:store-baseline`   | `mise run store-baseline`                                        |
| `blizzard:wheel`            | `mise run build`                                                 |
| `blizzard:wheel-smoke`      | The serve smoke on the built wheel in a node-free venv           |
| `blizzard:image-smoke`      | `mise run image-smoke`                                           |
| `blizzard:compose-smoke`    | `mise run compose-smoke`                                         |
| `blizzard:collector-config` | `mise run collector-config-check`                                |
| `blizzard:ci`               | `gh run watch --repo paul-gross/blizzard <run-id> --exit-status` |

### Angular workspace

Every command runs in `web/`. Detail: [`commands/web.md`](./blizzard/commands/web.md) routes each method to its file.

| Method                   | Command                                                     |
| ------------------------ | ----------------------------------------------------------- |
| `web:lint`               | `npm run lint`                                              |
| `web:typecheck`          | `npm run typecheck`                                         |
| `web:unit-test`          | `npm run test`                                              |
| `web:unit-test-scoped`   | `npx ng test <project> --include='<spec glob>'`             |
| `web:structural-gate`    | `npm run structural-gate`                                   |
| `web:bundle-composition` | `npm run bundle-check`                                      |
| `web:story-render`       | `npm run story-render`                                      |
| `web:shell-sweep`        | `npm run shell-sweep`                                       |
| `web:client-drift`       | `npm run generate:client`, then `git diff --exit-code -- .` |

### blizzard-mock

Every command runs from the `blizzard-mock` repo root. Detail: [`commands/mock.md`](./blizzard/commands/mock.md).

| Method                           | Command                                                               |
| -------------------------------- | --------------------------------------------------------------------- |
| `blizzard-mock:build`            | `uv sync`                                                             |
| `blizzard-mock:format`           | `uv run ruff format --check .`                                        |
| `blizzard-mock:lint`             | `uv run ruff check .`                                                 |
| `blizzard-mock:typecheck`        | `uv run pyright`                                                      |
| `blizzard-mock:process-ref-lint` | `mise exec -- vale --output=line .`                                   |
| `blizzard-mock:unit-test`        | `uv run pytest`                                                       |
| `blizzard-mock:unit-test-scoped` | `uv run pytest <test paths>`                                          |
| `blizzard-mock:e2e`              | `uv run pytest -m e2e`                                                |
| `blizzard-mock:gate`             | `mise run gate`                                                       |
| `blizzard-mock:ci`               | `gh run watch --repo paul-gross/blizzard-mock <run-id> --exit-status` |
| `blizzard-mock:ci-workflows`     | `mise x actionlint@1.7.12 -- actionlint`                              |

## Manual testing

Manual methods are verification no single command performs. Each row's surface, setup, steps, and pass condition are its
`### <method-id>` section in the spoke for its scope: [`manual.md`](./blizzard/manual.md) for the `blizzard:` rows,
[`manual-web.md`](./blizzard/manual-web.md) for the `web:` rows, and [`manual-mock.md`](./blizzard/manual-mock.md) for
the `blizzard-mock:` rows.

`blizzard:manual-hub`, `blizzard:manual-runner`, `web:manual-board`, and `web:manual-panel` are the general exercises —
one per surface a person can drive, for a change whose behavior shows on that running surface. A change to a storied
part names `web:manual-workshop` beside the general row for its surface, since one judges the part and the other judges
the page. Every other row is a narrow probe of one named claim, and wins over the general row only where the change
under verification is to that claim — a probe whose steps merely pass through the changed surface does not.

| Method                                                    | Surface                                                                     |
| --------------------------------------------------------- | --------------------------------------------------------------------------- |
| `blizzard:manual-strict-types`                            | Repository-wide Python discovery and suppression enforcement                |
| `blizzard:manual-hub`                                     | A running hub driven by hand: its HTTP API and the operator CLI             |
| `blizzard:manual-runner`                                  | A running runner driven by hand over its HTTP API                           |
| `blizzard:manual-runner-invariants-offline`               | The stopped-host runner invariant CLI and its borrowed-engine seam          |
| `blizzard:manual-runner-ingest`                           | The stopped-host runner ingest CLI, against disposable hosts                |
| `blizzard:manual-sse-probe`                               | The live SSE wire probe: framing and timing on a real socket                |
| `blizzard:manual-standing-idp`                            | Auth-gated behavior in a browser against a standing hub and stub IdP        |
| `blizzard:manual-external-usage-probe`                    | The vendor's real OAuth-usage response shape, live against `claude`         |
| `blizzard:manual-credential-renewal`                      | A live proactive OpenAI credential renewal via `codex app-server`           |
| `blizzard:manual-retired-wire-response-vocabulary-census` | Retired subscription wire-response vocabulary left in the app repo          |
| `blizzard:manual-opencode-compatibility`                  | An OpenCode version inside either major version's admitted range, live      |
| `blizzard:manual-opencode-operator-bundle`                | A real OpenCode worker launched with an operator bundle                     |
| `blizzard:manual-opencode-compatibility-rehearsal`        | The compatibility diagnostic rehearsed offline against a CLI artifact       |
| `blizzard:manual-opencode-export-budget`                  | `opencode export`'s wall-clock cost at concurrency                          |
| `blizzard:manual-autocompact-window`                      | A declared window compacting a real Claude Code or OpenCode session         |
| `blizzard:manual-worker-deny-list`                        | A worker `permissions.deny` list closing off tools on a live harness        |
| `blizzard:manual-headless-permission-refusal`             | A headless worker's permission request, per harness and mode                |
| `blizzard:manual-claude-code-bundle`                      | An operator Claude Code bundle loaded by a real `claude`                    |
| `blizzard:manual-claude-code-harness-telemetry`           | A real `claude`'s `OTEL_*` precedence and telemetry through a runner        |
| `blizzard:manual-claude-code-tool-heartbeat`              | Whether a real `claude` heartbeats a long foreground tool                   |
| `blizzard:manual-rollback-drill`                          | The compose deployment's rollback, walked against two published tags        |
| `blizzard:manual-store-copy-rehearsal`                    | A runner directory's store rehearsed on a WAL-consistent copy               |
| `blizzard:manual-fleet-read-latency`                      | A named hub read path's latency before and after, at fleet scale            |
| `blizzard:manual-trace-backends`                          | One hub's traces fanned out to a self-hosted store and a hosted service     |
| `blizzard:manual-egress-warehouse`                        | A kept egress directory loaded into a warehouse and read in a BI tool       |
| `blizzard:manual-sweep-pass-cost`                         | One derivation `sweep()` pass's wall time, statements, and bytes            |
| `blizzard:manual-branch-protection`                       | Each protected repo's live `master` protection against its documented set   |
| `blizzard:manual-postgres-migrations`                     | The hub chain via `blizzard hub migrate` on a throwaway Postgres cluster    |
| `blizzard:manual-postgres-runner-migrations`              | The runner chain via `blizzard runner migrate --dir` on throwaway Postgres  |
| `blizzard:manual-postgres-invariants`                     | The invariant routes against a hub on a throwaway Postgres cluster          |
| `blizzard:manual-live-routine`                            | A garden routine run end to end by a real-harness runner                    |
| `blizzard:manual-live-node`                               | One packaged-graph node run by a real-harness runner                        |
| `blizzard:manual-change-notes`                            | `blizzard-change-notes` driven over a throwaway clone and tag               |
| `blizzard:manual-compat`                                  | `blizzard-compat` driven over a throwaway clone with synthetic tags         |
| `blizzard:manual-flag-lifecycle`                          | `blizzard-flag-lifecycle` driven over a throwaway clone with synthetic tags |
| `blizzard:manual-store-fold`                              | `scripts/fold_store.py` driven over a throwaway clone                       |
| `blizzard:manual-release-verify`                          | A published release proven by `scripts/verify-release.sh`                   |
| `web:manual-board`                                        | The hub board driven in a real browser against a running hub                |
| `web:manual-panel`                                        | The runner panel driven in a real browser against a running runner          |
| `web:manual-workshop`                                     | A part of the board or the panel judged on its own in the workshop          |
| `web:manual-form-adoption-census`                         | Kit input controls in app templates left off the shared forms path          |
| `blizzard-mock:manual`                                    | The winter-wired mock forge fronting a fixture workspace's bare origins     |
| `blizzard-mock:manual-seeded-board`                       | A realistic board rendered from a direct store seed                         |
| `blizzard-mock:manual-seeded-fleet`                       | A seeded runner panel beside a seeded board                                 |

## Tools

Tools are setup an agent uses to stand up the scenario a verification needs, not assertions of correctness themselves.
Detail: [`tools.md`](./blizzard/tools.md), one `### <tool-id>` section each.

| Tool                     | What it stands up                                                                       |
| ------------------------ | --------------------------------------------------------------------------------------- |
| `tool:service-up`        | `winter service up <env> --wait` — a feature env's verification stack                   |
| `tool:mock-fleet`        | The `blizzard-mock` fleet: forge, fixture workspace, mock harness and daemons, stub IdP |
| `tool:fixture-workspace` | The fixture-workspace scaffold (`blizzard-mock-fixture`): bare `file://` origins        |
| `tool:mock-data`         | The mock-data CLI (`blizzard-mock-data`), seeding a store into a known world            |
