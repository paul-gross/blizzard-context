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

**Do.** `blizzard/src/blizzard/hub/domain/work.py` pairs `IReadChunkRepository` with `IWriteChunkRepository`, the write
variant extending the read one; the composition root binds the write variant only where mutation is required.

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

**Detect.** A domain signature typed `chunk_id: str` rather than `chunk: Chunk`, or a domain method loading an entity
from an id it was passed.

**Do.** `blizzard/src/blizzard/hub/domain/complete.py` declares `complete(self, chunk: Chunk, *, by: str)`; the
controller resolves that chunk through a read repository first.

**Don't.** `advance(chunk_id: str)`, loading the chunk inside the domain.
