# Verifiability matrix — blizzard (`bzh:verifiability-matrix`)

Each entry below is one way a skill or agent may assert a blizzard change is correct; the document conforms to the canon
concept at `winter-canon:/verifiability-matrix.md`, and method ids follow its scheme
(`winter-canon:/verifiability-matrix.md#method-identifiers`). The scopes here: `blizzard` for the app repo's Python QA
and the daemon-level tiers, `web` for the Angular workspace checks, and `blizzard-mock` for the mock-fleet repo.

A `*(more)*` marker on a row flags that a spoke carries the row's fuller detail:
[`./blizzard/commands.md`](./blizzard/commands.md) for Commands rows — what each runs, asserts, and cannot see — and
[`./blizzard/tools.md`](./blizzard/tools.md) for Tools rows — the route when standing up the state a verification needs.
Full detail lives under `./blizzard/`, one file per reader question.

| Spoke                                                         | Read when…                                                                                                                                     |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| [`tier-rules.md`](./blizzard/tier-rules.md)                   | The tier roster, writing a test at a tier, or changing a template or component style — what each tier answers, and what a change owes as proof |
| [`e2e-scenarios.md`](./blizzard/e2e-scenarios.md)             | Adding, renaming, or reading a `blizzard:e2e` scenario — what each one proves                                                                  |
| [`markers.md`](./blizzard/markers.md)                         | A row carries a `P3`–`P7` or **Gap** marker, or its method does not exist yet                                                                  |
| [`evidence.md`](./blizzard/evidence.md)                       | Judging whether a green run actually pins the behavior its name claims, or planning the claims a change falsifies or newly owes                |
| [`companion-changes.md`](./blizzard/companion-changes.md)     | A `tests/e2e/` case or a hub↔runner wire surface changed — each owes a companion landing                                                       |
| [`pre-push.md`](./blizzard/pre-push.md)                       | Before pushing — the sweeps that stand in for what a local gate cannot reach                                                                   |
| [`acceptance-criteria.md`](./blizzard/acceptance-criteria.md) | Which method proves which MVP acceptance criterion                                                                                             |
| [`gaps.md`](./blizzard/gaps.md)                               | Tempted to add a tier for something no tier covers — what stands in for one, and why                                                           |

## Commands

A command method passes when its command exits 0.

| Method                       | Command                                                                                                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `blizzard:build`             | `uv sync` from the repo root — installs the `blizzard` project and its `dev` group                          |
| `blizzard:lint`              | `uv run ruff check .`                                                                                       |
| `blizzard:format`            | `uv run ruff format --check .`                                                                              |
| `blizzard:typecheck`         | `uv run pyright`                                                                                            |
| `blizzard:unit-test`         | `uv run pytest -m unit` — one class or function in isolation *(more)*                                       |
| `blizzard:component-test`    | `uv run pytest -m component` — a domain slice, doubles only at the seams *(more)*                           |
| `blizzard:service-test`      | `mise run service-test` — a running daemon's HTTP API driven from outside *(more)*                          |
| `blizzard:e2e`               | `mise run e2e` — the standing full-stack smoke suite                                                        |
| `blizzard:journey`           | `mise run journey` — the capstone acceptance-journey rehearsal over real host daemons *(more)*              |
| `blizzard:crash-sweep`       | `mise run crash-sweep` — the full kill-9 sweep over the crash-point registry *(more)*                       |
| `blizzard:sse-contract`      | `mise run sse-contract` — the SSE frame shape against the golden corpus `contracts/sse/` *(more)*           |
| `blizzard:cli-contract`      | `uv run pytest tests/test_cli_surface_contract.py` — the CLI command tree against `contracts/cli/` *(more)* |
| `blizzard:restatement-sweep` | `mise run restatement-check` — the one-home census *(more)*                                                 |
| `blizzard:prose-ratchet`     | `mise run prose-check` — the per-root prose ratchet                                                         |
| `blizzard:gate`              | `mise run gate` — the local reproduction of CI's shared `gate` job *(more)*                                 |
| `blizzard:ci`                | `gh run watch --repo paul-gross/blizzard <run-id> --exit-status` — the authoritative remote gate *(more)*   |
| `blizzard:wheel`             | `mise run build` — both Angular apps, then the one wheel, node-free *(more)*                                |
| `blizzard:wheel-smoke`       | The serve smoke on the built wheel in a node-free venv — the **P5 exit criterion** *(more)*                 |
| `blizzard:image-smoke`       | `mise run image-smoke` — the hub image booted on an empty data volume *(more)*                              |
| `blizzard:compose-smoke`     | `mise run compose-smoke` — the reference compose deployment on a local image *(more)*                       |
| `web:lint`                   | `npm run lint` in `web/` — eslint over the Angular workspace, including the `max-lines` ceiling *(more)*    |
| `web:typecheck`              | `npm run build` in `web/` — a real AOT compile of both Angular apps *(more)*                                |
| `web:unit-test`              | `npm run test` in `web/` — vitest, the frontend unit/component tier                                         |
| `web:structural-gate`        | `npm run structural-gate` in `web/` — the real-timer and kit-floor sweeps *(more)*                          |
| `web:shell-sweep`            | `npm run shell-sweep` in `web/` — the real-Chromium proof for what jsdom cannot evaluate *(more)*           |
| `web:client-drift`           | `npm run generate:client` in `web/`, then fail on any unstaged diff (`bzh:generated-client`) *(more)*       |
| `blizzard-mock:build`        | `uv sync` in the `blizzard-mock` repo                                                                       |
| `blizzard-mock:lint`         | `uv run ruff check .`                                                                                       |
| `blizzard-mock:format`       | `uv run ruff format --check .`                                                                              |
| `blizzard-mock:typecheck`    | `uv run pyright`                                                                                            |
| `blizzard-mock:unit-test`    | `uv run pytest` — the mock fleet's own unit + component suite, plus the wire-parity guard *(more)*          |
| `blizzard-mock:e2e`          | `uv run pytest -m e2e` — the fleet acceptance proof, and the **P4 exit criterion** *(more)*                 |

