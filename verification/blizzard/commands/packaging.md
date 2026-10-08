# Gate, wheel, and image command detail (`bzh:matrix-command-packaging`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` headings, test-filename code spans, and `mise run` task names with their adjacent paired command spans are machine-checked — keep them verbatim, in their sections. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:gate

`mise run gate` (`./scripts/ci-gate.sh`) reproduces CI's shared `gate` job locally, the one the `pr` and `push`
workflows both call: ruff format --check, ruff check, pyright, the ast-grep structural gate
(`blizzard:structural-gate`), pytest, the OpenAPI spec-drift check, hub↔runner wire compatibility
(`blizzard:wire-compat`), then eslint, vitest, the web structural gate's sweeps (`web:structural-gate`), the
bundle-composition check (`web:bundle-composition`), and generated-client drift over `web/`. Stage regenerated
`openapi/` or `web/` client output before running it: the drift checks are a working-tree-vs-index `git diff`, so a
staged-but-uncommitted regeneration passes and an unstaged one fails (`web:client-drift`).

`mise run gate` is not the full master merge gate — it omits `blizzard:service-test` and the bounded crash-sweep CI
profile (`mise run crash-sweep-ci`); the `pr` and `push` workflows run both as separate real gate jobs, so a PR breaking
either tier still fails. `bzh:sweep-release-only-tiers` ([`../pre-push.md`](../pre-push.md)) names the surfaces this
blind spot bites. `mise run gate` runs `blizzard:process-ref-lint` as one of its own steps (`scripts/ci-gate.sh`), so a
green `blizzard:gate` already covers it; the row below exists for running the rule on its own.

### blizzard:process-ref-lint

`mise run process-ref-lint` (`vale --output=line .`) from the repo root — `styles/Blizzard/ProcessReference.yml`,
`styles/Blizzard/ChangeHistory.yml`, and `styles/Blizzard/VariantHolder.yml` against `.vale.ini`'s `[*.md]`,
`[{src,tests,scripts}/**/*.py]`, `[src/**/*.{yaml,yml}]`, and `[web/projects/**/*.{ts,css}]` sections. A process
reference (tracker, issue or PR number, review/finding id, phase, or lettered-change token) or crisp change-history
narration — the shapes `ChangeHistory.yml`'s own token list names — or a repository Protocol naming who holds its
variant (`depends on this variant`, `held by read-path edges`) is a hard failure. The generated web clients are
excluded; `.html` templates are outside the configured extensions. Other history shapes, including `used to` in
regression explanations, are not gated. `gate.yml` runs the command as its own dedicated job, installing Vale through
`jdx/mise-action`.

### blizzard:wire-compat

`mise run wire-compat` (`uv run blizzard-wire-compat --baseline merge-base --against origin/master`) fails on a breaking
change to the declared hub↔runner wire surface (`bzh:fleet-wire-additive`,
[`../../../architecture/system-shape/fleet-wire.md`](../../../architecture/system-shape/fleet-wire.md)):
`openapi/hub.openapi.json`'s `/api/fleet/*` paths, the `POST /api/runners` operation `runner init` adds a runner
through, the `/api/auth/jwks.json`/`/api/auth/authorize` federation routes, the query and path parameters of those
operations, and every component schema they reach. Walks `HEAD`'s merge-base with `origin/master` one first-parent
commit at a time, failing unless a commit the step lands carries a `!` (`bzh:fleet-wire-additive`). `gate.yml`'s
`wire-compat` job runs this only when the triggering event is `pull_request`; `push.yml`'s `wire-compat-deployed` job
runs `--baseline deployed` instead, diffing against the last commit `edge` was published from, and `dev-image` needs it.

### blizzard:wheel

`mise run build` (`./scripts/build-wheel.sh`) — the one build entrypoint: it builds both Angular apps into
`src/blizzard/static/`, builds the single wheel (`uv build --wheel`) embedding those assets plus both migration trees,
then installs it into a clean node-free venv and runs `blizzard --version` in it. `BLIZZARD_VERSION` overrides the wheel
version for dev builds and tag releases.

### blizzard:wheel-smoke

