# Companion changes — what a change must land alongside (`bzh:matrix-companion-changes`)

Two surfaces go silently unserved when a change lands without its companion in the same commit: the e2e scenario
registry, and the mock counterpart a service test drives.

- **An e2e test change lands its registry entry in the same change (`bzh:e2e-change-extends-registry`).** Adding,
  renaming, or deleting a `tests/e2e/` test lands the matching entry in
  `blizzard-context:/verification/blizzard/e2e-scenarios.md` in the same change, not as a follow-up —
  `blizzard-context:registry-drift` is the mechanical companion that catches the miss.
- **A hub↔runner wire change extends the mock counterpart and the service tier in the same change
  (`bzh:wire-change-extends-mock`).** `blizzard-mock`'s mock hub and mock runner are that mock counterpart — a new or
  changed `/api/fleet/...` route, `_drive/*` verb, or wire-visible `IHubClient`/`IHubGateway` method that lands on the
  real daemon but not its mock leaves the counterpart silently unserved, so the service tier that exists to catch a wire
  regression tests nothing new. The guards below cover the directions unevenly, each reaching a different half:

  - `blizzard`'s `tests/service/test_parity_guard.py` mechanically diffs `IHubClient` against the mock hub's served
    routes.
  - The mock runner's `/_drive/*` drive plane is only checked against a hardcoded declared-set snapshot that flags a
    grown or shrunk verb — `IHubGateway` itself is never independently diffed against a real contract.
  - `blizzard-mock`'s `tests/test_wire_parity.py` (issue #277) covers the shape half from the other side, reading the
    sibling `blizzard` worktree: mirror field sets against the committed `openapi/hub.openapi.json` with each model's
    omissions declared, the batched `/events` fact vocabulary against `wire/facts.py`, and a keyword-only sweep over the
    mirror entry points. Local-only and fail-closed — an unresolvable sibling refuses a green rather than skipping. Full
    detail: [./blizzard/commands.md](./commands.md#blizzard-mockunit-test).

  This rule is those guards' human-facing companion, and it carries more of the weight on the runner/`IHubGateway` side
  precisely because neither guard mechanically diffs it there: plan and land the mock's route or verb and the
  service-tier test that drives it in the same change that adds the wire surface, not as a follow-up the guard is left
  to chase down alone.
