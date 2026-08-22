# blizzard-mock command detail (`bzh:matrix-command-mock`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `### blizzard-mock:unit-test` heading and its test-filename code spans are machine-parsed registrations — keep them verbatim. -->

Read [`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard-mock:unit-test

Bare `uv run pytest` — the default suite: unit plus component coverage of the mock forge (issues, PRs, real-git merges,
every lever), the fixture-workspace scaffold, the mock coding-harness engine and façades, the mock-data CLI, and the
stub OAuth IdP (`test_idp.py` — the `blizzard-mock-idp` oidc and github surfaces plus its `/_levers` control plane).
`blizzard-mock` runs no CI, so this method gates the local command only.

The wire-parity guard (`tests/test_wire_parity.py`), the mock side of `bzh:wire-change-extends-mock`, maps every
mock-hub response model to the hub schema it mirrors and diffs field sets against the committed
`blizzard/openapi/hub.openapi.json`; deliberate omissions are declared inline, so a new real field fails. Every mirror
model must be mapped or explicitly declared unschemaed — `RouteClaimConflict` is the one unschemaed entry. The guard
separately maps the transcript lane's request-body mirrors in `mock_hub.api.deps`, which are invisible to the
response-model sweep. It also diffs the batched `/events` fact vocabulary against
`blizzard/src/blizzard/wire/facts.py`'s constants — a kind the mock never learned fails here, not silently at runtime —
and sweeps the mirror service entry points for two adjacent same-typed positional parameters, which transpose silently.

The guard is local-only and fail-closed: it reads the sibling `blizzard` worktree (`$BLIZZARD_SOURCE` overrides the
default path) and fails rather than skips when it cannot resolve one — parity never checked is not a green.
