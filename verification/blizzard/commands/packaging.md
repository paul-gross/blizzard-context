# Gate, wheel, and image command detail (`bzh:matrix-command-packaging`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` headings, test-filename code spans, and `mise run` task names with their adjacent paired command spans are machine-checked — keep them verbatim, in their sections. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:gate

`mise run gate` (`./scripts/ci-gate.sh`) reproduces CI's shared `gate` job locally, the one the `pr` and `push`
workflows both call: ruff format --check, ruff check, pyright, the ast-grep structural gate
(`blizzard:structural-gate`), the repo-path pointer check (`blizzard:pointer-check`), pytest, the OpenAPI spec-drift
check, the contract-document drift check (`blizzard-export-contracts` and a `git diff` over `contracts/`), compatibility
against the supported releases (`blizzard:compat`), the change-note check (`mise run change-notes`, which runs
`uv run blizzard-change-notes check && uv run blizzard-change-notes owed --against origin/master`), then eslint, vitest,
the web structural gate's sweeps (`web:structural-gate`), the bundle-composition check (`web:bundle-composition`), the
story render check (`web:story-render`), and generated-client drift over `web/`. Stage regenerated `openapi/`,
`contracts/` or `web/` client output before running it: the drift checks are a working-tree-vs-index `git diff`, so a
staged-but-uncommitted regeneration passes and an unstaged one fails (`web:client-drift`).

`mise run gate` is not the full master merge gate — it omits every upper tier, which the `pr` workflow runs as separate
real gate jobs; `blizzard:gate-full` below reproduces the unconditional tiers, and `bzh:ci-job-local-command`
([`../pre-push.md`](../pre-push.md)) maps each CI job to its local command. `mise run gate` runs
`blizzard:process-ref-lint` as one of its own steps (`scripts/ci-gate.sh`), so a green `blizzard:gate` already covers
it; the row below exists for running the rule on its own.

### blizzard:gate-full

`mise run gate-full` (`./scripts/gate-full.sh`) reproduces the unconditional `pr` tiers locally: `blizzard:gate`
(`./scripts/ci-gate.sh`), then `mise run service-test`, the FULL `mise run crash-sweep`, `mise run e2e`,
`mise run journey`, `mise run image-smoke` and `mise run compose-smoke`, serially, because the smokes bind fixed ports.
A red tier does not stop the later ones: the run ends with a per-tier verdict and exits non-zero on any red.
`GATE_FULL_TIERS` narrows it to the named tiers. The conditional checks are separate: for changed store revisions run
`mise run store-baseline` (`blizzard:store-baseline`), and for a cut PR run `mise run rehearsal` (`blizzard:rehearsal`).
Both need `gh` and Postgres. The task needs everything its tiers need: the sibling `blizzard-mock` worktree, Chromium,
and a docker daemon with compose v2.

### blizzard:process-ref-lint

`mise run process-ref-lint` (`vale --output=line .`, then `tests/test_route_clause_rule.py` with Vale required) from the
repo root — `styles/Blizzard/ProcessReference.yml`, `styles/Blizzard/ChangeHistory.yml`,
`styles/Blizzard/VariantHolder.yml`, `styles/Blizzard/ShortFormPointer.yml`, and `styles/Blizzard/RouteClause.yml`
against `.vale.ini`'s `[*.md]`, `[{src,tests,scripts}/**/*.py]`, `[src/**/*.{yaml,yml}]`, and
`[web/projects/**/*.{ts,css}]` sections. A process reference (tracker, issue or PR number, review/finding id, phase, or
lettered-change token) or crisp change-history narration — the shapes `ChangeHistory.yml`'s own token list names — or a
repository Protocol naming who holds its variant (`depends on this variant`, `held by read-path edges`), or a short-form
same-repo `.py` pointer, is a hard failure; so is a `client of <METHOD> /route` clause in a `.py` file under
`src/blizzard/hub/cli/` or `src/blizzard/runner/cli/` (`RouteClause.yml`, enabled only in that section). The test module
copies its fixtures into a temp tree under the repo's real `.vale.ini` and proves both directory scopes, the clause
allowed elsewhere, and the other rules still firing; it skips when Vale is absent unless `BLIZZARD_REQUIRE_VALE=1`. The
generated web clients are excluded; `.html` templates are outside the configured extensions. That token list is the one
statement of what the gate flags. `gate.yml` runs the command as its own dedicated job, installing Vale through
`jdx/mise-action`.

### blizzard:pointer-check

`mise run pointer-check` (`uv run python scripts/repo_pointers.py check`) fails when a repo-root path named in the prose
of a tracked `.py` file under `src/`, `tests/`, `scripts/` or `exemplars/python/` is not tracked. The prose is the
docstrings and full-line comments `scripts/prose_spans.py` extracts, plus trailing inline comments; string literals are
not prose. A path is a token rooted at one of the local roots `styles/Blizzard/ShortFormPointer.yml` lists. A file
pointer resolves only to a file in `git ls-files`; a directory pointer needs a tracked descendant, so an untracked file
on disk satisfies nothing. A glob or `<placeholder>` template passes when it matches at least one tracked path.

It checks file existence only: never a `#anchor`, `::symbol` or `:line` suffix (all stripped), never Markdown,
TypeScript or YAML, and never workspace notation, a URL or another repo's path — a token preceded by `:`, `/`, `.` or a
word character is skipped. Each reviewed exception is an entry in `scripts/repo-pointers-exemptions.json`, keyed by
`file`, `symbol` and `target`, with its exact `count`, a `kind` (`illustration`, `generated` or `debt`) and a `reason`.
An occurrence above an entry's count fails, and so does a stale entry whose count is no longer reached. There is no
regenerate mode. It needs no sibling checkout, and `blizzard:gate` runs it as one of its steps, as does `gate.yml`'s
`ruff + pyright + structural gate` job.

