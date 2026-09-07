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

**Detect.** `tests/test_repository_seam_size.py`'s AST scan: a class declaring `Protocol` among its own bases with more
than twelve own (non-underscore) methods, unless named in that test's `_ACCEPTED_VIOLATIONS` with its own reason.

**Do.** The runner's harness seam splits `IHarnessAdapter`'s fourteen methods into five narrower Protocols along its
consumers' own lines — worker lifecycle, model/effort/compaction resolution, verdict and output parsing, usage
accounting, and transcript access (`src/blizzard/runner/harness/adapter.py`) — and every consumer re-types to the
narrowest one its job needs; `IHarnessAdapter` itself stays as a composed alias, its own body empty, for the one
consumer (the runner's `app.py` composition root) that threads the full seam through rather than calling it.

**Don't.** Leaving a Protocol to grow past the ceiling because splitting it "later" is easier than registering the width
now, or registering an exception without a reason — either loses the one signal a reviewer has for "this seam grew wider
than any consumer's own job."
