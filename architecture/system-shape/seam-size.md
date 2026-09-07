# Seam size

This spoke owns the ceiling on how wide any single Protocol may grow; the macro-shape hub is
[../system-shape.md](../system-shape.md). Every rule here follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## A Protocol seam stays under the ceiling (`bzh:seam-size-ceiling`)

**Rule.** A Protocol — any class whose own bases include `Protocol` — declares at most twelve own methods. A wider one
either splits into narrower Protocols along its consumers' actual usage lines, with a composed alias retained for a
genuine pass-through that threads the whole seam on without calling it, or is individually registered as an accepted
exception naming why it is genuinely wide by design.

**Why.** `bzh:pluggable-seams` makes every external system reachable only through a Protocol so a consumer depends on
exactly the capability it calls and a test binds exactly that; a Protocol left to grow without bound quietly defeats
this — every consumer ends up typed against the same wide seam regardless of which sliver it actually uses, and a mock
for one caller must still stand in for methods it never touches.

**Scope.** Every Protocol under `src/blizzard/`, not only a repository's read/write seam (`bzh:repository-split`
generalizes here to the whole population) — a coding-harness adapter or a hub client is gated exactly as a repository
seam is.

**Detect.** `tests/test_seam_size.py`'s AST scan: a class declaring `Protocol` among its own bases with more than twelve
own (non-underscore) methods, unless its name is in that test's `_ACCEPTED_VIOLATIONS` set — a name-only membership
test; a reason for the entry is a review obligation, not something the gate itself checks.

**Do.** The runner's harness seam splits `IHarnessAdapter`'s fourteen methods into four narrower Protocols along its
consumers' own lines — worker lifecycle, model/effort/compaction resolution, verdict and output parsing, and usage
accounting (`src/blizzard/runner/harness/adapter.py`). A consumer needing one slice re-types to it directly
(`domain/takeover.py`, `domain/status.py` each take `IHarnessWorkerLifecycle`); two consumers needing the same wider
pair — the runner loop's own step functions (`LoopContext.harness`) and the selftest canary — share one composed
`IHarnessLifecycleAndVerdict` rather than each re-declaring it or falling back to the full seam. `transcript_source`
stays declared directly on `IHarnessAdapter` itself rather than in a fifth named slice: its one caller is the same
`app.py` composition root that already holds the whole seam, so a narrower Protocol would have no holder to narrow for.
`IHarnessAdapter` composes the four slices plus that one method, for the one code path that holds the whole seam without
calling every part of it piecemeal: the runner's `app.py` composition root.

**Don't.** Leaving a Protocol to grow past the ceiling because splitting it "later" is easier than registering the width
now, or registering an exception without a reason — either loses the one signal a reviewer has for "this seam grew wider
than any consumer's own job."
