# Clean architecture

The layering rules every blizzard daemon, the CLI, and the mock fleet are held to. Each rule below uses the slot
skeleton `winter-canon:/rule-shape.md` owns (`canon:rule-shape`), with its `bzh:` id carried in its heading.

When the behavior you are placing touches persistence or a controller, read
[`./repository-access.md`](./repository-access.md): it owns which repository each layer holds and what a domain call
takes.

## Domain core (`bzh:domain-core`)

**Rule.** Business rules live in a domain layer that depends on nothing outward — no FastAPI, SQLAlchemy, click, httpx,
filesystem, or network — with frameworks, stores, and transports outside it, depending inward.

**Why.** A domain core free of outward dependencies is unit-testable with no store or server, and survives a framework
swap untouched.

**Detect.** A domain module importing any of those packages, or a business rule reachable only through a store or HTTP
app. `tests/test_layering.py` fails the unit tier on a `hub/domain/` or `runner/domain/` module importing fastapi,
starlette, sqlalchemy, click, or httpx.

**Do.** `blizzard/src/blizzard/hub/domain/` and `blizzard/src/blizzard/runner/domain/` import no web, ORM, or CLI
package; `blizzard/src/blizzard/hub/api/` and `blizzard/src/blizzard/hub/store/` depend on them, never the reverse.

**Don't.** A domain function that opens a SQLAlchemy session or reads a request object.

## Dependency inversion (`bzh:dependency-inversion`)

**Rule.** The inner layer owns the interface and the outer implements it — the domain declares the Protocol seam, and
the store, forge, harness, or workspace adapter satisfies it.

**Why.** An inner-owned interface makes the outer layer a plug the inner never names: swapping a store or forge
(`bzh:pluggable-seams`) touches only the adapter, and tests substitute fakes by type.

**Detect.** A domain service importing a concrete adapter, or a Protocol defined in the adapter package and imported
inward.

**Do.** `blizzard/src/blizzard/hub/domain/chunks/` declares per-concept read/write Protocol pairs (for example
`IReadChunkRecordRepository` and `IWriteChunkRecordRepository`) plus one read-only-only seam (`facts`);
`ChunkRecordStore` in `blizzard/src/blizzard/hub/store/internal/chunk_record_store.py` implements that pair
structurally, one adapter per seam, and the domain never imports any of them.

**Don't.** A domain module that imports `ChunkRecordStore` directly.

**See also.** [`../exemplars/python/repo_pattern.py`](../exemplars/python/repo_pattern.py) — the runnable reference for
this seam, its `internal/` adapter placement, and its factory-injected error wrapping; read it when building a
repository.

## Dependency injection (`bzh:dependency-injection`)

**Rule.** Nothing constructs its own collaborators — every dependency is injected. A long-lived process has one
composition graph: process-scoped collaborators are built once and injected into both its served app and its driver.
Short-lived CLI commands have their own roots.

**Why.** One process graph prevents independently wired app and driver collaborators from diverging, and lets tests
substitute a fake store, a virtual clock, and a mock forge without patching module globals.

**Scope.** The injected clock (`bzh:injected-clock`) is a member of this rule, not an exception to it.

**Detect.** A service instantiating a store, client, clock, or subprocess runner in its own body, or a module-level
singleton read directly. `tests/test_layering.py` fails the unit tier on any of:

- `blizzard.runner.composition` imported, in any form, anywhere outside the composition roots named below — fail-closed,
  with no per-name exemption; the module is a wiring root, not a seam a collaborator reaches into.
- A `hub/` or `runner/` module — outside its own connections seam — acquiring `self._engine` directly instead of taking
  the injected `HubStoreConnections` / `RunnerStoreConnections` collaborator (`bzh:dependency-inversion`'s exemplar).
- A `blizzard.*` class constructed more than once across the hub's composition-root files (`hub/app.py`,
  `hub/composition.py`, `hub/store/internal/chunk_store_factory.py`) — a second copy of a process-scoped collaborator.
- `build_stores`, `build_production_harness_registry`, or `HarnessHealthCache` called anywhere under
  `blizzard/src/blizzard/` other than `runner/composition.py` — a second copy of the runner's process graph.

