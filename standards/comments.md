# Comments and docstrings state only what their own code owns (`bzh:comment-locality`)

Follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`), at file-per-rule granularity.

## Rule

A comment or docstring states only facts its adjacent code owns — what this line, function, or module does, and why it is here.
Delete prose that narrates another module's, component's, or repo's behavior; restates an invariant owned elsewhere; paraphrases the adjacent code; or narrates change history.
A test docstring claims no production behavior beyond what the test's own assertions pin.
A comment defending a decision is converted, not kept: the decision gets a pinning test where none exists (`bzh:mutation-review-selection`), and the comment reduces to a pointer at the test or at the owning doc.

## Why

Cross-module narration is an encapsulation violation in documentation form: module A's text couples to module B's implementation, goes stale silently on every change to B, and no test catches it.
Prose density is also self-replicating — agents match the comment density of the file they edit — so every kept violation seeds more.

## Scope

Binds `#` comments and docstrings across blizzard's Python trees (`blizzard/src`, `blizzard/tests`, `blizzard-mock/src`).
What stays, exhaustively:

| Keep | Example shape |
|------|---------------|
| Why-this-here rationale | why this guard, this ordering, this default — for the adjacent code |
| A local invariant not expressible in code | a lock-ordering or lifetime fact about this module's own state |
| A safety warning tied to the adjacent line | "SIGKILL between these two writes is the armed crash point" |
| An issue / decision citation | `(issue #258)`, `(D-104)`, a `bzh:` id |
| A pointer at the owner | "supersession rules: `hub/domain/status.py`" — a pointer, never the restated content |
| Wire-model field semantics | a wire dataclass docstring scoped to the field's own meaning — it generates into `openapi/`; claims about how a *client* renders or uses the field go |

Growth against the recorded baseline (`blizzard:scripts/prose_density.py`) is the measurable half; this rule is what the measurement enforces.

## Detect

- A comment or docstring explaining what a *named other* module, class, service, or repo does — the other party's name followed by its behavior, not just a pointer to it.
- A test docstring stating behavior no assertion in that test observes.
- A comment restating the statement beside it in English.
- Change-history framing: "unlike the old…", "previously…", "as of this change…" (`canon:no-retro`).
- A multi-sentence comment arguing for a decision with no test that would fail if the decision were reverted — the fix is a pinning test plus a pointer, not better prose.
- Prose growth over the baseline reported by `scripts/prose_density.py --check` in the `blizzard` repo.

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

- `bzh:docstring-prose-authoring` in [`./python.md`](./python.md) — the markdown-authoring principles a docstring's prose is additionally held to.
- `bzh:mutation-review-selection` in [`../verification/blizzard.md`](../verification/blizzard.md) — why a comment-defended decision is the first thing to mutate, and what the pinning test must name.
- `canon:one-owner` in `winter-canon:/principles.md` — the one-canonical-owner principle this rule applies to code prose.
