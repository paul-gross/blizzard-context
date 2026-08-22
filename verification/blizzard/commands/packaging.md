# Gate, wheel, and image command detail (`bzh:matrix-command-packaging`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` headings, test-filename code spans, and `mise run` task names with their adjacent paired command spans are machine-checked — keep them verbatim, in their sections. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:gate

`mise run gate` (`./scripts/ci-gate.sh`) reproduces CI's shared `gate` job locally, the one the `pr` and `push`
workflows both call: ruff format --check, ruff check, pyright, pytest, the OpenAPI spec-drift check, then eslint,
vitest, the structural gate (`web:structural-gate`), and generated-client drift over `web/`. Stage regenerated
`openapi/` or `web/` client output before running it: the drift checks are a working-tree-vs-index `git diff`, so a
staged-but-uncommitted regeneration passes and an unstaged one fails (`web:client-drift`).

`mise run gate` is not the full master merge gate — it omits `blizzard:service-test` and the bounded crash-sweep CI
profile (`mise run crash-sweep-ci`); the `pr` and `push` workflows run both as separate real gate jobs, so a PR breaking
either tier still fails. `bzh:sweep-release-only-tiers` ([`../pre-push.md`](../pre-push.md)) names the surfaces this
blind spot bites.

### blizzard:wheel

`mise run build` (`./scripts/build-wheel.sh`) — the one build entrypoint: it builds both Angular apps into
`src/blizzard/static/{hub,runner}`, builds the single wheel (`uv build --wheel`) embedding those assets plus both
migration trees, then installs it into a clean node-free venv and runs `blizzard --version` in it. `BLIZZARD_VERSION`
overrides the wheel version for dev builds and tag releases.

### blizzard:wheel-smoke

The P5 exit criterion: the serve smoke on the built wheel in a node-free venv. `blizzard hub init <dir>` (idempotent,
store migrated to head), then `blizzard hub host --dir <dir> --port <p>` serves the embedded board — `GET /` returns the
Angular `index.html`, deep routes falling back to it — and `GET /api/health` returns `200`; likewise
`blizzard runner init`/`host`.

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

### blizzard:ci

`gh run watch --repo paul-gross/blizzard <run-id> --exit-status` — watch a GitHub Actions run, the `push` merge-gate on
master or the `pr` gate, to completion, exiting non-zero on failure. This is the authoritative remote gate; the
workflows and the watch loop are documented in the `blizzard` app repo's `docs/ci.md`.