**Do.** Blizzard has no DI container. Its long-lived processes each own one graph, handing process-scoped collaborators
down in a frozen dataclass like `HubServices`. Thread-confined engines and clients can remain independent, but belong to
the same process graph with explicit lifetimes:

- `build_hosted_app` in `blizzard/src/blizzard/hub/app.py`, which runs `build_hub_core`, then the work-source registry,
  then `build_services`
- `build_hub_core` and `build_services` in `blizzard/src/blizzard/hub/composition.py`: the core builds the shared stores
  and leaf services once; `build_services` takes it and builds none of them
- The runner host graph in `blizzard/src/blizzard/runner/composition.py`, injected into the served app in
  `blizzard/src/blizzard/runner/app.py` and the periodic loop in `blizzard/src/blizzard/runner/loop/build.py`

The CLI modules below are roots for short-lived commands — they wire collaborators once, inline, at the top of the
command body, without joining the hosted process graph:

- `blizzard/src/blizzard/runner/cli/runtime.py`
- `blizzard/src/blizzard/runner/cli/external_usage.py`
- `blizzard/src/blizzard/runner/cli/opencode.py`
- `blizzard/src/blizzard/tools/invariants.py`
- `blizzard/src/blizzard/hub/cli/__init__.py` — the `hub` group callback, which every verb's context inherits `ctx.obj`
  from

The same reasoning extends to a helper a command's own root calls into rather than repeating:

- `blizzard/src/blizzard/runner/cli/daemon.py`'s `uds_client` builds the local UDS `httpx.Client` both
  `RunnerDaemon.reach` and `runner/cli/transcript.py`'s `_daemon_holding` need, shared rather than duplicated, with
  neither call site substituting a fake for it in a test.
- `blizzard/src/blizzard/runner/cli/runtime.py`'s `read_stores` builds the runner's read-only store bundle and disposes
  the engine on exit, so `runner/cli/prompt.py`'s `_stored_override` calls into it instead of repeating the construction
  outside a composition root.

**Don't.** A coordinator that calls `ChunkRecordStore()` or `datetime.now()` inside a method.

## Internal visibility (`bzh:internal-visibility`)

**Rule.** A package's `internal/` is private to that package: only the package that directly contains it, and every
module below that package, may import from it. Composition roots may import any `internal/`.

**Why.** `internal/` holds a package's adapters and helpers; a sibling package importing one couples to a concrete class
instead of the package's public surface, so the adapter can no longer change without breaking its neighbor.

**Scope.** Tests are out of scope: they are white-box and act as their own roots. The composition roots are the modules
`bzh:dependency-injection` names; there is no per-import exemption — a crossing is fixed, or its importer is a root.

**Detect.** A module outside `<pkg>/` importing a module under `<pkg>/internal/`, by absolute, relative, or
`from <pkg> import internal` form. `tests/test_layering.py`'s generic check fails the unit tier on it, over every
`internal/` under `blizzard/src/blizzard/`, naming the owner.

**Do.** `blizzard/src/blizzard/foundation/store/batching.py` is the public home of the id-batching both daemons' stores
share.

**Don't.** A store adapter in one package importing an adapter or helper from another package's `internal/`, rather than
taking the seam or a public module.

## Screaming architecture (`bzh:screaming-architecture`)

**Rule.** Group functionality by the domain concept it serves and name the grouping for that concept, so the layout
announces what the system does, not what runs it.

**Why.** A domain-named layout lets a cold agent find a behavior's code from the behavior's name alone, without a
framework map.

**Detect.** One feature's code split across several technical buckets, or a package named for a framework or bucket
rather than for the concept it serves.

**Do.** Blizzard's concept packages sit inside each daemon — `blizzard/src/blizzard/hub/auth/`,
`blizzard/src/blizzard/hub/delivery/`, `blizzard/src/blizzard/runner/harness/`,
`blizzard/src/blizzard/runner/transcripts/` — each owning that concept's domain types and repository seam.

**Don't.** `models/`, `routers/`, and `crud/`, where one chunk change touches three unrelated directories.
