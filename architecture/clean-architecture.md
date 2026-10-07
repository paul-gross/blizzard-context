# Clean architecture

The layering rules every blizzard daemon, the CLI, and the mock fleet are held to. Each rule below uses the slot
skeleton `winter-canon:/rule-shape.md` owns (`canon:rule-shape`), with its `bzh:` id carried in its heading.

When the behavior you are placing touches persistence or a controller, read
[`./repository-access.md`](./repository-access.md): it owns which repository each layer holds and what a domain call
takes. When a module under `blizzard/src/blizzard/hub/domain/` needs another concept package's types or data, the table
in `bzh:domain-package-layers` below decides whether it may import that package or the code must move.

When you add a runner loop step or give one something new to read, `bzh:narrow-seams` below owns the step's own context
Protocol.

## Domain core (`bzh:domain-core`)

**Rule.** Business rules live in a domain layer that depends on nothing outward — no FastAPI, SQLAlchemy, click, httpx,
filesystem, or network — with frameworks, stores, and transports outside it, depending inward.

**Why.** A domain core free of outward dependencies is unit-testable with no store or server, and survives a framework
swap untouched.

**Detect.** A domain module importing any of those packages, or a business rule reachable only through a store or HTTP
app. `tests/test_layering.py` fails the unit tier on a `hub/domain/` module, or a runner domain-core module, importing
fastapi, starlette, sqlalchemy, click, httpx, os, shutil, subprocess, or tempfile. A harness binding package
(`runner/harness/claude_code/`, `runner/harness/opencode/`) is an adapter, not a concept package: it may bind a process
or the filesystem, so it is exempt from the `os`, `shutil`, `subprocess`, and `tempfile` half of the check and still
held to the framework five. The binding set is named explicitly, so a new binding fails the gate until it is named. Any
other module's stdlib-driver import needs a reasoned entry in the per-module exemption map in `tests/test_layering.py`,
which admits only the packages it names; an entry whose module no longer imports a package it admits is stale and fails
the gate. Pure path arithmetic (`posixpath`, `PurePosixPath`) needs no exemption, and the import check cannot see
pathlib I/O (`Path.read_text`, `Path.mkdir`). A runner domain-core module is any module of a `bzh:domain-package-layers`
runner node outside an `internal/` package (`_runner_domain_core_files`): a concept package's public surface holds its
models, ports, and the services carrying its rules, and the adapter binding a framework or driver sits in its
`internal/`. The layer gate already keeps every such module off `blizzard.runner.store` and `blizzard.runner.api`, which
no row lists. The same layer walker fails a `hub/domain/` module importing `blizzard.hub.config` or
`blizzard.hub.delivery`, in any import form.

**Do.** `blizzard/src/blizzard/hub/domain/` and the runner's concept packages (`runner/leases/`, `runner/lifecycle/`,
`runner/tracing/`, …) import no web, ORM, or CLI package; `hub/api/`, `hub/store/`, `runner/api/`, and `runner/store/`
depend on them, never the reverse. The hub-JWKS seam `IJwksCache` sits in `runner/auth/jwks_cache.py`; its httpx binding
sits in `runner/auth/internal/http_jwks_cache.py`, built only in the app composition root. The runner's FastAPI
federation router lives at `runner/api/federation.py`, not under `runner/auth/`. A config value the hub domain reads is
a domain-owned type the config edge builds (`hub/config.py` parses and renders; the domain holds the value). A domain
service types a delivery collaborator by a domain Protocol, as `ApplyService` does with `IHubNodeExecutor`.

**Don't.** A domain function that opens a SQLAlchemy session or reads a request object.

**See also.** `bzh:shared-kernel` owns which business rules leave a daemon's domain for `foundation/` — the ones both
daemons evaluate identically.

## Domain-orchestration split (`bzh:domain-orchestration-split`)

