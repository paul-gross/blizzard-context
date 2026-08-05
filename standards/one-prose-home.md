# One prose home per fact (`bzh:one-prose-home`)

Follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), at file-per-rule granularity.

## Rule

Every fact stated in code prose has exactly one home site; every other mention is a one-line pointer naming the home and carrying none of its content.
The home is assigned by the fact's kind, never chosen per site:

| Fact | Home |
|------|------|
| A boundary contract | The seam that defines the boundary — the Protocol, wire model, or schema |
| A defended decision | The pinning test that fails on revert (`bzh:mutation-review-selection`), in its docstring |
| A local invariant | The module that owns the state |
| Wire-field semantics | The wire dataclass — it generates into `openapi/` |

## Why

This is `canon:one-owner` applied to code prose: a fact explained in two files drifts into two versions, and a reader cannot tell which one the code obeys.

## Scope

Binds the same trees as `bzh:comment-locality`.

## Detect

- The same issue number *explained* — not merely cited — in more than one file.
- A contract narrated at both the seam and an implementation, or at both a schema column and its domain reader.
- A pointer that also summarizes what it points at: a pointer names the owner, it never précises the content.

## Do

```python
# Mint-only model application: see IHarnessAdapter.spawn.
```

## Don't

```python
# Model is applied at mint only — a resume passes no model flag and leans on the
# harness restoring the session's own (the same contract IHarnessAdapter.spawn states).
```

## See also

- `canon:one-owner` in `winter-canon:/principles.md` — the one-canonical-owner principle this rule instantiates for code prose.
- `bzh:comment-locality` in [`./comments.md`](./comments.md) — the pointer-at-the-owner keep-shape this rule's pointers follow.
- `bzh:comment-encapsulation` in [`./comment-encapsulation.md`](./comment-encapsulation.md) — a fact's home also determines whose vocabulary states it.
