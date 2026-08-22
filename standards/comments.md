# Comments and docstrings state only what their own code owns (`bzh:comment-locality`)

Follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), at file-per-rule granularity.

## Rule

A comment or docstring states only facts its adjacent code owns — what this line, function, or module does, and why it
is here. Delete prose that narrates another module's, component's, or repo's behavior; restates an invariant owned
elsewhere; paraphrases the adjacent code; or narrates change history. A test docstring claims no production behavior
beyond what the test's own assertions pin. A comment defending a decision is converted, not kept: the decision gets a
pinning test where none exists (`bzh:mutation-review-selection`), and the comment reduces to a pointer at the test or at
the owning doc — the pointer *replaces* the argument, it never rides alongside it. Alternative-rebuttal prose — "X
rather than Y because…" — goes with it: the road not taken is not a fact the code owns, and if the choice needs
defending, the argument lives in the pinning test's docstring.

## Why

Cross-module narration is an encapsulation violation in documentation form: module A's text couples to module B's
implementation, goes stale silently on every change to B, and no test catches it. Prose density is also self-replicating
— agents match the comment density of the file they edit — so every kept violation seeds more.

## Scope

Binds `#` comments and docstrings across blizzard's Python trees (`blizzard/src`, `blizzard/tests`,
`blizzard-mock/src`). What stays, exhaustively:

| Keep                                       | Example shape                                                                                                                                         |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Why-this-here rationale                    | why this guard, this ordering, this default — for the adjacent code                                                                                   |
| A local invariant not expressible in code  | a lock-ordering or lifetime fact about this module's own state                                                                                        |
| A safety warning tied to the adjacent line | "SIGKILL between these two writes is the armed crash point"                                                                                           |
| An issue / decision citation               | `(issue #258)`, `(D-104)`, a `bzh:` id — riding a one-line fact; a citation never licenses a paragraph                                                |
| A pointer at the owner                     | "supersession rules: `hub/domain/status.py`" — a pointer, never the restated content                                                                  |
| Wire-model field semantics                 | a wire dataclass docstring scoped to the field's own meaning — it generates into `openapi/`; claims about how a *client* renders or uses the field go |

A docstring that **generates into `blizzard/openapi/`** — a wire model's, or a route handler's — is public API reference
text, so it additionally drops what an external consumer cannot resolve:

| Goes                                                                                      | Stays                                                                                                                          |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| A client rendering or UI-surface claim                                                    | The keep table above, unchanged — including the issue / decision / `bzh:` citation, which resolves against a public repository |
| An internal identifier: a Python module path, class, method, Sphinx role, or test node id | An absolute public URL, when a reference is warranted                                                                          |
| Winter workspace path notation                                                            | A sibling **route or schema published in the same spec**                                                                       |

The one exclusion is `blizzard-mock/src`, whose wire models mirror a schema they never export — nothing there generates,
so this paragraph does not reach it. Inside `blizzard/src/blizzard/wire` the whole package is held to it, published or
not: a model there is one `responses=` from being reference text, and the Detect bullet below enforces exactly that
reach.

The measurable half — per-block caps and the growth ratchet — is owned by `bzh:prose-budget`; this rule is what the
measurement enforces.

## Detect

- A comment or docstring explaining what a *named other* module, class, service, or repo does — the other party's name
  followed by its behavior, not just a pointer to it.
- A test docstring stating behavior no assertion in that test observes.
- A comment restating the statement beside it in English.
- Change-history framing: "unlike the old…", "previously…", "as of this change…" (`canon:no-retro`).
- A multi-sentence comment arguing for a decision with no test that would fail if the decision were reverted — the fix
  is a pinning test plus a pointer, not better prose.
- Per-parameter provenance: each field introduced with the issue that added it and its arrival story — change history
  organized by parameter.
- Alternative-rebuttal framing: "rather than", "instead of", "not X because" defending a road not taken.
- Prose growth over the baseline reported by `scripts/prose_density.py check` in the `blizzard` repo.
- An unresolvable reference in a generated description — `blizzard/tests/test_openapi_descriptions.py` fails the unit
  tier on the three `Goes` shapes above, so this half is enforced rather than remembered. It scans the committed specs
  **and** the `wire/` models no spec reaches, which are one `responses=` away from being public and are held to the same
  three shapes.

## Do

```python
# Fencing epoch: reject a stale lease's write (issue #157; pinned by
# tests/test_runner_loop.py::test_stale_epoch_write_rejected).
if lease.epoch < current_epoch:
    raise StaleLeaseError(lease)
```

## Don't

```python
# The hub's deliver node will later merge this branch and the board shows the
# chunk as "delivering" while TakeoverService forwards the identity env, so we
# must set the epoch here first.
if lease.epoch < current_epoch:
    raise StaleLeaseError(lease)
```

## See also

- `bzh:docstring-prose-authoring` in [`./python.md`](./python.md) — the markdown-authoring principles a docstring's
  prose is additionally held to.
- `bzh:mutation-review-selection` in [`../verification/blizzard/evidence.md`](../verification/blizzard/evidence.md) —
  why a comment-defended decision is the first thing to mutate, and what the pinning test must name.
- `canon:one-owner` in `winter-canon:/principles.md` — the one-canonical-owner principle this rule applies to code
  prose.
- `bzh:comment-encapsulation` in [`./comment-encapsulation.md`](./comment-encapsulation.md) — the boundary discipline an
  owned fact's *vocabulary* is additionally held to.
- `bzh:prose-budget` in [`./prose-budget.md`](./prose-budget.md) — the per-block line caps that make pruning a trigger
  rather than a judgment.
- `bzh:one-prose-home` in [`./one-prose-home.md`](./one-prose-home.md) — where each fact's one full statement lives.
