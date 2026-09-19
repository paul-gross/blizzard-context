# Repository access

These rules refine the dependency-inversion seam [`./clean-architecture.md`](./clean-architecture.md) owns
(`bzh:dependency-inversion`): they govern who may hold which repository, and what crosses the domain boundary. Each rule
below uses the slot skeleton `winter-canon:/rule-shape.md` owns (`canon:rule-shape`), with its `bzh:` id carried in its
heading.

## Split every repository seam (`bzh:repository-split`)

**Rule.** Every repository seam splits into a read-only Protocol and a write Protocol, and a collaborator depends on the
narrowest one its job needs.

**Why.** The Protocol a service depends on makes its intent enforceable at type-check time, and is what the layer gate
`bzh:controller-read-only` keys on.

**Detect.** One repository Protocol exposing both queries and mutations, or a read-path service holding a write-capable
one.

**Scope.** A seam whose reads only project other concepts' own fact tables, with no mutation of its own, stays read-only
rather than pairing with an empty write half: `blizzard/src/blizzard/hub/domain/chunks/facts.py`'s
`IReadChunkFactsRepository` has no write counterpart because `load_facts`/`load_all_facts` project the union of the
other seams' own writes, and splitting that projection per concept would turn one bounded read into one per seam.

**Do.** `blizzard/src/blizzard/hub/domain/chunks/record.py` pairs `IReadChunkRecordRepository` with
`IWriteChunkRecordRepository`, the write variant extending the read one; the composition root binds the write variant
only where mutation is required.

**Don't.** One combined repository injected everywhere, handing a controller that only lists chunks the power to delete
them.

**See also.** [`../exemplars/python/repo_pattern.py`](../exemplars/python/repo_pattern.py) — the read/write Protocol
pair and its binding in runnable form.

## Controllers hold read repositories only (`bzh:controller-read-only`)

**Rule.** Access is layer-gated — controllers at the API and CLI edges hold read-only repositories only, and write
repositories belong to the domain layer alone.

**Why.** A controller able to write around the domain can violate an invariant the domain exists to protect.

**Scope.** A controller answering a query straight from a read model is fine: reads bypass no invariant.

**Detect.** A router or CLI handler injecting a write repository, or a mutation performed in an edge handler instead of
delegated.

**Do.** `blizzard/src/blizzard/hub/api/queue.py` stays read-only over the store and delegates its writes to the queue
domain services, which hold the write chunk repository.

**Don't.** An API route that constructs a chunk and saves it through a write repository.

## Domain operations take objects (`bzh:domain-takes-objects`)

**Rule.** Domain operations receive already-loaded, typed domain objects, never raw identifiers; resolving an identifier
to its object is an edge concern, done before the domain is invoked.

**Why.** A domain that takes objects cannot fail on a missing or malformed id mid-rule, and its signatures state exactly
which entities a rule operates on.

**Exception.** A parameter that resolves not to the entity the operation is about, but to a guard the domain must itself
evaluate as part of its own business rule. `ClaimService.claim`'s `runner_id: str` resolves a paused-runner denial check
inline — a claim-denial rule that belongs in the domain, not at the edge — so it stays a raw id, reasoned and registered
at its own site with `# ast-grep-ignore: bzh:domain-takes-objects`.

**Scope.** A layer that holds no entity type for the identifier at all — the runner's chunk-keyed operations, where no
`Chunk` type exists locally (`bzh:facts-not-status` keeps each per-concept table independent) — still resolves at the
edge: it mints a typed scope naming exactly the facts the rule reads, rather than loading an aggregate that does not
exist. The scope is data, not behavior, and never grows into one.

**Detect.** A domain signature typed `chunk_id: str` rather than `chunk: Chunk`, or a domain method loading an entity
from an id it was passed.

**Do.** `blizzard/src/blizzard/hub/domain/complete.py` declares `complete(self, chunk: Chunk, *, by: str)`; the
controller resolves that chunk through a read repository first. Where no aggregate exists,
`blizzard/src/blizzard/runner/api/chunk_scope.py` mints the typed scope instead — `TakeoverService.open` takes a
`TakeoverOpenScope` resolved there, never a bare `chunk_id`.

**Don't.** `advance(chunk_id: str)`, loading the chunk inside the domain.

`bzh:domain-takes-objects` is tooled by `blizzard:structural-gate`'s ast-grep scan
([`../verification/blizzard.md`](../verification/blizzard.md)), scoped to the hub and runner domain trees.

## Reconstitute in bulk (`bzh:bulk-reconstitution`)

**Rule.** A read seam that reconstitutes domain objects declares a plural counterpart keyed by a caller-supplied id set
beside its singular getter, and a caller holding a set of ids calls that counterpart once instead of the singular form
per id. Every plural answers in a bounded number of queries per id batch and drops an id that does not resolve rather
than raising. A *wide* plural returns exactly what calling the singular form for each id would; a *narrowed* one returns
that restricted to the families it reads, and names that set at the seam so a caller can check its own reaches against
it.

**Why.** `bzh:facts-not-status` makes reconstituting one object cost a fact load and `bzh:domain-takes-objects` puts
that load at the edge before any domain call, so a seam offering only one id and every id leaves a caller holding a
subset with nothing but a fan-out: the bulk strategy has to exist at the seam before a call site can choose it.

**Scope.** This binds seams that reconstitute — a read returning an entity, an aggregate, or a fact projection keyed by
id. A read already set-shaped (a list or page over a filter) and a scalar probe (a count, an existence check) are
outside it, because neither is something a caller iterates ids over. A narrowed plural is the better form wherever the
wide projection's remaining families are dead weight to the caller, but it is never a drop-in for the wide one:
substituting it is safe only where the consumer's reaches sit inside the set it names.

**Detect.** A singular getter called inside a loop, a comprehension, or a per-item resolver; a read Protocol whose only
reads are one id and every id, with nothing keyed by a set between them; a plural form building one unbatched `IN (...)`
over a caller-supplied list, which trades the fan-out for the driver's bind-parameter ceiling; a narrowed plural
substituted for the wide one at a call site whose consumer reaches outside the set the narrowed form names.

**Do.** `blizzard/src/blizzard/hub/domain/chunks/facts.py`'s `IReadChunkFactsRepository` pairs `load_facts` with the
*wide* plural `load_facts_for`, which returns exactly what calling `load_facts` per id would; `status_facts_for` is the
*narrowed* sibling, reading only the fact families a `ChunkStatusView` reaches and naming that set in its own docstring
rather than every family `load_facts_for` loads. `blizzard/src/blizzard/hub/store/internal/finding_store.py`'s
`FindingStore.get_many` resolves its rows in one query and batches their facts through `_facts_for_many` at
`_FACTS_BATCH_SIZE` ids per statement.

**Don't.** `{chunk_id: self._facts.load_facts(chunk_id) for chunk_id in chunk_ids}` — and its seam-level cause, a
Protocol declaring no `load_facts_for` for that comprehension to collapse into.

**See also.** [`./system-shape/store-facts.md`](./system-shape/store-facts.md) `bzh:facts-not-status` and
`bzh:domain-takes-objects` above — together the reason reconstitution is expensive enough to need a plural form.
[`../standards/persistence.md`](../standards/persistence.md) `bzh:sql-portable` — the surface a plural form's batched
`IN` stays inside. [`./system-shape/seam-size.md`](./system-shape/seam-size.md) `bzh:seam-size-ceiling` — a narrowed
plural is preferred partly because it lets a seam split along consumer lines rather than widening one seam toward the
cap. `blizzard/tests/support.py`'s `count_queries` is how a call site's statement count is held flat as the fleet grows.
