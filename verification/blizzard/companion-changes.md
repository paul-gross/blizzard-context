# What a change must land alongside (`bzh:matrix-companion-changes`)

A surface can land on one side of a boundary and go silently unserved on the other. The rules below name what has to be
in the same commit for that not to happen. Across the repo boundary, the domain statement an author-facing surface owes
is the companion that `bzh:owed-claims-landed` in [./evidence.md](./evidence.md) requires of a `blizzard` change.

## A wire change extends the mock (`bzh:wire-change-extends-mock`)

**Rule.** A hub-to-runner wire change extends the mock counterpart — `blizzard-mock`'s mock hub and mock runner — and
the service tier in the same change. A wire change means a new or changed `/api/fleet/...` route, `_drive/*` verb, or
wire-visible `IHubClient` or `IHubGateway` method.

**Why.** A wire surface that lands on the real daemon but not on its mock leaves the counterpart silently unserved, so
the service tier that exists to catch a wire regression tests nothing new.

**Detect.** `blizzard`'s `tests/service/wire/test_parity_guard.py` mechanically diffs `IHubClient` against the mock
hub's served routes, and `blizzard-mock`'s `tests/test_wire_parity.py` covers the shape half from the other side by
reading the sibling `blizzard` worktree — its detail is at [`./commands.md`](./commands/mock.md#blizzard-mockunit-test).
The mock PR and master-push gates use the matching blizzard branch (falling back to the target line); a scheduled gate
uses blizzard's master, and the parity check is among the mock's required checks. The other direction has no such check:
the mock runner's `/_drive/*` plane is checked only against a hardcoded declared-set snapshot flagging a grown or shrunk
verb, `IHubGateway` is never independently diffed against a real contract, and that direction therefore rests on this
rule rather than on anything mechanical. `blizzard:compat` (`bzh:released-surface-additive`) is a different axis on the
same surface — additive-vs-breaking across the hub↔runner skew window — and does not stand in for extending the mock: a
new route can be perfectly additive and still leave the mock counterpart unserved.

**Do.** A new `/api/fleet/widgets` route the runner calls outside `IHubClient` lands in one change family: the route in
`blizzard`, the same route on `blizzard-mock`'s mock hub, the mock runner's `IHubGateway` call to it, and a service-tier
case that drives a runner through it.

**Don't.** A new `/api/fleet/...` route the runner calls outside `IHubClient`, landing in `blizzard` alone — the guard
diffs only the protocol's methods, so it stays green while the service tier drives a runner against a mock that answers
the new route `404`.

## An OpenCode lever roster change extends both sides (`bzh:opencode-lever-roster-extends-both-sides`)

**Rule.** A change to `blizzard-mock`'s `opencode_surface.levers.Lever`/`CATALOG` — adding, renaming, or removing a
member — lands `blizzard`'s `_fake_binary` (`tests/service/harnesses/test_opencode_compatibility_service.py`) kwarg and
name-mapping in the same change, kept 1:1 with the enum, and updates `_fake_binary`'s `len(lever_flags)` pin to match.
OpenCode 2's roster, which both of its artifacts bake, is held the same way: a change to
`opencode2_core.levers.Lever`/`CATALOG` lands the matching `_LEVERS` entry
(`tests/service/harnesses/test_opencode2_compatibility_service.py`), its `len(_LEVERS)` pin, and a service-tier case
that arms it. The OpenCode 2 proof's prompts are held the same way: a change to a prompt in `blizzard`'s
`runner/harness/opencode_v2/compatibility/script.py` lands the matching recognition in `blizzard-mock`'s
`opencode2_surface/domain/script.py`, whose `needs_blizzard` test plans every prompt when both checkouts are present.

**Why.** A member landed on one side alone drifts silently: a lever no service-tier case arms, or a kwarg naming a
retired lever. [`./gaps.md`](./gaps.md#the-cross-repo-opencode-lever-roster) owns why nothing mechanical diffs the two
rosters.

**Detect.** None — this rule is the standing check; `_fake_binary`'s count pin only catches a size mismatch, never a
same-count rename.

**Do.** One change adds the `blizzard-mock` member `Lever.NEW_MISBEHAVIOUR` and, in `blizzard`, the `_fake_binary` kwarg
`new_misbehaviour`, its `"NEW_MISBEHAVIOUR": new_misbehaviour` entry in `lever_flags`, and the bumped `len(lever_flags)`
pin.

**Don't.** A `blizzard-mock` commit adding `Lever.NEW_MISBEHAVIOUR` to the roster with no companion `blizzard` change —
the new lever emits correctly but no service-tier case ever arms it.