The P5 exit criterion: the serve smoke on the built wheel in a node-free venv. `blizzard hub init <dir>` (idempotent,
store migrated to head), then `blizzard hub host --dir <dir> --port <p>` serves the embedded board — `GET /` returns the
Angular `index.html`, deep routes falling back to it — and `GET /api/health` returns `200`. Then, with that hub still
serving, likewise `blizzard runner init <dir> --hub http://127.0.0.1:<p>`/`host`: init adds the runner at that hub,
which the scaffold's `auth.mode = "none"` lets it do with no sign-in, and exits non-zero, adding nothing, when no hub
answers.

### blizzard:image-smoke

`mise run image-smoke` (`./scripts/image-smoke.sh`) builds the wheel then the hub container image
(`packaging/docker/Dockerfile`) and boots it on an empty data volume, asserting what a docker-free unit test cannot: a
non-root uid, `git` on `PATH`, `import psycopg` succeeding, the store migrated to head before serving begins
(`bzh:manual-migrations` — the entrypoint orders `init`-if-absent, `migrate`, `exec host`, never folded into daemon
startup), and a live `GET /api/health` `200` plus `GET /api/ready` `ready: true`. Local-only: CI builds and pushes the
multi-arch image but never boots what it publishes. The docker-free static image contract (`USER`, the `git` install,
the migrate-before-host ordering, the `ENV` defaults, the documented mount path) is pinned at `blizzard:unit-test` in
`tests/test_container_image.py` — packaging rot fails the default gate with no docker.

### blizzard:compose-smoke

`mise run compose-smoke` (`./scripts/compose-smoke.sh`) stands up the reference compose deployment
(`packaging/docker/compose.yaml`: hub, postgres, Caddy) against a locally-built image on the localhost http-only
evaluation profile, asserting: `GET /api/ready` through the Caddy proxy port reports `ready: true`; the hub's resolved
`BZ_HUB_DB_URL` is the postgres one; and `docker compose down` without `-v` then `up` loses nothing — a durable artifact
written into the postgres volume before the restart is still readable. Local-only — no CI compose smoke, the same
pattern as `blizzard:image-smoke`. The docker-free static compose contract (every durable path a named volume, the
postgres health dependency, `trusted_proxies` matching the declared network subnet, the hub naming a postgres
`BZ_HUB_DB_URL`, and — `test_hub_has_no_published_ports_only_reachable_through_the_proxy` — the hub publishing no port
of its own) is pinned at `blizzard:unit-test` in `tests/test_compose_deployment.py`.

### blizzard:collector-config

`mise run collector-config-check` runs `otelcol-contrib validate` over `packaging/otel-collector/collector.yaml`, the
example operator collector config that fans one trace stream to two backends. The task pins `otelcol-contrib` through
mise's github backend, scoped to the task rather than the global `[tools]`, so the pin is the collector release the
config is promised valid for. Local-only: the binary is about 390 MB and `gate.yml` is network-free, so no CI job runs
it — the same pattern as `blizzard:ci-workflows`.

Falsify it by planting an unknown key in the file and observing `validate` reject it, then reverting.

### blizzard:ci

`gh run watch --repo paul-gross/blizzard <run-id> --exit-status` — watch a GitHub Actions run, the `push` merge-gate on
master or the `pr` gate, to completion, exiting non-zero on failure. This is the authoritative remote gate; the
workflows and the watch loop are documented in the `blizzard` app repo's `docs/ci.md`.

**Required checks on `master`.** The `pr.yml` checks below are the set an operator applies and verifies via
`blizzard:manual-branch-protection`:

```bash
gh api -X PUT repos/paul-gross/blizzard/branches/master/protection --input - <<'EOF'
{
  "required_status_checks": {
    "strict": false,
    "checks": [
      {"context": "gate / ruff + pyright + structural gate"},
      {"context": "gate / pytest (unit + component)"},
      {"context": "gate / OpenAPI spec drift"},
      {"context": "gate / hub↔runner wire compatibility"},
      {"context": "gate / eslint + vitest + client drift"},
      {"context": "gate / process-reference and change-history lint"},
      {"context": "upper-tiers / service tier (blizzard:service-test)"},
      {"context": "upper-tiers / kill-9 crash sweep — CI profile (blizzard:crash-sweep)"}
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
EOF
```