**Rule.** A concept's business rules live on its model — methods on its types, or pure functions in its own module —
taking loaded objects and plain values, the current instant included, and returning a decision: the fact or record to
write, or a refusal. A use-case service only orchestrates: it reads the clock, calls the model, hands the decision to a
port, and absorbs a lost write race. A controller only resolves ids, calls the service, and maps a domain error to its
status.

**Why.** A rule interleaved with ports is testable only through fakes and reusable only by copying, so it drifts outward
into a controller or goes unwritten. On the model it is tested by value, and the concept's legal transitions are
declared in one place.

**Scope.** A decision on a loaded object's state is a rule. Choosing what to load, ordering writes, the post-write
re-check that turns a lost race into the domain error, and the store's own guard are orchestration and adapter concerns,
not the rule restated. The rule binds where a decision is made, not its form: a pure function the service calls already
complies.

**Detect.** The anemic domain model — types that carry state while services decide for them. Its tells:

- A `*Service` method raising a domain error from a field of an object it was handed.
- A rule whose branch a test reaches only through a fake repository or clock.
- A controller raising a 4xx for anything but an unknown id or a mapped domain error.
- A concept carrying a state with no declared table of which verbs are legal from which state.

The fix is the pass [`../workflows/domain-orchestration-split.md`](../workflows/domain-orchestration-split.md) owns
(`bzh:domain-orchestration-split-pass`).

**Do.**

```python
class Finding:
    def supersede_into(self, absorber: Finding, *, note: str, actor: str, at: datetime) -> FactEntry:
        if not absorber.live:
            raise AbsorberNotLive(absorber.finding_id)
        return FactEntry(finding_id=self.finding_id, kind="superseded", at=at, note=require_note(note), actor=actor)


class FindingExitService:
    def supersede(self, findings: Sequence[Finding], absorber: Finding, *, note: str, actor: str) -> None:
        at = self._clock.now()
        self._repo.record_facts([f.supersede_into(absorber, note=note, actor=actor, at=at) for f in findings])
```

**Don't.**

```python
class ProposalClosureService:
    def pass_(self, proposal: Proposal, *, reason: str, by: str) -> Closure:
        if not reason.strip():  # a rule, reachable only past the repository and clock this service holds
            raise PassReasonRequired()
        at = self._clock.now()
        ...
```

**See also.** `bzh:domain-core` — what the model may not depend on. `bzh:domain-takes-objects`
([./repository-access.md](./repository-access.md)) — an id a rule needs arrives as its loaded object.

## Dependency inversion (`bzh:dependency-inversion`)

**Rule.** The inner layer owns the interface and the outer implements it — the domain declares the Protocol seam, and
the store, forge, harness, or workspace adapter satisfies it.

**Why.** An inner-owned interface makes the outer layer a plug the inner never names: swapping a store or forge
(`bzh:pluggable-seams`) touches only the adapter, and tests substitute fakes by type.

**Detect.** A domain service importing a concrete adapter, or a Protocol defined in the adapter package and imported
inward.

