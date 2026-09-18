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
app.

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

**Rule.** Nothing constructs its own collaborators — every dependency is injected, and concrete wiring happens once, at
the composition root.

**Why.** A single wiring root lets a test substitute a fake store, a virtual clock, and a mock forge without patching
module globals.

**Scope.** The injected clock (`bzh:injected-clock`) is a member of this rule, not an exception to it.

**Detect.** A service instantiating a store, client, clock, or subprocess runner in its own body, or a module-level
singleton read directly. `tests/test_layering.py` fails the unit tier on any of:

- `blizzard.runner.composition` imported, in any form, anywhere outside the seven composition roots named below —
  fail-closed, with no per-name exemption; the module is a wiring root, not a seam a collaborator reaches into.
- `ClaudeCodeAdapter` imported anywhere outside `runner/harness/internal/harness_registry.py` — the one factory that
  constructs it, `build_production_harness_registry`, whose built registry the composition roots take instead;
  `OpenCodeAdapter` is gated the same way, constructed only by `runner/harness/internal/opencode_registry.py`'s
  `build_opencode_binding`.
- A `hub/` or `runner/` module — outside its own connections seam — acquiring `self._engine` directly instead of taking
  the injected `HubStoreConnections` / `RunnerStoreConnections` collaborator (`bzh:dependency-inversion`'s exemplar).
- `SessionFile` named anywhere under `hub/` other than `hub/cli/sessions/internal/session_file.py` (its declaring
  module) and its composition root.
- `IWriteSessionStore` named anywhere under `hub/cli/` other than `hub/cli/sessions/` (the Protocol's own package) and
  its composition root — `login`/`logout` take the `SessionService` application service instead, never the raw seam
  (`bzh:controller-read-only`).
- `runner/transcripts/service.py` importing any package's `internal/` module — its per-owner repository resolver is
  injected instead.

**Do.** Blizzard has no DI container. Seven modules are its composition roots, each wiring every seam once and handing
collaborators down in a frozen dataclass like `HubServices`: `build_hosted_app` in `blizzard/src/blizzard/hub/app.py`,
`build_services` in `blizzard/src/blizzard/hub/composition.py`, `build_hosted_app` in
`blizzard/src/blizzard/runner/app.py`, and `LoopWiring.context` in `blizzard/src/blizzard/runner/loop/build.py`.
`blizzard/src/blizzard/runner/cli/runtime.py`, `blizzard/src/blizzard/runner/cli/external_usage.py`, and
`blizzard/src/blizzard/hub/cli/__init__.py` are roots too: a `click` command (or, for the hub CLI, the `hub` group
callback every verb's context inherits `ctx.obj` from) is a short-lived process with no server loop to hand a dataclass
through, so wiring its concrete collaborators once, inline, at the top of the command body is that process's composition
root. The same reasoning extends to a helper a command's own root calls into rather than repeating:
`blizzard/src/blizzard/runner/cli/daemon.py`'s `uds_client` builds the local UDS `httpx.Client` both
`RunnerDaemon.reach` and `runner/cli/transcript.py`'s `_daemon_holding` need, shared rather than duplicated, with
neither call site substituting a fake for it in a test. `blizzard/src/blizzard/runner/cli/runtime.py`'s `read_stores` is
the same shape: it builds the runner's read-only store bundle and disposes the engine on exit, so
`runner/cli/prompt.py`'s `_stored_override` calls into it instead of repeating the construction outside a composition
root.

**Don't.** A coordinator that calls `ChunkRecordStore()` or `datetime.now()` inside a method.

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
