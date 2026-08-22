# What a change must land alongside (`bzh:matrix-companion-changes`)

A surface can land on one side of a boundary and go silently unserved on the other. The rules below name what has to be
in the same commit for that not to happen.

## An e2e change extends the registry (`bzh:e2e-change-extends-registry`)

**Rule.** Adding, renaming, or deleting a `tests/e2e/` test lands its matching entry in the e2e scenario registry,
[`./e2e-scenarios.md`](./e2e-scenarios.md), in the same change — never as a follow-up.

**Detect.** `blizzard-context:registry-drift` is the mechanical companion that catches a missing registry entry.

## A wire change extends the mock (`bzh:wire-change-extends-mock`)

**Rule.** A hub-to-runner wire change extends the mock counterpart — `blizzard-mock`'s mock hub and mock runner — and
the service tier in the same change. A wire change means a new or changed `/api/fleet/...` route, `_drive/*` verb, or
wire-visible `IHubClient` or `IHubGateway` method.

**Why.** A wire surface that lands on the real daemon but not on its mock leaves the counterpart silently unserved, so
the service tier that exists to catch a wire regression tests nothing new.

**Detect.** `blizzard`'s `tests/service/test_parity_guard.py` mechanically diffs `IHubClient` against the mock hub's
served routes, and `blizzard-mock`'s `tests/test_wire_parity.py` covers the shape half from the other side by reading
the sibling `blizzard` worktree — its detail is at [`./commands.md`](./commands/mock.md#blizzard-mockunit-test). The
other direction has no such check: the mock runner's `/_drive/*` plane is checked only against a hardcoded declared-set
snapshot flagging a grown or shrunk verb, `IHubGateway` is never independently diffed against a real contract, and that
direction therefore rests on this rule rather than on anything mechanical.