The lint, format, and typecheck rows of the `blizzard` and `blizzard-mock` scopes are governed by
[`../standards/python.md`](../standards/python.md), and `web:lint` and `web:unit-test` by
[`../standards/frontend.md`](../standards/frontend.md); the one-home census is governed by
[`../standards/one-prose-home.md`](../standards/one-prose-home.md), and the prose ratchet by
[`../standards/prose-budget.md`](../standards/prose-budget.md).
[`../architecture/crash-correctness.md`](../architecture/crash-correctness.md) owns the daemon requirements
`blizzard:crash-sweep` exercises, and `blizzard:e2e`'s scenario registry is
[`./blizzard/e2e-scenarios.md`](./blizzard/e2e-scenarios.md).

## Manual testing

Manual methods are verification no single command performs. Each row's full surface, setup, steps, and pass condition
live in [`./blizzard/manual.md`](./blizzard/manual.md) for the `blizzard:` rows and in
[`./blizzard/manual-mock.md`](./blizzard/manual-mock.md) — the live forge, the seeded board and fleet — for the
`blizzard-mock:` rows.

| Method                                   | Surface                                                                                           |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `blizzard:manual`                        | The acceptance loop end-to-end; **automated as of P6** — run it as `blizzard:e2e`, not by hand    |
| `blizzard:manual-sse-probe`              | The live SSE wire probe: framing and timing on a real socket, hub or runner, one daemon at a time |
| `blizzard:manual-standing-idp`           | Auth-gated behavior in a browser against a standing hub and stub IdP, outside any test fixture    |
| `blizzard:manual-external-usage-probe`   | The vendor's real OAuth-usage response shape, proven live against `claude`'s own `/usage`         |
| `blizzard:manual-opencode-compatibility` | OpenCode `1.18.25` with ChatGPT `5.6 Luna` at `max`, live CLI/provider compatibility diagnostic   |
| `blizzard:manual-autocompact-window`     | A declared `--autocompact` window compacting a real session, rather than the model's own maximum  |
| `blizzard:manual-worker-deny-list`       | A worker settings `permissions.deny` list actually closing off the denied tools on a live harness |
| `blizzard:manual-rollback-drill`         | The compose deployment's rollback promise, walked for real against two published image tags       |
| `blizzard:manual-fleet-read-latency`     | `GET /api/chunks` wall-clock latency, before/after a read-path change, at fleet scale             |
| `blizzard-mock:manual`                   | The winter-wired mock forge fronting a real fixture workspace's bare origins                      |
| `blizzard-mock:manual-seeded-board`      | A realistic board rendered from a direct store seed: no work source configured, no hub restart    |
| `blizzard-mock:manual-seeded-fleet`      | A seeded runner panel beside a seeded board, coherent after the daemon's first reconciling tick   |

## Tools

Tools are setup an agent uses to stand up the scenario a verification needs, not assertions of correctness themselves.

| Tool                     | What it stands up                                                                                                    |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| `tool:service-up`        | `winter service up <env> --wait` — the verification stack for a feature env, port-band isolated *(more)*             |
| `tool:mock-fleet`        | The `blizzard-mock` fleet: forge, fixture workspace, mock harness, mock hub/runner, stub IdP *(more)*                |
| `tool:fixture-workspace` | The fixture-workspace scaffold (`blizzard-mock-fixture`): bare `file://` origins plus a throwaway workspace *(more)* |
| `tool:mock-data`         | The mock-data CLI (`blizzard-mock-data`), seeding a hub or runner store into a known world *(more)*                  |
