# Every prose block has a hard budget (`bzh:prose-budget`)

Follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), at file-per-rule granularity.

## Rule

A comment or docstring block fits the cap for its host below; a block over cap is pruned, not defended — the burden of
proof sits on every line kept, never on deleting one. A docstring block counts its physical span in lines, blank lines
included; a `#` block counts its consecutive comment lines.

| Host                                    | Cap     |
| --------------------------------------- | ------- |
| Module docstring                        | 6 lines |
| Class, dataclass, or Protocol docstring | 4 lines |
| Function or method docstring            | 5 lines |
| Test docstring                          | 3 lines |
| Field, column, or constant `#` comment  | 1 line  |
| Inline `#` comment block                | 2 lines |

## Why

No author judges its own writing as too long, so without a numeric bound every keep-category of `bzh:comment-locality`
is elastic and any paragraph survives by framing itself as rationale. A hard cap turns pruning from a judgment call into
a trigger.

## Exception

A block whose owned content genuinely cannot fit moves the excess to its one prose home (`bzh:one-prose-home`) — the
seam, the pinning test, or an owning doc — and keeps a capped statement plus a pointer in place. There is no in-place
waiver.

## Scope

Binds the same trees as `bzh:comment-locality`; `blizzard-context`'s `exemplars/` files are expository teaching
artifacts and are not bound. A change is held to the caps on every block it adds or edits; the pre-existing surface is
worked down by pruning passes and the ratchet, never blocked on an incidentally-touched file. The measurable half is
`mise run prose-check` in the `blizzard` repo (`blizzard:prose-ratchet`) — a per-root growth ratchet against the
committed baseline; `check --blocks` additionally names each over-cap block as file:line.

The ratchet's only teeth are that committed number, so **re-recording it (`measure --write-baseline`) is a deliberate
act, not a step in going green.** A re-record upward is warranted only when the growth is prose **newly added code** had
to carry — a new module, guard, class, or method whose blocks are each under cap — and the change says so where it
lands. Rewriting the baseline to absorb prose grown on code that already existed reads as passing the gate while
defeating it: prune to the old number instead. The distinction is per block, not per file, so a new class in an old
module qualifies and a fuller docstring on an untouched one does not. Re-record **once**, at the tip of the work, rather
than per commit — the baseline is a generated snapshot, and several commits each re-recording it conflict on rebase by
construction.

## Detect

- Any block over its cap — `scripts/prose_density.py check --blocks` names the file and line.
- A parameter-by-parameter docstring: one paragraph per field.
- A prune that tightens wording to keep every fact — under-cap is reached by dropping content, not compressing it.

## Do

```python
Column("ordinal", Integer, nullable=False),  # authored `sessions:` position, display-only
```

## Don't

```python
# The declaration's 0-based position in the authored `sessions:` map. Order carries no
# semantics — every lookup is by name — but it is what the graph explorer renders, and
# the composite primary key above makes an index scan (name order) the natural plan for
# the by-graph read, so authored order has to be a persisted fact rather than an
# insertion-order accident to survive the round trip.
Column("ordinal", Integer, nullable=False),
```

## See also

- `bzh:comment-locality` in [`./comments.md`](./comments.md) — which facts a block may state at all; this rule bounds
  how much room stating them gets.
- `bzh:one-prose-home` in [`./one-prose-home.md`](./one-prose-home.md) — where over-cap content moves instead of being
  re-wrapped in place.
- `bzh:docstring-prose-authoring` in [`./python.md`](./python.md) — the wrap regime each tree's prose lines follow,
  which the caps count over.