**Do.** `blizzard/src/blizzard/hub/domain/chunk/ports/` declares per-concept read/write Protocol pairs (for example
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
  `blizzard/src/blizzard/runner/app.py` and the periodic loop's wiring in `blizzard/src/blizzard/runner/loop_wiring.py`

Every click command body under a `*/cli/` directory, and the `OperatorGroup` and `_RunnerGroup` `invoke` methods, is a
short-lived root: it wires collaborators once, inline, at the top, without joining the hosted process graph. A root
resolves what a test may swap from `ctx.find_object(<carrier>)` and defaults to the production one when the invoker
handed none; a test hands its own through `CliRunner.invoke(obj=...)`. A module-level factory a test patches is not a
seam. The shared carrier is `CliCollaborators` in `blizzard/src/blizzard/cli/collaborators.py`; the root groups resolve
it and pass it into `OperatorTrace` and `WorkerSession` as required arguments. `runner/cli/runtime.py`'s `init` resolves
its own hub-clients carrier the same way, keeping the HTTP default out of the `runner` group so a worker verb never
loads a daemon's stack.

This prose rule is wider than the mechanical roster: `tests/test_layering.py::_COMPOSITION_ROOTS` stays the narrower set
of modules that may import `internal/` (`bzh:internal-visibility`) or `blizzard.runner.composition`, and a CLI module
outside it is not a violation.

The same reasoning extends to a helper a command's own root calls into rather than repeating, provided the root passes
in whatever varies:

- `blizzard/src/blizzard/runner/cli/daemon.py`'s `uds_client` builds the local UDS `httpx.Client` both
  `RunnerDaemon.reach` and `runner/cli/transcript.py`'s `_daemon_holding` need, shared rather than duplicated; each
  caller passes the trace-header source its command resolved, so no call site reads one ambiently.
- `blizzard/src/blizzard/runner/cli/runtime.py`'s `read_stores` builds the runner's read-only store bundle and disposes
  the engine on exit, so `runner/cli/prompt.py`'s `_stored_override` calls into it instead of repeating the construction
  outside a composition root.

Example — a click command taking its swappable collaborators from the invoker:

```python
@click.command()
@click.pass_context
def init(ctx: click.Context, ...) -> None:
    collaborators = ctx.find_object(InitCollaborators) or InitCollaborators(_http_hub_clients)
    with collaborators.join_with(config) as (identity, admin):
        _join_hub(config, identity, admin, allow_readd=allow_readd)


# in a test: result = CliRunner().invoke(blizzard, ["runner", "init", ...], obj=InitCollaborators(fake_hub.clients))
```

**Don't.** A coordinator that calls `ChunkRecordStore()` or `datetime.now()` inside a method; a module-level
`client_factory` that a test monkeypatches.

## Narrow seams and step context Protocols (`bzh:narrow-seams`)

**Rule.** Type each collaborator's dependencies as the seams it uses, never as a bundle that carries every seam. Only a
composition root, the runner's loop driver, or an API or CLI edge holds a bundle. Adding a runner loop step, or giving a
step something new to read — a probe, a config value, a store — takes three moves:

1. Put the logic in a step module, never inline in a `steps.py` phase: the driver holds `LoopContext` only to hand it to
   step modules. Combining a new check's result with existing ones is step logic too: the phase makes one call into a
   step module and branches on that one result.
2. Add the member to that module's context Protocol and to `LoopContext`.
3. Keep a `_conforms_*` sentinel for that Protocol in `runner/loop/context.py`.

A pluggable seam such as a probe (`bzh:pluggable-seams` in [./system-shape.md](./system-shape.md)) is one member the
step's Protocol declares; it never stands in for that Protocol.

**Why.** A bundle parameter hides what a collaborator touches: a test must build the whole bundle, and a reviewer cannot
tell from the signature which state a change can reach. A narrow seam states the dependency in the type, so pyright
fails any caller that supplies less and any member the collaborator starts reading without declaring it.

**Scope.** The bundles are the runner's store bundles — `RunnerStores`, `RunnerReadStores`, and the `IReadRunnerStore` /
`IWriteRunnerStore` Protocols they satisfy, all in `blizzard/src/blizzard/runner/stores.py` — and the loop's
`LoopContext`. The composition roots are those `bzh:dependency-injection` names; the loop driver is
`runner/loop/context.py`, `runner/loop/tick.py`, and `runner/loop/steps.py`; the edges are everything under
`runner/api/` and `runner/cli/`. The hub's `HubServices`, held by its API edge, is out of scope. Tests are out of scope:
they act as their own roots.

**Detect.** A step or domain service typed by a bundle while its body reads a handful of the bundle's members.
`tests/test_layering.py` fails the unit tier on each check below, and each has its own self-tests over a temporary tree:

- `test_only_the_loop_driver_and_composition_roots_name_loop_context` — `LoopContext` named, in any form, under
  `blizzard/src/blizzard/` outside the loop driver and the composition roots. Self-tests:
  `test_loop_context_check_catches_every_naming_form`,
  `test_loop_context_check_admits_the_driver_and_other_context_names`.
- `test_only_the_roots_driver_and_edges_name_a_runner_store_bundle` — a store-bundle name under `runner/` outside
  `stores.py`, the loop driver, the composition roots, `runner/api/`, and `runner/cli/`. Self-tests:
  `test_store_bundle_check_catches_a_bundle_outside_the_edges`, `test_store_bundle_check_admits_the_edges_and_driver`.
- `test_no_runner_loop_module_is_a_composition_root_or_imports_composition` — a composition root placed under
  `runner/loop/`, or a `runner/loop/` module importing `blizzard.runner.composition`. Self-test:
  `test_loop_composition_check_catches_every_import_form`.
- `test_every_loop_step_types_its_context_by_a_protocol_it_declares` — a `ctx` parameter or `ctx:` field under
  `runner/`, outside the driver, roots, and edges, not typed by a `Protocol` its own module declares; or a parameter or
  field of any other name typed — bare, module-qualified, or wrapped in a union — by `LoopContext` or another module's
  step context. Self-tests: `test_step_context_check_catches_a_foreign_or_bundle_context`,
  `test_step_context_check_admits_a_local_protocol`.
- `test_loop_context_has_a_conformance_sentinel_for_every_step_context` — a step context Protocol with no `_conforms_*`
  sentinel in `runner/loop/context.py` proving `LoopContext` satisfies it. Self-test:
  `test_conformance_check_catches_a_step_context_without_a_sentinel`.

The fix is to declare what the module reads, never to widen an exemption.

**Do.** A loop step module declares its own context Protocol beside its steps, inheriting the Protocol of any step it
hands its context to, and `runner/loop/context.py` proves the driver's bundle satisfies it:

```python
# runner/lifecycle/attempt.py: hands its ctx to a spawn step
class AttemptContext(SpawnContext, Protocol): ...

# runner/loop/context.py
if TYPE_CHECKING:
    from blizzard.runner.lifecycle.attempt import AttemptContext

    def _conforms_to_attempt(ctx: LoopContext) -> AttemptContext:
        return ctx
```

A domain service takes one keyword parameter per repository seam:
`TakeoverService(clock, process, *, takeover, asks, outbound, tokens, elicitations, ...)`.

**Don't.** A domain service taking `stores: RunnerReadStores` to read seven of its repositories, or a step dataclass
with a `ctx: LoopContext` field. A new gate added inline to a `steps.py` phase, reading a new `LoopContext` member that
no step Protocol declares.

**See also.** `bzh:seam-size-ceiling` ([./system-shape/seam-size.md](./system-shape/seam-size.md)) caps how wide one
Protocol grows; this rule governs which Protocols a collaborator depends on.

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

## Shared kernel (`bzh:shared-kernel`)

**Rule.** `blizzard/src/blizzard/wire/`, `foundation/`, and `auth_core/` are the shared kernel both daemons import, and
none of them imports a blizzard package outside it — `hub`, `runner`, `cli`, or `tools` — directly or transitively.
Every vocabulary type a wire model carries has exactly one definition, in the kernel (`foundation/`, one module per
vocabulary); the daemons import it from there, with no re-export at an old home, no mirror, and no mapping layer. The
business rules over that vocabulary stay in each daemon's domain (`bzh:domain-core`), with one carve-out: a rule both
daemons must evaluate identically, so that neither accepts what the other refuses, lives once in `foundation/` as pure
functions or methods of frozen kernel types, with no I/O and no collaborators; a rule only one daemon applies stays in
that daemon's domain. Within a daemon, a `wire/` model is named only at its app boundary, which maps it to domain models
(`bzh:data-roles`, [./data-roles.md](./data-roles.md)).

**Why.** A wire model importing a daemon's domain type makes importing the wire load that daemon, so the hub loads
runner modules and the runner loads hub modules through it. The wire stops being the one place a vocabulary changes, and
a second copy of an enum — or of a predicate both daemons apply — drifts unseen until the runner accepts what the hub
refuses.

**Detect.** `tests/test_layering.py` fails the unit tier on a kernel module importing a non-kernel blizzard package
(check A), on any kernel module import loading a `hub`, `runner`, `cli`, or `tools` module in a fresh interpreter, and
on a hub or runner composition root loading the other daemon. Its moved-vocabulary check (D) fails an import of a moved
name through any home but its `foundation/` one. A business rule in `foundation/` that only one daemon applies is that
daemon's rule placed in the kernel; the fix moves it into that daemon's domain. One both daemons apply that takes a
repository, clock, or client, or performs I/O, is made pure, with the facts and the instant passed in as values.

**Do.** A new enum carried on a `wire/` model that hub domain code also uses is defined once in a `foundation/` module;
`wire/` and `hub/domain/` both import it. A type no wire model carries stays in its daemon's domain.
`foundation/completion_gates.py` holds the node-step completion predicates — `Coverage.unmet`, `ChecksGate.violated` —
the runner judges before it submits and the hub re-checks before it accepts, and `foundation/usage_windows.py` holds
`admit_usage_window`, which the runner applies before it sends a usage window and the hub applies at intake.

**Don't.** A `wire/` module importing from `hub/domain/` or `runner/`, or a daemon-side copy of a wire enum paired with
a function mapping between the two. Two hand-synced copies of a completion predicate, one per daemon; or one daemon
calling the other over the wire for a verdict it can compute from the facts it already holds.

**See also.** `bzh:fleet-wire-additive` ([./system-shape/fleet-wire.md](./system-shape/fleet-wire.md)) governs what may
change on the wire; this rule makes the kernel the only place it can change.

## Screaming architecture (`bzh:screaming-architecture`)

**Rule.** Group functionality by the domain concept it serves and name the grouping for that concept, so the layout
announces what the system does, not what runs it.

**Why.** A domain-named layout lets a cold agent find a behavior's code from the behavior's name alone, without a
framework map.

**Detect.** One feature's code split across several technical buckets, or a package named for a framework or bucket
rather than for the concept it serves.

**Do.** Blizzard's concept packages sit inside each daemon — `blizzard/src/blizzard/hub/auth/`,
`blizzard/src/blizzard/hub/delivery/`, `blizzard/src/blizzard/runner/harness/`, `blizzard/src/blizzard/runner/leases/`,
`blizzard/src/blizzard/runner/lifecycle/`, `blizzard/src/blizzard/runner/transcripts/` — each owning that concept's
domain types and repository seam. Inside `blizzard/src/blizzard/hub/domain/`, the hub's business rules split the same
way into the concept packages `bzh:domain-package-layers` orders (`chunk/`, `execution/`, `operations/`, `garden/`, …);
the runner's concept packages sit directly under `blizzard/src/blizzard/runner/`, ordered by the same rule's runner
table.

**Don't.** `models/`, `routers/`, and `crud/`, where one chunk change touches three unrelated directories.

## Domain package layers (`bzh:domain-package-layers`)

**Rule.** Put every hub-domain module in one of the concept packages under `blizzard/src/blizzard/hub/domain/`, and
every runner module outside the edges in one of the runner's nodes; import another package only where the importer's
table row allows it. Every hub package may also import `kernel`.

| Layer | Package         | May import (besides `kernel`)            |
| ----- | --------------- | ---------------------------------------- |
| L0    | `kernel`        | —                                        |
| L0    | `artifact`      | —                                        |
| L0    | `config`        | —                                        |
| L1    | `graph`         | `artifact`                               |
| L1    | `runners`       | —                                        |
| L2    | `chunk`         | `graph`, `runners`, `artifact`           |
| L3    | `execution`     | `chunk`, `graph`, `runners`, `artifact`  |
| L4    | `operations`    | `execution`, `chunk`, `graph`, `runners` |
| L5    | `work_items`    | `operations`, `chunk`, `graph`           |
| L6    | `garden`        | `work_items`, `chunk`, `graph`, `config` |
| L7    | `observability` | `chunk`, `graph`, `runners`              |

The runner's table. `harness/claude_code`, `harness/opencode`, and `harness/wiring` are nodes of their own; any other
`runner/<first segment>` is that segment, so `config_table.py` and `stores.py` are the two top-level modules in the
graph.

| Layer | Node                  | May import                                                                                                                                             |
| ----- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| L0    | `config_table`        | —                                                                                                                                                      |
| L0    | `node_steps`          | —                                                                                                                                                      |
| L0    | `process`             | —                                                                                                                                                      |
| L0    | `events`              | —                                                                                                                                                      |
| L0    | `environments`        | —                                                                                                                                                      |
| L0    | `subscriptions`       | —                                                                                                                                                      |
| L0    | `auth`                | —                                                                                                                                                      |
| L1    | `harness`             | `config_table`, `environments`, `node_steps`, `process`                                                                                                |
| L2    | `harness/claude_code` | `config_table`, `harness`, `node_steps`, `process`, `subscriptions`                                                                                    |
| L2    | `harness/opencode`    | `config_table`, `harness`, `node_steps`, `process`                                                                                                     |
| L2    | `leases`              | `environments`, `events`, `harness`, `node_steps`                                                                                                      |
| L3    | `harness/wiring`      | `config_table`, `harness`, `process`, `harness/claude_code`, `harness/opencode`                                                                        |
| L3    | `hub`                 | `auth`, `events`, `harness`, `leases`, `node_steps`                                                                                                    |
| L4    | `transcripts`         | `environments`, `harness`, `hub`, `leases`                                                                                                             |
| L4    | `throttle`            | `events`, `harness`, `leases`                                                                                                                          |
| L5    | `usage`               | `environments`, `events`, `harness`, `leases`, `subscriptions`, `transcripts`                                                                          |
| L6    | `lifecycle`           | `auth`, `environments`, `events`, `harness`, `hub`, `leases`, `node_steps`, `process`, `throttle`, `transcripts`, `usage`                              |
| L7    | `operator`            | `leases`, `lifecycle`                                                                                                                                  |
| L7    | `tracing`             | `harness`, `hub`, `leases`, `transcripts`                                                                                                              |
| L7    | `selftest`            | `environments`, `harness`, `lifecycle`, `node_steps`, `process`                                                                                        |
| L7    | `status`              | `environments`, `harness`, `hub`, `leases`, `lifecycle`, `throttle`                                                                                    |
| L8    | `stores`              | `auth`, `environments`, `harness`, `hub`, `leases`, `lifecycle`, `throttle`, `tracing`, `transcripts`, `usage`                                         |
| L9    | `loop`                | `process`, `events`, `environments`, `harness`, `subscriptions`, `leases`, `hub`, `transcripts`, `throttle`, `usage`, `lifecycle`, `tracing`, `stores` |

A row's layer orders its table: every package or node a row may import sits on a strictly lower layer, `kernel` aside,
so no declared edge runs between two rows of one layer.

Import a module by its full module path, and a name from the module that defines it: a package's surface is its modules
outside `internal/` (`bzh:internal-visibility`), and its `__init__.py` re-exports nothing.

**Why.** Edges that only point down let a package change without breaking any package below it, and leave no
package-level cycle for a `TYPE_CHECKING` guard or a function-level import to hide. One import path per name means a
moved type leaves no second spelling behind.

**Scope.** The table governs imports of `blizzard.hub.domain.*` made by modules under `hub/domain/`; imports inside one
package are free. Adapters — `hub/api/`, `hub/store/`, the composition roots, tests — depend inward on any package
(`bzh:domain-core`), but they too take each name from the module that defines it. The runner table governs imports of
`blizzard.runner.*` made by modules of its nodes; imports inside one node are free. `runner/api/`, `runner/cli/`,
`runner/store/`, `config`, `composition`, `app`, `runtime`, `listeners`, `loop_wiring`, and tests are edges: they depend
inward on any node, and no node imports them — a concept package takes config values by injection (a settings object or
a structural Protocol), never `RunnerConfig`.

**Detect.** A domain module importing a package its row does not list — at module level, inside a function, under
`TYPE_CHECKING`, or by relative import — or importing the bare `blizzard.hub.domain` umbrella; a `.py` directly under
`hub/domain/` other than `__init__.py`, or a package directory the table does not declare; a package `__init__.py` that
imports a name to re-export it; any module under `src/` or `tests/` importing a name from a domain module that only
imports it. `tests/test_layering.py` fails the unit tier on all six:
`test_hub_domain_packages_import_only_what_their_layer_allows` walks every domain module against the table's mirror,
`_DOMAIN_PACKAGE_LAYERS`, `test_hub_domain_package_layers_are_acyclic` holds that dict acyclic with its keys equal to
the package directories, and `test_hub_domain_package_inits_re_export_nothing` holds every package `__init__.py` to a
docstring and the `__future__` import, `test_runner_node_package_inits_re_export_nothing` holds every runner node's
package `__init__.py` to the same, and `test_each_hub_domain_name_has_one_import_path` holds every import of a domain
module's name to the module defining it. `test_domain_layer_check_counts_every_import_form`,
`test_domain_layer_cycle_check_catches_a_cycle`, `test_a_domain_init_that_imports_a_name_is_flagged`, and
`test_domain_second_spelling_check_flags_an_import_through_an_importer` prove the walker, the cycle check, the re-export
check, and the second-spelling check fire on planted trees. `test_runner_packages_import_only_what_their_layer_allows`
walks every module of a runner node against the runner table's mirror, `_RUNNER_PACKAGE_LAYERS`, failing on an edge the
row does not list and on any import of an edge module or the bare `blizzard.runner` package;
`test_every_runner_layer_edge_is_one_the_code_uses` fails on a declared edge no import walks, so the dict carries no
slack an unreviewed import could later pass along; `test_runner_package_layers_are_acyclic` holds that dict acyclic and
every package under `runner/` outside `api/`, `cli/`, and `store/`, and every top-level runner module outside the edge
modules, mapped to a node. `test_runner_layer_check_counts_every_import_form`,
`test_runner_node_check_catches_an_undeclared_package_or_module`,
`test_runner_unused_edge_check_catches_an_edge_no_import_walks`, and `test_runner_layer_cycle_check_catches_a_cycle`
prove each check fires on planted trees. The fix moves the shared type down into the lower package, or the dependent
code up; a new edge is a change to this table and the dict together, made only when an import needs it and only when
both stay acyclic, and an edge whose last import is removed leaves both. `scripts/check-registry-drift.py` check H fails
when either table here and its dict differ in a unit or an edge.

**Do.** `UNSET` lives in `blizzard/src/blizzard/hub/domain/kernel/unset.py`, so `config`, `garden`, and `work_items`
take it without importing `operations`. The requeue and attachment repository seams live in
`blizzard/src/blizzard/runner/leases/operator_requests.py`: the L6 claim and dormant steps read through
`IReadRequeueRepository` and `IReadAttachmentRepository`, and the L7 `operator/` services import the write seams from
there. `WorktreeGitError` sits beside `IWorktreeGit` in `runner/environments/worktree.py`, so
`lifecycle/judgement/git_commits.py` names no `internal/` module.

**Don't.** `runners/registration.py` importing a chunk port under `TYPE_CHECKING` — an L1 package reaching up into L2 —
or `from blizzard.hub.domain.chunk import Chunk` through a re-exporting `chunk/__init__.py`. `runner/auth/roles.py`
importing `RunnerConfig` — a concept package reaching an edge; it takes a `RolePolicy` instead.

**See also.** `bzh:domain-core` governs what every domain package may not import outward; `bzh:shared-kernel` governs
the `foundation/` vocabulary both daemons' domains share with `wire/`, and the rules both daemons evaluate identically.
