# Repository access

How blizzard code reaches persisted state: the read/write repository split, the layer allowed to mutate, and the shape of a domain call.
These rules sit on top of the dependency-inversion seam (`bzh:dependency-inversion`) — they govern *who may hold which repository* and *what crosses the domain boundary*.
Each rule follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Split repositories into read-only and write (`bzh:repository-split`)

**Rule.** Every repository seam is split into a **read-only** Protocol and a **write** Protocol; a collaborator depends on the narrowest one its job needs.

**Why.** The Protocol a service depends on makes its intent legible and enforceable at type-check time: a read-only dependency cannot mutate even by mistake, and the split is what the layer-gating rule (`bzh:controller-read-only`) keys on. A single read-write repository everywhere erases that signal.

**Detect.** A single `IChunkRepository` exposing both queries and mutations that every consumer depends on; a read-path service holding a write-capable repository.

**Do.** `IReadChunkRepository` (queries) and `IWriteChunkRepository` (mutations, extending the read variant); the DI container binds the write variant only where mutation is required.

**Don't.** One combined repository injected everywhere, so a controller that only lists chunks is handed the ability to delete them.

## Controllers read; only the domain writes (`bzh:controller-read-only`)

**Rule.** Access is layer-gated: controllers at the API and CLI edges may hold **read-only** repositories only; **write** repositories are held by the domain layer alone, so all mutation flows through the business rules.

| Layer                         | Read-only repositories | Write repositories |
| ----------------------------- | ---------------------- | ------------------ |
| Controllers (API / CLI edges) | allowed                | **forbidden**      |
| Domain layer                  | allowed                | allowed            |

**Why.** A controller that can write around the domain can violate an invariant the domain exists to protect; forcing every mutation through the domain layer keeps the business rules the single gate on state change. A controller answering a query straight from a read model is fine — reads bypass no invariant.

**Detect.** A router or CLI handler that injects or calls a write repository; a mutation performed in an edge handler rather than delegated to a domain service.

**Do.** The edge handler resolves inputs and calls a domain service; the domain service holds the write repository and applies the rules before persisting.

**Don't.** An API route that constructs a chunk and saves it through a write repository directly — the transition rules are now bypassable from the edge.

## Domain operations take objects, not identifiers (`bzh:domain-takes-objects`)

**Rule.** Domain-layer operations receive already-loaded, typed **domain objects**, never raw identifiers; resolving an identifier to its object is an edge concern (controller or application service) done before the domain is invoked.

**Why.** A domain that takes objects cannot fail on a missing or malformed id mid-rule, and its signatures state exactly which entities a rule operates on; a domain that takes ids re-does lookup and existence-checking inside the business logic, scattering resolution and error handling across the core.

**Detect.** A domain method signature typed `chunk_id: str` / `runner_id: str` rather than `chunk: Chunk` / `runner: Runner`; a domain method opening a repository to load an entity from an id it was passed.

**Do.** The controller loads `chunk: Chunk` via a read repository, then calls `advance(chunk, verdict)`; the domain never sees the id.

**Don't.** `advance(chunk_id: str)` that loads the chunk inside the domain — resolution and not-found handling have leaked into the core.

## See also

- [./clean-architecture.md](./clean-architecture.md) — `bzh:dependency-inversion` and `bzh:domain-core`, the seam and layering these access rules refine.
- [../exemplars/python/repo_pattern.py](../exemplars/python/repo_pattern.py) — the read/write Protocol pair and the DI binding in concrete form.
