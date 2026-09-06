# Keep every comment and docstring inside its line cap (`bzh:prose-budget`)

The room a block of code prose gets, and what to do when it overruns, in the Rule/Why/Detect/Do/Don't slot skeleton
owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Rule

A block fits the cap for its host and, over cap, is pruned rather than defended: the burden of proof sits on every line
kept, not on deleting one. Content that cannot fit moves the excess to its one prose home (`bzh:one-prose-home` in
[./one-prose-home.md](./one-prose-home.md)) — the seam, the pinning test, or an owning doc — leaving a capped statement
plus a pointer.

## Why

No author judges their own writing too long, so without a numeric bound every keep-category of `bzh:comment-locality`
stays elastic; the cap turns pruning from a judgment call into a trigger.

## Scope

Binds `blizzard/src`, `blizzard/tests`, and `blizzard-mock/src` — exactly the roots `blizzard:prose-ratchet` measures —
and no other tree: a cap is only as real as the ratchet that reports it, so `blizzard/web/projects`, which
`bzh:comment-locality` binds and the ratchet cannot parse, carries no cap until the ratchet reaches it and a baseline
for it is recorded. `blizzard-context`'s `exemplars/` files are teaching artifacts and are not bound. A change is held
to the caps on every block it adds or edits, while the pre-existing surface is worked down by pruning passes and the
ratchet, never blocking an incidentally-touched file. The distinction is per block: a new class in an old module
qualifies, a fuller docstring on an untouched one does not.

## The caps

| Block                                   | Lines |
| --------------------------------------- | ----- |
| Module docstring                        | 6     |
| Class, dataclass, or Protocol docstring | 4     |
| Function or method docstring            | 5     |
| Test docstring                          | 3     |
| Field, column, or constant `#` comment  | 1     |
| Inline `#` comment block                | 2     |

A docstring block counts its physical span in lines, blank lines included; a `#` block counts its consecutive comment
lines. Both count lines as wrapped under `bzh:docstring-prose-authoring` in [./python.md](./python.md), which owns that
regime.

## Detect

- `mise run prose-check` (`blizzard:prose-ratchet`), whose `scripts/prose_density.py check --blocks` names each over-cap
  block as `file:line`.
- A parameter-by-parameter docstring, one paragraph per field.
- A prune that tightens wording to keep every fact: under-cap is reached by dropping content, not compressing it.

## Re-recording the baseline

`prose-check` ratchets per-root growth against a committed baseline, and that committed number is the ratchet's only
teeth — so re-recording it (`measure --write-baseline`) is deliberate, never a step in going green, and warranted only
when the growth is prose newly added code had to carry — a new module, guard, class, or method, each block under cap —
and the change says so where it lands. Re-record once at the tip of the work, not per commit: the baseline is a
generated snapshot, and several re-records conflict on rebase.

## Do

```python
lease_expires_at = Column(UtcDateTime)  # When the current holder's claim lapses.
```

## Don't

```python
# The deadline the current holder's claim lapses at, set when the claim is taken and
# cleared on release; a null here means the row has never been claimed.
lease_expires_at = Column(UtcDateTime)
```

## See also

- `bzh:comment-locality` in [./comments.md](./comments.md) — which facts a block may state at all; this rule bounds the
  room they get.