### blizzard:compat

`mise run compat` (`uv run blizzard-compat --commits origin/master..HEAD`) holds HEAD's committed contract documents —
the OpenAPI documents, `contracts/config/`, `contracts/traces/`, `contracts/egress/`, and `contracts/store/` — to each
supported release's copy (`bzh:released-surface-additive`,
[`../../../architecture/system-shape/released-surfaces.md`](../../../architecture/system-shape/released-surfaces.md)),
the releases `src/blizzard/wire/window.toml` and the tags select. A finding the base of the range already carried is
reported as inherited and does not fail. A finding passes only where the window admits a break: deprecated in every
supported release and a commit in the range carrying `!`; or, on a `master` whose window carries `opening`, a `!` and a
breaking change note naming it. Nothing passes on a release branch (`--line release/X.Y`). A response enum's gained
value is additive against a release whose own document marks every response position reaching it open
(`x-blizzard-open`); a union's gained member never is. A finding an entry of `contracts/compat/allowances.toml` admits
passes under the state `allowance`, printed with its `because`, and a stale entry fails the run; that file's README owns
when an entry admits and when it is stale. `--json` prints every finding, with an `allowance` field, and the stale
entries under `allowances`; `--tag <version>` judges HEAD as that tag and writes `compat-breaks.json`, whose entries
carry the same field. `gate.yml`'s `compat` job (named `compatibility against supported releases`) runs it on every
trigger but a tag; `release.yml`'s job of the same name runs `--tag` before any build. `blizzard:manual-compat` drives
the tool by hand.

### blizzard:change-notes

`mise run change-notes` runs two commands. `blizzard-change-notes check` asserts every file under `changes/` is a note
in the documented format. `blizzard-change-notes owed --against <ref>` asserts the commits in
`merge-base(HEAD, <ref>)..HEAD` owe no note they do not add: a changed contract document (the compat registry's less the
store schema, plus the CLI contract) carries an added or edited unreleased note or a reasoned `Change-Note: none —`
trailer; a `!` commit and a newly breaking note owe each other, the note with an `## Upgrade` section; and a released
note changes only in its body outside the cut of its own version. Git reads only: the working tree is never consulted.
CI runs `owed` on pull requests only, against `origin/<base branch>`; a push runs `check` alone. Locally it runs against
`origin/master`, so fetch first. The OpenAPI documents have no contract-document row of their own: `blizzard:gate`'s
spec-drift check above and `owed` both hold them.

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
startup), and a live `GET /api/health` `200` plus `GET /api/ready` `ready: true`. `upper-tiers.yml` runs it as a job on
every pull request and tag; the multi-arch GHCR publish is not booted. The docker-free static image contract (`USER`,
the `git` install, the migrate-before-host ordering, the `ENV` defaults, the documented mount path) is pinned at
`blizzard:unit-test` in `tests/test_container_image.py` — packaging rot fails the default gate with no docker.

### blizzard:compose-smoke

`mise run compose-smoke` (`./scripts/compose-smoke.sh`) stands up the reference compose deployment
(`packaging/docker/compose.yaml`: hub, postgres, Caddy) against a locally-built image on the localhost http-only
evaluation profile, asserting: `GET /api/ready` through the Caddy proxy port reports `ready: true`; the hub's resolved
`BZ_HUB_DB_URL` is the postgres one; and `docker compose down` without `-v` then `up` loses nothing — a durable artifact
written into the postgres volume before the restart is still readable. `upper-tiers.yml` runs it as a job on every pull
request and tag, like `blizzard:image-smoke`. The docker-free static compose contract (every durable path a named
volume, the postgres health dependency, `trusted_proxies` matching the declared network subnet, the hub naming a
postgres `BZ_HUB_DB_URL`, and — `test_hub_has_no_published_ports_only_reachable_through_the_proxy` — the hub publishing
no port of its own) is pinned at `blizzard:unit-test` in `tests/test_compose_deployment.py`.

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

**Required checks on `master`.** The checks below are every job `pr.yml` runs for a `master` base — `line provenance`
runs only on a release-line base, so it is not among them. The jobs a pull request skips by condition (the store
baseline, the rehearsal) are required through always-running result jobs that pass when the guarded job was skipped by
its condition. The set is what an operator applies and verifies via `blizzard:manual-branch-protection`:

```bash
gh api -X PUT repos/paul-gross/blizzard/branches/master/protection --input - <<'EOF'
{
  "required_status_checks": {
    "strict": false,
    "checks": [
      {"context": "gate / ruff + pyright + structural gate"},
      {"context": "gate / pytest (unit + component)"},
      {"context": "gate / OpenAPI spec drift"},
      {"context": "gate / contract drift"},
      {"context": "gate / compatibility against supported releases"},
      {"context": "gate / change notes"},
      {"context": "gate / flag lifecycle"},
      {"context": "gate / dprint"},
      {"context": "gate / eslint + vitest + client drift"},
      {"context": "gate / exemplar check (web)"},
      {"context": "gate / process-reference and change-history lint"},
      {"context": "upper-tiers / service tier (blizzard:service-test)"},
      {"context": "upper-tiers / kill-9 crash sweep (blizzard:crash-sweep)"},
      {"context": "upper-tiers / e2e acceptance loop (blizzard:e2e)"},
      {"context": "upper-tiers / acceptance journey (blizzard:journey)"},
      {"context": "upper-tiers / hub image smoke (blizzard:image-smoke)"},
      {"context": "upper-tiers / reference compose smoke (blizzard:compose-smoke)"},
      {"context": "store baseline (blizzard:store-baseline)"},
      {"context": "upgrade rehearsal (release cut)"}
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
EOF
```
