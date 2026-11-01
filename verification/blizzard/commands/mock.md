# blizzard-mock command detail (`bzh:matrix-command-mock`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `### blizzard-mock:unit-test` heading and its test-filename code spans are machine-parsed registrations — keep them verbatim. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard-mock:unit-test

Bare `uv run pytest` — the default suite: unit plus component coverage of the mock forge (issues, PRs, real-git merges,
every lever), the fixture-workspace scaffold, the mock coding-harness engine and façades, the CLI-surface harness mode
and its own lever roster, the mock-data CLI, and the stub OAuth IdP (`test_idp.py` — the `blizzard-mock-idp` oidc and
github surfaces plus its `/_levers` control plane). `.github/workflows/{pr,push}.yml` run this same method, minus the
`needs_blizzard`-marked wire-parity and real-runner tests (`mise run test -- -m "not needs_blizzard"`, check name
`gate / pytest (sans needs_blizzard)`). The separate `gate / wire parity (needs_blizzard)` job checks out the resolved
blizzard commit and runs both marked modules. The bare local command stays unmarked and fail-closed.

The wire-parity guard (`tests/test_wire_parity.py`), the mock side of `bzh:wire-change-extends-mock`, maps every
mock-hub response model to the hub schema it mirrors and diffs field sets against the committed
`blizzard/openapi/hub.openapi.json`; deliberate omissions are declared inline, so a new real field fails. Every mirror
model must be mapped or explicitly declared unschemaed — `RouteClaimConflict` is the one unschemaed entry. The guard
separately maps the transcript lane's request-body mirrors in `mock_hub.api.deps`, which are invisible to the
response-model sweep. It also diffs the batched `/events` fact vocabulary against
`blizzard/src/blizzard/foundation/fact_kinds.py`'s constants — a kind the mock never learned fails here, not silently at
runtime — and sweeps the mirror service entry points for two adjacent same-typed positional parameters, which transpose
silently.

The guard is fail-closed: it reads the sibling `blizzard` worktree (`$BLIZZARD_SOURCE` overrides the default path) and
fails rather than skips when it cannot resolve one — parity never checked is not a green. The real-runner module also
uses `$BLIZZARD_RUNNER_BIN` from that checkout. `.github/actions/resolve-blizzard-ref/` selects a same-named `v*` tag,
the PR head's matching branch or its `master`/`release/X.Y` base, or `master` on a master push; other implicit events
fail. `.github/workflows/nightly.yml` passes an explicit `master` ref to the reusable gate on a schedule. The resolver
logs the selected ref and commit, and checkout pins that commit.

### blizzard-mock:e2e

`uv run pytest -m e2e` — the fleet acceptance proof and the **P4 exit criterion**: a scripted prompt lands a commit the
mock forge merges to bare `main`.

### blizzard-mock:gate

`mise run gate` (`[tasks.gate]`) runs the ordinary checks locally: ruff format --check, ruff check, pyright,
`uv run pytest -m "not needs_blizzard"`, and the process-reference Vale rule. Run `mise run test -- -m needs_blizzard`
with a synced sibling blizzard checkout for the separate parity proof. `gate.yml` runs the Vale rule as its own
dedicated job, installing it through `jdx/mise-action` the same way the `quality` job already installs mise to run
`mise run lint`/`typecheck`.

### blizzard-mock:process-ref-lint

`mise exec -- vale --output=line .` from the repo root — `styles/Blizzard/ProcessReference.yml` against `.vale.ini`'s
`[*.md]` and `[{src,tests}/**/*.py]` sections. Same token set and no-exemption-list rule as `blizzard:process-ref-lint`.

### blizzard-mock:ci

`gh run watch --repo paul-gross/blizzard-mock <run-id> --exit-status` — watch a GitHub Actions run, the `push`
merge-gate on master or the `pr` gate, to completion, exiting non-zero on failure. Both include the parity job; the
scheduled `nightly` caller proves against blizzard's `master`. The real-to-mock parity guard covers `IHubClient` routes,
and the mock-to-real guard covers declared response and event shapes; the mock runner's `/_drive/*` contract and
`IHubGateway` still have no independent cross-repo diff.

**Required checks on `master`.** The four `pr.yml` checks below are the set an operator applies and verifies via
`blizzard:manual-branch-protection`:

```bash
gh api -X PUT repos/paul-gross/blizzard-mock/branches/master/protection --input - <<'EOF'
{
  "required_status_checks": {
    "strict": false,
    "checks": [
      {"context": "gate / ruff + pyright"},
      {"context": "gate / pytest (sans needs_blizzard)"},
      {"context": "gate / process-reference lint"},
      {"context": "gate / wire parity (needs_blizzard)"}
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
EOF
```
