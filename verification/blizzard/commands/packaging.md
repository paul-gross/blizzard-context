# Gate, wheel, and image command detail (`bzh:matrix-command-packaging`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->

The merge gate and the distributables it does not build — the wheel, its smoke, the image, and the CI mirror. Read
[`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to every other method's detail.

### blizzard:gate

`mise run gate` (`./scripts/ci-gate.sh`) — the local reproduction of the shared `gate` job the `pr` and `push` workflows
both call: ruff format --check + ruff check + pyright + pytest, the OpenAPI spec-drift check, then eslint + vitest + the
structural gate (`web:structural-gate`) + generated-client drift over `web/`. **Stage any regenerated `openapi/` or
`web/` client output first**: the drift checks are a working-tree-vs-index `git diff`, so a staged-but-uncommitted
regeneration passes and an unstaged one fails the gate (`web:client-drift`). It is **not** the full master merge gate:
this command does not run `blizzard:service-test` or the bounded `blizzard:crash-sweep` CI profile
(`mise run crash-sweep-ci`); the `pr` workflow runs both as separate real gate jobs alongside `gate`, the same jobs the
`push` workflow runs, so a PR that breaks either tier fails its own check before it can merge. Run both locally too
before pushing for faster feedback than waiting on CI. The `bzh:sweep-release-only-tiers` rule
([pre-push sweeps](../pre-push.md)) names which surfaces this blind spot actually bites.

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
