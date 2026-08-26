# Comment only what the code beside it owns (`bzh:comment-locality`)

Which facts a `#` comment or docstring may state, in the Rule/Why/Detect/Do/Don't slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Rule

A comment or docstring states only facts the code beside it owns — what this line, function, or module does, and why it
is there. What a block may state is a closed, exhaustive set:

- why-this-here rationale for the adjacent code;
- a local invariant the code cannot express;
- a safety warning tied to the adjacent line;
- an issue or decision citation;
- a bare pointer at the fact's owner;
- a wire model's field semantics, scoped to the field's own meaning.

Delete prose that narrates another module's, component's, or repo's behavior, restates an invariant owned elsewhere,
paraphrases the code beside it, or narrates change history. A citation rides a one-line fact and never licenses a
paragraph, and a test docstring claims no production behavior beyond what that test's own assertions pin.

A comment defending a decision is converted, not kept: the decision earns a pinning test if it lacks one, and the
comment shrinks to a pointer at that test or at the owning doc — the pointer replacing the argument rather than riding
alongside it. Alternative-rebuttal prose goes with the argument; any defence the choice still needs belongs in the
pinning test's docstring.

## Why

Comment density replicates — an agent matches the density of the file it edits — so every violation left standing seeds
more. Cross-module narration couples one module's text to another's implementation, stales on every change there, and no
test notices.

## Scope

Binds `#` comments and docstrings across `blizzard/src`, `blizzard/tests`, and `blizzard-mock/src`.

## Generated docstrings

A docstring that generates into `blizzard/openapi/` is public API reference text, so the closed set above still governs
it and it additionally drops whatever an external consumer cannot resolve. Three of the set's shapes go:

- a client-rendering or UI-surface claim;
- an internal identifier — a Python module path, class, method, Sphinx role, or test node id;
- winter workspace path notation.

Against that narrowing, generated description text gains two allowances — an absolute public URL where a reference is
warranted, and a sibling route or schema published in the same spec — and keeps the citation, which resolves publicly.
Every model under `blizzard/src/blizzard/wire` is held to this clause published or not, since any of them is one
`responses=` from being public; `blizzard-mock/src` falls outside it, because its wire models mirror a schema they never
export, so nothing there generates.

## Detect

- A named other module, class, service, or repo followed by what it does, where a pointer would serve.
- A multi-sentence comment arguing a decision no test would fail on if the decision were reverted.
- Alternative-rebuttal framing, greppable as "rather than", "instead of", "not X because".
- Change-history framing, greppable as "unlike the old…", "previously…", "as of this change…" (`canon:no-retro`).
- Per-parameter provenance — each field introduced with the issue that added it, change history organized by parameter.
- An unresolvable reference in a generated description. `blizzard/tests/test_openapi_descriptions.py` fails the unit
  tier on those three shapes, scanning the committed specs and the `wire/` models no spec reaches.

## Do

```python
# Guarded because the row can be naive (`bzh:utc-instants`); pinned by `test_naive_row_rejected`.
seen_at = as_utc(row.seen_at)
```

## Don't

```python
# Guarded because the board renders this value raw and the runner would then report a future
# timestamp to the CLI export downstream.
seen_at = as_utc(row.seen_at)
```

## See also

- `bzh:comment-encapsulation` in [./comment-encapsulation.md](./comment-encapsulation.md) — whose vocabulary an owned
  fact is stated in.
- `bzh:one-prose-home` in [./one-prose-home.md](./one-prose-home.md) — where a fact's one full statement lives.
- `bzh:prose-budget` in [./prose-budget.md](./prose-budget.md) — the measurable half this rule is enforced by: the
  per-block caps and the growth ratchet.
- `bzh:mutation-review-selection` in [../verification/blizzard/evidence.md](../verification/blizzard/evidence.md) — how
  to choose the mutation candidate, and what the pinning test must name.
