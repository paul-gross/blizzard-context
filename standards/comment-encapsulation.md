# Code prose respects the code's own boundaries (`bzh:comment-encapsulation`)

Follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), at file-per-rule granularity.

## Rule

A docstring or comment on a boundary — a Protocol, an interface dataclass, a wire model, a store schema — states the
obligation at that boundary in the boundary's own vocabulary: parameters, return, error contract, invariants. It never
names a party on the other side of that boundary: no concrete caller, no loop step, no CLI or UI surface, no sibling or
concrete implementation. The discipline is symmetric — an implementation never re-explains the seam contract it
implements, and a caller never explains its callee; each side gets at most a bare pointer across the boundary. The
mechanical filter: prose naming a symbol its module does not import — or naming a module that imports this one — is
narrating across a boundary.

## Why

Prose that names a cross-boundary party couples the boundary's text to that party's implementation — the exact
dependency the code's layering (`bzh:dependency-inversion`) forbids — and every change on the far side stales it
silently. A seam whose docstrings enumerate their consumers also stops reading as a contract: the next implementer or
caller inherits one consumer's specifics as if they were obligations.

## Exception

A bare pointer at the owning party — a name or path on one line, carrying none of the owner's content
(`bzh:one-prose-home`).

## Scope

Binds the same trees as `bzh:comment-locality`; `blizzard-context`'s `exemplars/` files are expository teaching
artifacts and are not bound. Where that rule bounds *which facts* code prose may state, this rule bounds *whose
vocabulary* an owned fact is stated in: a seam owns its contract, but the contract must be expressible without naming
who is on the other side.

## Detect

- In a Protocol, wire-model, or schema docstring: the name of a concrete caller, a loop step, a CLI or UI surface, or a
  sibling adapter — followed by what that party does with this code.
- Prose naming a symbol the module neither defines nor imports, or naming a module that imports this one.
- The fix: delete the cross-boundary clause, or reduce it to a pointer at the party that owns the fact. A contract
  restated on *both* sides of a seam is `bzh:one-prose-home`'s signature — cite that id.

## Do

```python
def resolve_model(self, preferences: Sequence[str]) -> str:
    """Resolve a preference list to a native model name: left-to-right, first
    resolvable entry wins; an unresolvable entry is skipped, never an error;
    an empty or fully-unresolvable list falls back to the adapter default."""
```

## Don't

```python
def resolve_model(self, preferences: Sequence[str]) -> str:
    """The seam that keeps the hub and graph YAML harness-agnostic: the loop
    hands an ordered list of opaque preference strings, and a codex runner is
    expected to skip ``opus``; FILL surfaces what was skipped. ..."""
```

## See also

- `bzh:comment-locality` in [`./comments.md`](./comments.md) — state only facts your code owns; this rule additionally
  holds an owned fact to its host's altitude.
- `bzh:one-prose-home` in [`./one-prose-home.md`](./one-prose-home.md) — where the fact's one full statement lives, and
  what a pointer may carry.
- `bzh:dependency-inversion` in [`../architecture/clean-architecture.md`](../architecture/clean-architecture.md) — the
  code-layering rule whose arrows this rule makes prose obey.
