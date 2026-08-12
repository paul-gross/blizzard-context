# CLEAN architecture

The CLEAN-architecture aspects blizzard carries over from winter-cli — the layering every blizzard daemon, the CLI, and
the mock fleet are structured by. Each rule follows the slot skeleton owned by `winter-canon:/rule-shape.md`
(`canon:rule-shape`).

## Screaming, domain-grouped layout (`bzh:screaming-architecture`)

**Rule.** Group functionality by the domain concept it serves and name the grouping after that concept, so the top-level
package layout announces what the system does — chunks, workflow, delivery — not which framework it runs on.

**Why.** A layout named for its domain lets a cold agent find the code for a behavior from the behavior's name alone,
without a framework map; a layout named for frameworks (`routers/`, `models/`, `services/`) scatters one domain concept
across every technical bucket.

**Detect.** Top-level packages named for a framework or a technical layer (`api/`, `db/`, `schemas/`) rather than a
domain concept; one feature's code split across several such buckets.

**Do.** Top-level packages `chunk/`, `workflow/`, `delivery/`, `lease/` — each owning that concept's domain types, its
repository seam, and its edge handlers.

**Don't.** Top-level packages `models/`, `routers/`, `crud/` that force every chunk-related change to touch three
unrelated directories.

## A dependency-free domain core (`bzh:domain-core`)

**Rule.** Business rules live in a domain layer that depends on nothing outward — no FastAPI, no SQLAlchemy, no click,
no filesystem or network; frameworks, stores, and transports sit outside it and depend inward.

**Why.** A domain core free of outward dependencies is testable at the unit tier without a store or a server standing
up, and survives a framework swap untouched; a domain that imports the ORM cannot be reasoned about or tested without
it.

**Detect.** A domain module importing `fastapi`, `sqlalchemy`, `click`, `httpx`, or `pathlib` I/O; a business rule
reachable only by standing up a store or an HTTP app.

**Do.** A `chunk` domain type and its transition rules that import only other domain types and the framework-agnostic
standard library; the store and the API depend on it.

**Don't.** A domain function that opens a SQLAlchemy session or reads a request object — the rule now cannot run or be
tested without the framework.

## Dependency inversion across owned interfaces (`bzh:dependency-inversion`)

**Rule.** Separate concepts by an interface *owned at the inner layer* and implemented by the outer one: the domain
declares the seam it needs (a Protocol), and the store, forge, harness, or workspace adapter implements it. The
reference shape is the Protocol-seam + `internal/` adapter + factory-injected error pattern in
[../exemplars/python/repo_pattern.py](../exemplars/python/repo_pattern.py).

**Why.** When the inner layer owns the interface, the outer layer is a plug the inner never names — swapping a store or
a forge (`bzh:pluggable-seams`) changes only the adapter, and tests substitute a fake by type. An interface owned by the
outer layer inverts the arrow and drags the framework back into the core.

**Detect.** A domain service that constructs or imports a concrete adapter class instead of depending on a Protocol; an
interface defined in the adapter package and imported inward.

**Do.** The domain declares `IChunkStore` (a `Protocol`); `internal/sqlalchemy_chunk_store.py` implements it; the domain
never imports the adapter.

**Don't.** The domain imports `SqlAlchemyChunkStore` directly, or depends on an `IChunkStore` defined in the adapter
module — either way the arrow points outward.

## Wire at the composition root (`bzh:dependency-injection`)

**Rule.** Nothing constructs its own collaborators; every dependency is injected, and the concrete wiring happens once
at the composition root. The injected clock (`bzh:injected-clock`) is a member of this rule, not an exception to it.

**Why.** Injection at a single root is what lets a test build a daemon with a fake store, a virtual clock, and a mock
forge without patching module globals; a class that news up its own store hard-codes the production collaborator into
every test of it.

**Detect.** A service instantiating a store, an HTTP client, a clock, or a subprocess runner in its own `__init__` or
method body instead of receiving it; module-level singletons read directly rather than injected.

**Do.** The daemon's container binds the store, clock, and seam clients once; each service receives them through its
constructor.

**Don't.** A coordinator that calls `SqlAlchemyChunkStore()` or `datetime.now()` inside a method — the collaborator is
now unswappable and the method untestable in isolation.

## See also

- [./repository-access.md](./repository-access.md) — the read/write repository split and layer-gating these seams are
  shaped by.
- [./system-shape.md](./system-shape.md) — `bzh:pluggable-seams`, the external-system corollary of dependency inversion;
  and `bzh:facts-not-status`, the store-schema invariant.
- [../exemplars/python/repo_pattern.py](../exemplars/python/repo_pattern.py) — the concrete Protocol-seam +
  injected-error pattern the inversion rule points to.
