# What a change must land alongside (`bzh:matrix-companion-changes`)

A surface can land on one side of a boundary and go silently unserved on the other. The rules below name what has to be
in the same commit for that not to happen. Across the repo boundary, the domain statement an author-facing surface owes
is the companion that `bzh:owed-claims-landed` in [./evidence.md](./evidence.md) requires of a `blizzard` change.

## An e2e change updates the registry (`bzh:e2e-change-extends-registry`)

**Rule.** Renaming, deleting, or porting a `tests/e2e/` test lands its matching registry change in the same change —
never as a follow-up. The tier takes no new test (`bzh:service-tests-in-playwright`). A scenario's entry lives in the
spoke under [`./e2e-scenarios/`](./e2e-scenarios/) that owns the reader question it answers; the registry hub
[`./e2e-scenarios.md`](./e2e-scenarios.md) routes to it and carries no entries itself.

**Why.** The registry is what the drift check reads, so a renamed or removed scenario left behind in it turns that check
red for every change behind it, and the fix ends up written by an author who never touched the scenario.

**Detect.** `blizzard-context:registry-drift` is the mechanical companion that catches a stale registry entry.

**Don't.** A `blizzard` commit that ports an e2e scenario to a `tests/service/fleet/` spec with this message, and no
companion `blizzard-context` change under `verification/blizzard/e2e-scenarios/`:

```text
test(fleet): port the landing-order scenario

Registry entry to drop once the port settles.
```

## A wire change extends the mock (`bzh:wire-change-extends-mock`)

**Rule.** A hub-to-runner wire change extends the mock counterpart — `blizzard-mock`'s mock hub and mock runner — and
the service tier in the same change. A wire change means a new or changed `/api/fleet/...` route, `_drive/*` verb, or
wire-visible `IHubClient` or `IHubGateway` method.

**Why.** A wire surface that lands on the real daemon but not on its mock leaves the counterpart silently unserved, so
the service tier that exists to catch a wire regression tests nothing new.

**Detect.** `blizzard`'s `tests/service/test_parity_guard.py` mechanically diffs `IHubClient` against the mock hub's
served routes, and `blizzard-mock`'s `tests/test_wire_parity.py` covers the shape half from the other side by reading
the sibling `blizzard` worktree — its detail is at [`./commands.md`](./commands/mock.md#blizzard-mockunit-test). The
mock PR and master-push gates use the matching blizzard branch (falling back to the target line); a scheduled gate uses
blizzard's master. The parity check remains optional until green CI history establishes it. The other direction has no
such check: the mock runner's `/_drive/*` plane is checked only against a hardcoded declared-set snapshot flagging a
grown or shrunk verb, `IHubGateway` is never independently diffed against a real contract, and that direction therefore
rests on this rule rather than on anything mechanical. `blizzard:compat` (`bzh:released-surface-additive`) is a
different axis on the same surface — additive-vs-breaking across the hub↔runner skew window — and does not stand in for
extending the mock: a new route can be perfectly additive and still leave the mock counterpart unserved.

**Don't.** A new `/api/fleet/...` route the runner calls outside `IHubClient`, landing in `blizzard` alone — the guard
diffs only the protocol's methods, so it stays green while the service tier drives a runner against a mock that answers
the new route `404`.

## An OpenCode lever roster change extends both sides (`bzh:opencode-lever-roster-extends-both-sides`)

**Rule.** A change to `blizzard-mock`'s `opencode_surface.levers.Lever`/`CATALOG` — adding, renaming, or removing a
member — lands `blizzard`'s `_fake_binary` (`tests/service/test_opencode_compatibility_service.py`) kwarg and
name-mapping in the same change, kept 1:1 with the enum, and updates `_fake_binary`'s `len(lever_flags)` pin to match.

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
