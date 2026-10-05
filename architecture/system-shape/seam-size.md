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
test; a reason for the entry is a review obligation, not something the gate itself checks. A Protocol base nothing else
names counts toward each Protocol composing it, so a split made only to clear the ceiling still fails; a stale entry
fails too. The one registered exception is `SpawnContext` (`runner/lifecycle/spawn.py`): `Spawner` and `Attempt` hand
each other their context, so it is the union of what either reads.

**Do.** The runner's harness seam splits `IHarnessAdapter`'s methods into narrower Protocols along its consumers' own
lines — worker lifecycle, model/effort/compaction resolution, verdict and output parsing, usage accounting, usage-limit
classification, and provider-overload classification (`src/blizzard/runner/harness/adapter.py`). A consumer never
resolves the full adapter: the registry exposes one accessor per consumer role, each declared to return exactly the
slice that role calls — `lifecycle`, `lifecycle_and_verdict`, `self_test`, `model_resolution`, `usage_accounting`,
`usage_limits`, `provider_overload` (`IHarnessRegistry` in `src/blizzard/runner/harness/registry.py`). The domain
services (`lifecycle/takeover.py`, `status/view.py`) take `IHarnessLifecycleRegistry`, which declares only `lifecycle`.
`LoopContext.harnesses` stays the composed `IHarnessRegistry`, a pass-through every loop step reads its role accessor
from. The selftest canary's widened roster — lifecycle, verdict parsing, usage accounting, plus `transcript_source` —
takes its own `IHarnessSelfTestSeam`. The full `IHarnessAdapter` lives only in `HarnessBinding` (`harness/registry.py`)
and the composition-side registry builder in `harness/wiring.py` that fills it from the harness catalog's declarations.

**Don't.** Leaving a Protocol to grow past the ceiling because splitting it "later" is easier than registering the width
now, or registering an exception without a reason — either loses the one signal a reviewer has for "this seam grew wider
than any consumer's own job."
