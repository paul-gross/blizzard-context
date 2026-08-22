# blizzard-mock command detail (`bzh:matrix-command-mock`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->

The mock-fleet repo's own suite, and the wire-parity guard that holds it to the real hub's schema. Read
[`../../blizzard.md`](../../blizzard.md) first for the short command and the method-id inventory;
[`../commands.md`](../commands.md) routes to every other method's detail.

### blizzard-mock:unit-test

`uv run pytest` — the default suite: unit + component coverage of the mock forge (issues, PRs, real-git merges, every
lever, and — issue #179/#180 — repo and issue label routes: create/list, the 422-on-duplicate, add/remove idempotency,
and the `labels=` list-issues filter composing with `state=all`), the fixture-workspace scaffold, the mock
coding-harness engine + façades, the mock-data CLI, and the **stub OAuth IdP** (`test_idp.py` — the `blizzard-mock-idp`
oidc + github surfaces and its `/_levers` control plane, issue #92) (component tiers drive real git and a real
`winter ws init`). **The wire-parity guard** (`tests/test_wire_parity.py`, issue #277) is the mock side of
`bzh:wire-change-extends-mock`: it maps every mock-hub response model to the hub schema it mirrors and diffs the field
sets against the committed `blizzard/openapi/hub.openapi.json`, each model's deliberate omissions declared inline so a
**new** real field fails rather than passing unnoticed; requires every mirror model to be mapped or explicitly declared
unschemaed (`RouteClaimConflict`, whose real 409 body no route declares a response model for, is the one entry);
separately maps the transcript lane's five request-**body** mirrors (blizzard#246), which live in `mock_hub.api.deps`
and are invisible to the response-model sweep above — they otherwise rest their whole rename defense on being typed and
required, which `ToolCallSegmentBody.input_truncated` no longer is; diffs the batched `/events` fact vocabulary against
`blizzard/src/blizzard/wire/facts.py`'s constants, so a real-side kind the mock never learned fails here instead of
being silently rejected at runtime; and sweeps the mirror service entry points for two adjacent same-typed positional
parameters, which transpose silently at a call site. **Local-only, and fail-closed**: it reads the sibling `blizzard`
worktree (`$BLIZZARD_SOURCE` overrides the default sibling path) and *fails* rather than skipping when it cannot resolve
one — parity it never checked is not a green. `blizzard-mock` runs no CI, so this gates the local command only.
