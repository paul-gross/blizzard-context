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

**Rule.** Business rules live in a domain layer that depends on nothing outward — no FastAPI, SQLAlchemy, click, httpx2,
dishka, filesystem, or network — with frameworks, stores, and transports outside it, depending inward. The registry
interface (`blizzard.foundation.registry.interface`) is not a framework: an area's `wiring.py`, under `hub/domain/` or
in a runner concept package, imports it to declare the area's ports and services, and never dishka itself.

**Why.** A domain core free of outward dependencies is unit-testable with no store or server, and survives a framework
swap untouched.

**Exception.** A harness binding package (`runner/harness/claude_code/`, `runner/harness/opencode/`,
`runner/harness/opencode_v2/`) is an adapter, not a concept package: it may bind a process or the filesystem, so it is
exempt from `tests/guards/test_layering.py`'s check on the `os`, `shutil`, `subprocess`, and `tempfile` imports and
still held to its check on the framework packages — fastapi, starlette, sqlalchemy, click, and httpx2. The binding set
is named explicitly, so a new binding fails `tests/guards/test_layering.py` until it is named. Any other module's
stdlib-driver import needs a reasoned entry in the per-module exemption map in `tests/guards/test_layering.py`, which
admits only the packages it names; an entry whose module no longer imports a package it admits is stale and fails the
check. Pure path arithmetic (`posixpath`, `PurePosixPath`) needs no exemption. The binding packages sit outside the
disk-call rule (`blizzard/contracts/ast-grep/rules/runner-domain-core-disk-calls.yml`) as they sit outside the driver
check. A read of prose shipped inside the package itself (the harness prompt and workspace-prompt sample files) carries
a per-site `# ast-grep-ignore` with its one-line reason, never a module-level exemption, since those modules also hold
domain code; a suppression whose site no longer matches fails the structural gate.

**Scope.** A runner domain-core module is any module of a `bzh:domain-package-layers` runner node outside an `internal/`
package (`_runner_domain_core_files`): a concept package's public surface holds its models, ports, and the services
carrying its rules, and the adapter binding a framework or driver sits in its `internal/`.

**Detect.** A domain module importing any of those packages, or a business rule reachable only through a store or HTTP
app. `tests/guards/test_layering.py` fails the unit tier on a `hub/domain/` module, or a runner domain-core module,
importing fastapi, starlette, sqlalchemy, click, httpx2, dishka, os, shutil, subprocess, or tempfile. The ast-grep rule
in `blizzard/contracts/ast-grep/rules/runner-domain-core-disk-calls.yml` fails a runner domain-core module calling
`exists`, `is_dir`, `is_file`, `resolve`, or `iterdir` with no argument, or `mkdir`, `read_text`, `write_text`, `glob`,
or `unlink` with any; it reads the call's shape only, with no typing, so a zero-argument call of one of those names on a
non-Path receiver is matched too. It does not see any other pathlib method (`open`, `stat`, `rename`, `touch`,
`read_bytes`, `write_bytes`, …), builtin `open`, or a call through a stored bound method — it narrows disk I/O in the
domain core, it does not prove its absence. The layer gate already keeps every such module off `blizzard.runner.store`
and `blizzard.runner.api`, which no row lists. The same layer walker fails a `hub/domain/` module importing
`blizzard.hub.config` or `blizzard.hub.delivery`, in any import form.

**Do.** `blizzard/src/blizzard/hub/domain/` and the runner's concept packages (`runner/leases/`, `runner/lifecycle/`,
`runner/tracing/`, …) import no web, ORM, or CLI package; `hub/api/`, `hub/store/`, `runner/api/`, and `runner/store/`
depend on them, never the reverse. The hub-JWKS seam `IJwksCache` sits in `runner/auth/jwks_cache.py`; its httpx2
binding sits in `runner/auth/internal/http_jwks_cache.py`, built only in the app composition root. The runner's FastAPI
federation router lives at `runner/api/federation.py`, not under `runner/auth/`. A config value the hub domain reads is
a domain-owned type the config edge builds (`hub/config.py` parses and renders; the domain holds the value). A domain
service types a delivery collaborator by a domain Protocol, as `ApplyService` does with `IHubStepWake`.

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
re-check that turns a lost race into the domain error, and the store's own freshness refusal are orchestration and
adapter concerns, not the rule restated — a store never judges the rule itself (`bzh:store-refuses-stale`,
[./system-shape/exclusive-writes.md](./system-shape/exclusive-writes.md)). The rule binds where a decision is made, not
its form: a pure function the service calls already complies.

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
`blizzard/exemplars/python/exemplar/hub/domain/permits/` ([../exemplars/index.md](../exemplars/index.md)) — the split as
reference code: the model deciding, the service orchestrating, and a route mapping each refusal.

## Dependency inversion (`bzh:dependency-inversion`)

**Rule.** The inner layer owns the interface and the outer implements it — the domain declares the Protocol seam, and
the store, forge, harness, or workspace adapter satisfies it.

**Why.** An inner-owned interface makes the outer layer a plug the inner never names: swapping a store or forge
(`bzh:pluggable-seams`) touches only the adapter, and tests substitute fakes by type.

**Detect.** A domain service importing a concrete adapter, or a Protocol defined in the adapter package and imported
inward.

**Do.** `blizzard/src/blizzard/hub/domain/chunk/ports/` declares per-concept read/write Protocol pairs (for example
`IReadChunkRecordRepository` and `IWriteChunkRecordRepository`) alongside read-only seams such as `facts`;
`ChunkRecordStore` in `blizzard/src/blizzard/hub/store/internal/chunk_record_store.py` implements that pair
structurally, one adapter per seam, and the domain never imports any of them.

**Don't.** A domain module that imports `ChunkRecordStore` directly.

**See also.** `blizzard/exemplars/python/exemplar/hub/store/internal/permit_store.py`
([../exemplars/index.md](../exemplars/index.md)) — the reference for this seam: the domain-owned ports in the exemplar
`permits/model.py`, the `internal/` adapter implementing them, registered in the exemplar `store/wiring.py`, and the
area's `permits/wiring.py` aliasing the ports onto it; read it when building a repository.

## Dependency injection (`bzh:dependency-injection`)

**Rule.** Nothing constructs its own collaborators — every dependency is injected. A long-lived process has one
composition graph: process-scoped collaborators are built once and injected into both its served app and its driver.
Short-lived CLI commands have their own roots.

CLI wiring is in transition, and a command is wired one of two ways. An unmigrated command — the hub's local verbs
(`init`, `migrate`, `host`, `config import-legacy`, `config check-forges`, `secret rotate-key`) and the runner CLI —
keeps its body under a `*/cli/` directory as such a root: it wires collaborators once, inline, at the top, without
joining the hosted process graph. The `OperatorGroup` and `_RunnerGroup` `invoke` methods are roots of the same kind. A
migrated command — every hub client verb — declares its collaborators by type and takes only those instances, from a
validated `COMMAND`-lifetime container that `blizzard/src/blizzard/cli/command_root.py` builds per invocation over the
shared (`cli/wiring.py`) and hub client (`hub/cli/wiring.py`) areas, composed by `hub/cli/command.py`. The carrier's
values, the operator trace and the connection options enter that container as borrowed contexts it never closes; what
the command owns is closed as it ends, on success and on failure. A verb declaring no `collaborators` takes the
`CliContext` alone. A new collaborator is born in its area's `wiring.py` and named at its verb. The container composes
only the shared and hub client areas on its own: a verb whose collaborator lives in any other area also passes that
area's `register` as `area=` to its command class. An unmigrated command keeps inline wiring until its own migration
moves it.

Either way a command resolves what a test may swap from `ctx.find_object(<carrier>)`, and defaults to the production one
when the invoker handed none; a test hands its own through `CliRunner.invoke(obj=...)`. A module-level factory a test
patches is not a seam. The shared carrier is `CliCollaborators` in `blizzard/src/blizzard/cli/collaborators.py`, the CLI
trees' one httpx2 import: every command builds its HTTP client through the carrier's `client_factory` and takes httpx2's
types (`Client`, `Response`, the error classes) from that module, never from httpx2. The root groups pass the resolved
carrier into `OperatorTrace` and `WorkerSession` as required arguments, and a hub verb's `CliContext` holds its factory.
`runner/cli/runtime.py`'s `init` resolves its own hub-clients carrier the same way, keeping the HTTP default out of the
`runner` group so a worker verb never loads a daemon's stack; the carrier also holds the `host` verb's process and
harness-bundle builders, which only `runtime.py` — a composition root — may import. A runner verb resolves the shared
carrier extended with the child-process launcher, the loopback transport, and the OpenCode 2 service transport from
`runner/cli/children.py`, and reads its clocks, launcher, and transports from that one carrier, so a test hands HTTP,
launcher, and transport fakes in one `obj`.

**Why.** One process graph prevents independently wired app and driver collaborators from diverging, and lets tests
substitute a fake store, a virtual clock, and a mock forge without patching module globals.

**Scope.** The injected clock (`bzh:injected-clock`) is a member of this rule, not an exception to it. The CLI-root half
reaches a helper a command's own root calls into rather than repeating, provided the root passes in whatever varies, and
it is wider than the mechanical roster: `tests/guards/test_layering.py::_COMPOSITION_ROOTS` stays the narrower set of
modules that may import `internal/` (`bzh:internal-visibility`) or `blizzard.runner.composition` — `cli/command_root.py`
among them — and a CLI module outside it is not a violation.

**Detect.** A service instantiating a store, client, clock, or subprocess runner in its own body, or a module-level
singleton read directly. `tests/guards/test_layering.py` fails the unit tier on any of:

- `blizzard.runner.composition` imported, in any form, anywhere outside the composition roots named below — fail-closed,
  with no per-name exemption; the module is a wiring root, not a seam a collaborator reaches into.
- A `hub/` or `runner/` module — outside its own connections seam — acquiring `self._engine` directly instead of taking
  the injected `HubStoreConnections` / `RunnerStoreConnections` collaborator (`bzh:dependency-inversion`'s exemplar).
- Duplicate construction or engine acquisition in the hosted hub graph across its app, composition, runtime, and tool
  roots — a second copy of a process-scoped collaborator. Independent short-lived roots remain separate.
- `build_stores`, `build_production_harnesses`, or `HarnessHealthCache` called anywhere under `blizzard/src/blizzard/`
  other than the host's composition modules (`runner/composition.py`, `runner/host_root.py`) and a runner area's
  `wiring.py` that imports the registry interface — a second copy of the runner's process graph.
- A concrete runner-store adapter (a `*Store` class under `runner/store/internal/`) named anywhere under
  `blizzard/src/blizzard/` other than the host's composition modules and a `wiring.py` of the adapter package's own in
  `runner/store/`.
- A hub store acquisition inside a registered factory or resource, or inside any wiring module; a class the hub registry
  owns constructed again in a hub root file.
- An offline hub or runner verb or tool, such as the event-log opener or `tools.invariants`, taking its capability from
  anything but a registered provider. The opener gets it through `open_store_backed`; each invariant checker comes from
  its store wiring's bounded registered factory over borrowed connections.
- An engine opened under `runner/cli/` or in `runner/runtime.py` at a site the gate's shrink-only allowlist does not
  list, or a listed site that no longer opens one — the stopped-host verbs read the store through the composition's
  readers.

The hub's container is held by `tests/guards/test_hub_graph.py` and `tests/guards/test_container_boundaries.py`, over
the checks in `tests/support/container_guards.py`; each check carries a planted violation it fails:

- The real hub registry, store-backed and store-free, builds, and declares no second owner, no lifetime off its scope
  path, no alias onto a doubled owner, no two roles over one key, and no defaulted constructor.
- Every route's `FromDishka` dependency resolves at the lifetime the route runs in: a tenant service only on a tenant
  route.
- The registry, in every graph shape, declares no legacy leaf or bag, and no registered provider or service takes a
  generic resolver or process handle — `Resolver`, `HubProcess`, `TenantContainers` or `OwnedChild`, however wrapped.
- No module under `blizzard/src/blizzard/` names a services bag (`BAG_NAMES`) in an import, a definition, a name, or an
  attribute.
- No hub root — `hub/process_root.py`, `hub/app.py`, `hub/composition.py` — and no CLI root — `cli/command_root.py`,
  `hub/cli/command.py` — calls a registration verb; each composes areas and orchestrates lifecycles, and the areas'
  wiring registers.
- A wiring module imports no other area's wiring and no adapter, other than an adapter package's own `wiring.py` naming
  its `internal/`; a runner area's `wiring.py` imports only the registry interface and its own package. The process
  roots, the two CLI roots among them, compose them all.
- dishka is imported only under `foundation/registry/internal/`, and from `dishka.integrations.fastapi` under the route
  edges `hub/api/` and `runner/api/`.
- A child scope opens only through the registry's own opener.

The runner host's container is held by `tests/guards/test_host_graph.py`, over the same checks; each carries a planted
violation it fails:

- The production host registry (`register_host`) builds, and declares no second owner, no lifetime off `HOST_LIFETIMES`,
  no alias onto a doubled owner, no two roles over one key, and no defaulted constructor.
- Every host-root route's `FromDishka` dependency resolves from the host's process scope, and no `/runners/{id}` route
  takes one.
- The host-free graph (`open_host_free`) refuses every host-root route's `FromDishka` dependency as absent, so a host
  service missing from its area's `register_absent` fails the gate rather than answering `500`.
- Its legacy leaves are inventoried, not refused, while the runner children hold them.

Migrated commands are held by three more modules. `tests/guards/test_command_graph.py` walks the `hub` tree: it fails a
verb that is neither a `HubCommand` nor one of the named local verbs, a client verb's graph that does not build on the
`COMMAND` lifetime, and a declared collaborator nothing registers; over the `hub status` registry it also fails a
missing dependency, a second owner, another lifetime, an alias onto a doubled owner, two roles over one key, a defaulted
constructor, a parameter taking a generic resolver or process handle, and a legacy declaration.
`tests/unit/hub/cli/test_client_verb_imports.py` runs one verb of each client group in a fresh interpreter: it loads no
daemon app or store stack, no other group's module and no other area's wiring, beyond the shrink-only exceptions that
module records. `tests/unit/hub/cli/test_status_imports.py` pins the exact CLI modules `hub status` loads.

Four ast-grep rules in `blizzard/contracts/ast-grep/rules/` hold the CLI's HTTP seam (`blizzard:structural-gate`):

- `cli-httpx-confined` fails any httpx2 import under the three CLI trees (`cli/`, `hub/cli/`, `runner/cli/`) other than
  `blizzard/src/blizzard/cli/collaborators.py`.
- `cli-patch-not-seam` matches test calls of the form `patcher.setattr(...)` whose first argument is a string matching
  its `blizzard.` CLI-path regex; it does not cover builtin `setattr` calls.
- `cli-refusal-body-confined` catches specific `detail` reads from a JSON response, status reads in a function that
  passes the same response to `refusal_of` (except inside a `RunnerDaemon.reach` with block), and raw JSON reads inside
  an `if` whose condition calls `refusal_of` on that response. It applies outside
  `blizzard/src/blizzard/cli/refusal.py`; it is not an exhaustive detector of refusal-body reads
  ([`bzh:clients-read-problem-types`](./system-shape/fleet-wire.md)).
- `hub-cli-answer-decoded` fails any `.json()` call under `blizzard/src/blizzard/hub/cli/`: a hub answer is read through
  the decoder ([`bzh:clients-decode-answers`](./system-shape/fleet-wire.md)).

One Ruff rule beside them holds the OpenCode 2 service seam: `TID251` bans `UrllibServiceTransport` in every
`runner/cli/` module except `runner/cli/children.py`, which builds the production one. It is scoped to that one concrete
adapter, not to transports in general.

**Do.** The hub process composes its graph in a container; the runner host serves from a container over its host root
and still hands its legacy-built collaborators down in frozen dataclasses. Thread-confined engines and clients can
remain independent, but belong to the same process graph with explicit lifetimes. The hub's container is the direction
(`decision:adopt-di/container`): one validated graph refuses a missing dependency, a second owner, or a lifetime off its
scope path when it is built, not when a request first reaches it. In the hub:

- `blizzard/src/blizzard/hub/process_root.py` is the hub's composition root. `register_hub` declares, over the plain
  recording registry, the scope inputs, each store adapter, and each area over the adapter `Ref` the store wiring hands
  it — the tenant store wiring returns the invitation store's `Ref`, which `hub/auth/wiring.py` aliases its write port
  onto — and `registered()` hands a root a fresh registry holding that graph; `build_store_backed` and
  `build_store_free` open the validated container over the borrowed connections, clock, settings graph, boot config,
  tracing handle, environment, hub actions, and packaged graph and system-artifact loaders. Registering and building are
  separate steps, so a stand-in root reuses `register_hub` and adds an area before it builds.
- The store wiring registers every store adapter and transaction primitive, at the tenant or the process lifetime, among
  them the tenant's `IHubTransactions`. The hub settings ports are the members of the borrowed settings graph,
  registered in `hub/settings/wiring.py`.
- A new hub service is born in its area's `wiring.py`, beside the concept it serves
  (`hub/domain/garden/findings/wiring.py`, `hub/domain/graph/wiring.py`): the area aliases its read and write ports onto
  the adapter `Ref` it is handed and registers its services by class, naming no adapter and no other area's wiring. An
  adapter is registered in its own package's `wiring.py` (`hub/store/wiring.py`), the one module beside its `internal/`
  that names the adapter. The store-free or settings-less graph declares each absent port, and a route that reaches one
  answers the store's unavailability. The hub identity area is adopted this way, born in `hub/auth/wiring.py`; the
  pre-admission auth dependencies take named process services through `FromDishka` under `@inject_sync`. Branch-gated
  services use optional keys that alias the canonical owner when available and yield `None` in the store-free graph;
  consumers that require storage take the plain absent key and receive its unavailability.
- When a lower area takes a sequence of collaborators that areas above it define, the lower area declares the key and
  the highest such area's wiring provides it, so no import runs upward: the urgency lifecycle takes
  `UrgencyReferenceClearings`, which `hub/domain/cadence/wiring.py` composes from the garden and cadence clearings.
- A process-scoped registered service that reads tenant state takes a typed tenant accessor, a role type the process
  root binds over `TenantContainers` once the process is built, never a bag or a generic resolver: the trace store's
  `StepHydrations` is the reference, resolving each tenant's `StepHydration` from that tenant's scope; the close drain,
  cadence, event-derivation, annotation and graph-reconciliation passes reach each tenant the same way. A value the root
  decides at boot is registered from a `register_hub` switch with `Registry.optional`, and its consumers take
  `T | None`: the trace and egress sweeps the roster reads, and the clock controls a controlled process clock serves.
- A route takes each service it calls through `FromDishka[...]` under `@inject_sync`, resolved through the request's
  resolver: the process scope on every route, and on a tenant route a request scope beneath the admitted tenant's scope
  (`hub/api/resolution.py`, entered through `tenant_bound`).
- The hub's lifecycle owners and passes are registered in their areas' wiring: the action loop, step wake and action
  pass driver, the open tenants, readiness, tenant administration and teardown, the close drain, and the sweeps and
  their roster (`hub/domain/sweeps/wiring.py`). `hub/process_root.py` only composes them, handing each area the `Ref`s
  it needs and binding the typed tenant accessors once the process is built.
- Every hub collaborator is resolved from the container. No hub root makes an individual registration, and the hub
  registry declares no legacy leaf or bag.

The hub's hosted lifetimes and the runner host:

- `hub/cli/runtime.py` owns the hosted engine and platform tracing handle. It acquires the instrumented connections
  graph through `hub/composition.py` and shares it with settings and the hosted app; it disposes the engine and shuts
  down tracing after their users finish.
- `build_hosted_app` in `blizzard/src/blizzard/hub/app.py` consumes those borrowed resources and opens its process over
  them with `open_store_backed`, and each configured adapter is born in its area's wiring, not passed in. It resolves
  every owner it boots and serves from the process — the action loop, readiness, the boot checks, each open tenant's
  reads through `TenantContainers.every_open`, and the roster `lifespan` times — and its hosted cleanup is the process
  close alone: the tenant scopes close their configured clients on the running action loop, then the process scope stops
  the loop, before `hub host` disposes the borrowed engine and tracing.
- `blizzard/src/blizzard/hub/composition.py` builds only the borrowed context `hub host` supplies — the settings graph,
  the engine and its connections, the system clock, and the boot fact export (`build_egress_boot`) — and the flow
  driver. A tenant's services are resolved from that tenant's container scope (`TenantContainers` in
  `hub/scopes/tenants.py`), never from the unscoped process (`bzh:tenant-scoped-store`,
  [./system-shape/tenancy.md](./system-shape/tenancy.md)). A typed tenant accessor (above) may also be built by its
  entrypoint, with `build_flow_driver` as the reference.
- The runner host graph in `blizzard/src/blizzard/runner/composition.py`: `build_host_process` builds the host — its
  `HostStores`, telemetry receiver and records reconcile, once per host — and no runner, and `compose_runner` composes
  one `RunnerProcess` over it. Each `RunnerProcess` references that host graph and holds runner-bound collaborators, its
  attempt handle and one host-kind write seam for external-usage attempts. That seam uses runner-bound connections to
  write an unregistered host's sampled attempt and its runner-scoped outbound report in one transaction. Each runner's
  periodic loop is wired in `blizzard/src/blizzard/runner/loop_wiring.py`.
- `blizzard/src/blizzard/runner/host_root.py` is the host's composition root, and the running host serves from it.
  `register_host` declares the borrowed `HostProcess`, the `HostConfig` and `RunnerCompose` options a runner child is
  composed from, `HostRunnerSet`, each runner child's one context value `BuiltRunner`, the named legacy leaves, and each
  adopted area's `register` call. `HostRoot.serving` opens it: `build_hosted_app_over_process` in
  `blizzard/src/blizzard/runner/app.py` opens it over the host `runner host` built, and `open_standalone` and
  `build_runner_process` open it over a host of one for the standalone verbs, the self-built loop tick and
  `runner tick`, whose caller owns and closes what it opened; `build_hosted_app` serves such an opened host. A stand-in
  root reuses `register_host`, adds an area, and hands its registry to `open_host` before the build.
- `HostRunnerSet` in `runner/composition.py` alone opens and closes runner children, one new child for every start
  attempt, and a runner's graph closes before its child on drain, abandon and host stop. The served app closes the root
  — its runner children, then its process scope — before `runner host` closes the borrowed host.
- Until each area's slice adopts it, what the host and each runner are still built by is reached through named legacy
  leaves that only the root declares, through `LegacyRegistry`: a runner child holds its `RunnerProcess` as a
  runner-lifetime leaf, built as the child opens so a bad entry fails the child's opening, and the host's usage-limit
  store and clock are process-lifetime leaves over the borrowed host. An adopted area depends on a leaf only by the
  `Ref` the root hands it, or by its type.
- A new host or runner service is born in its area's `wiring.py`, which imports only the registry interface and its own
  package: `runner/throttle/wiring.py` aliases the floor-clear write onto the usage-limit `Ref` the root hands it and
  registers `SubscriptionFloorClearService` at the process lifetime, and declares it absent through `register_absent`.
  An app built without a host root serves its host routes from the host-free graph `open_host_free` opens, each host
  service declared absent; a route that reaches one answers `503` through the runner app's `ServiceAbsent` handler.
- A host-root route serving an adopted host service takes it through `FromDishka[...]` under `@inject_sync`, resolved
  through the host's process scope: `host_request` (`runner/api/resolution.py`) attaches that resolver on the host-root
  lanes, never on a `/runners/{id}` lane, and never closes it. The floor clear takes `SubscriptionFloorClearService` so;
  it and the other host routes still read `RunnerWiring` for what no area has adopted, and a `/runners/{id}` route still
  reads its runner's seams.
- `HostRunnerSet` is the one exception to a registered service taking no `OwnedChild`: the host root hands it the
  process scope through `bind` once it is built, and it opens runner children beneath that scope and resolves nothing
  through it.

Helpers a CLI root calls into rather than repeating:

- `blizzard/src/blizzard/runner/cli/daemon.py`'s `Door.uds_client` builds the local UDS client, through the carrier's
  factory, that both `RunnerDaemon.reach` and `daemon_holding` need, shared rather than duplicated; each caller passes
  the `Door` its command resolved from the context, so no call site reads a trace source or a factory ambiently.
- `blizzard/src/blizzard/runner/cli/runtime.py`'s `read_host_stores` builds a host-scoped read-only store bundle and
  disposes the engine on exit, so `runner/cli/prompt.py`'s `_effective_prompt_lane` calls into it instead of repeating
  the construction outside a composition root.

Example — a click command taking its swappable collaborators from the invoker:

```python
@click.command()
@click.pass_context
def init(ctx: click.Context, ...) -> None:
    collaborators = InitCollaborators.of(ctx)
    # ...
    with collaborators.host_clients(config.hub_url) as host_clients:
        host = register_host(config, collaborators, host_clients, store, rerun)


# A test passes an InitCollaborators containing its fake clients and session store as obj.
```

**Don't.** A coordinator that calls `ChunkRecordStore()` or `datetime.now()` inside a method; a module-level
`client_factory` that a test monkeypatches. A hub services bag (`TenantServices`, `HubServices`, `HubCore`) brought back
to carry a new service; a registered factory taking a `Resolver` or `HubProcess` to reach the services it uses.

## Narrow seams and step context Protocols (`bzh:narrow-seams`)

**Rule.** Type each collaborator's dependencies as the seams it uses, never as a bundle that carries every seam. Only a
composition root, the runner's loop driver, or an API or CLI edge holds a bundle. Adding a runner loop step, or giving a
step something new to read — a probe, a config value, a store — takes three moves:

1. Put the logic in a step module, never inline in a `steps.py` phase: the driver holds `LoopContext` only to hand it to
   step modules. Combining a new check's result with existing ones is step logic too: the phase makes one call into a
   step module and branches on that one result.
2. Add the member to that module's context Protocol and to `LoopContext`.
3. Keep a sentinel for that Protocol in `runner/loop/context.py`: the assignment
   `_<name>_conforms: type[<Protocol>] = LoopContext`.

A pluggable seam such as a probe (`bzh:pluggable-seams` in
[./system-shape/pluggable-seams.md](./system-shape/pluggable-seams.md)) is one member the step's Protocol declares; it
never stands in for that Protocol.

**Why.** A bundle parameter hides what a collaborator touches: a test must build the whole bundle, and a reviewer cannot
tell from the signature which state a change can reach. A narrow seam states the dependency in the type, so pyright
fails any caller that supplies less and any member the collaborator starts reading without declaring it.

**Scope.** The bundles are the runner's store bundles — `RunnerStores`, `RunnerReadStores`, and the `IReadRunnerStore` /
`IWriteRunnerStore` Protocols they satisfy, all in `blizzard/src/blizzard/runner/stores.py` — and the loop's
`LoopContext`. The composition roots are those `bzh:dependency-injection` names; a host-root route taking `FromDishka`
names each service it calls, never a bundle. The loop driver is `runner/loop/context.py`, `runner/loop/tick.py`, and
`runner/loop/steps.py`; the edges are everything under `runner/api/` and `runner/cli/`. On the hub, every module is in
scope, with no roster: each takes every service through the container and holds no bag. Tests are out of scope: they act
as their own roots.

**Detect.** A step or domain service typed by a bundle while its body reads a handful of the bundle's members.
`tests/guards/test_layering.py` fails the unit tier on each of these, and plants a temporary tree to prove each check
fires:

- `LoopContext` named, in any form, under `blizzard/src/blizzard/` outside the loop driver and the composition roots.
- A store-bundle name under `runner/` outside `stores.py`, the loop driver, the composition roots, `runner/api/`, and
  `runner/cli/`.
- A composition root placed under `runner/loop/`, or a `runner/loop/` module importing `blizzard.runner.composition`.
- A `ctx` parameter or `ctx:` field under `runner/`, outside the driver, roots, and edges, not typed by a `Protocol` its
  own module declares; or a parameter or field of any other name typed — bare, module-qualified, or wrapped in a union —
  by `LoopContext` or another module's step context.
- A Protocol used to type a scanned `ctx` with no annotated assignment of `LoopContext` to `type[<Protocol>]` in
  `runner/loop/context.py`. The guard checks the assignment's annotation and value, not its target name; pyright checks
  that `LoopContext` satisfies the Protocol.

`tests/guards/test_container_boundaries.py` fails the unit tier on any module under `blizzard/src/blizzard/` that names
a hub services bag in an import, a definition, a name, or an attribute.

The fix is to declare what the module reads, never to widen an exemption.

**Do.** A loop step module declares its own context Protocol beside its steps, inheriting the Protocol of any step it
hands its context to, and `runner/loop/context.py` proves the driver's bundle satisfies it:

```python
# runner/lifecycle/attempt.py: hands its ctx to a spawn step
class AttemptContext(SpawnContext, Protocol): ...

# runner/loop/context.py
if TYPE_CHECKING:
    from blizzard.runner.lifecycle.attempt import AttemptContext

    _attempt_conforms: type[AttemptContext] = LoopContext
```

A domain service takes one keyword parameter per repository seam:
`TakeoverService(clock, process, *, takeover, elicitations, local_api_url, harnesses_for_lease, workspaces, events=None)`.

**Don't.** A domain service taking `stores: RunnerReadStores` to read seven of its repositories, or a step dataclass
with a `ctx: LoopContext` field. A new gate added inline to a `steps.py` phase, reading a new `LoopContext` member that
no step Protocol declares.

**See also.** `bzh:seam-size-ceiling` ([./system-shape/seam-size.md](./system-shape/seam-size.md)) caps how wide one
Protocol grows; this rule governs which Protocols a collaborator depends on.
`blizzard/exemplars/python/exemplar/runner/disk/floor.py` ([../exemplars/index.md](../exemplars/index.md)) — a loop step
and its own context Protocol as reference code, with its sentinel in the exemplar `runner/loop/context.py`.

## Internal visibility (`bzh:internal-visibility`)

**Rule.** A package's `internal/` is private to that package: only the package that directly contains it, and every
module below that package, may import from it. Composition roots may import any `internal/`.

**Why.** `internal/` holds a package's adapters and helpers; a sibling package importing one couples to a concrete class
instead of the package's public surface, so the adapter can no longer change without breaking its neighbor.

**Scope.** Tests are out of scope: they are white-box and act as their own roots. The composition roots are the modules
`bzh:dependency-injection` names; there is no per-import exemption — a crossing is fixed, or its importer is a root.

**Detect.** A module outside `<pkg>/` importing a module under `<pkg>/internal/`, by absolute, relative, or
`from <pkg> import internal` form. `tests/guards/test_layering.py`'s generic check fails the unit tier on it, over every
`internal/` under `blizzard/src/blizzard/`, naming the owner.

**Do.** `blizzard/src/blizzard/foundation/store/batching.py` is the public home of the id-batching both daemons' stores
share.

**Don't.** A store adapter in one package importing an adapter or helper from another package's `internal/`, rather than
taking the seam or a public module.

**See also.** `bzh:sibling-adapter-independence` ([./repository-access.md](./repository-access.md)) applies a narrower
repository boundary even when both adapters are under the same `internal/` and this visibility rule permits the import.

## Shared kernel (`bzh:shared-kernel`)

**Rule.** `blizzard/src/blizzard/wire/`, `foundation/`, and `auth_core/` are the shared kernel both daemons import, and
none of them imports a blizzard package outside it — `hub`, `runner`, `cli`, or `tools` — directly or transitively.
Every vocabulary type a wire model carries has exactly one definition, in the kernel (`foundation/`, one module per
vocabulary); the daemons import it from there, with no re-export, mirror, or mapping layer. The business rules over that
vocabulary stay in each daemon's domain (`bzh:domain-core`), with one carve-out: a rule both daemons must evaluate
identically, so that neither accepts what the other refuses, lives once in `foundation/` as pure functions or methods of
frozen kernel types, with no I/O and no collaborators; a rule only one daemon applies stays in that daemon's domain.
Within a daemon, a `wire/` model is named only at its app boundary, which maps it to domain models (`bzh:data-roles`,
[./data-roles.md](./data-roles.md)).

**Why.** A wire model importing a daemon's domain type makes importing the wire load that daemon, so the hub loads
runner modules and the runner loads hub modules through it. The wire stops being the one place a vocabulary changes, and
a second copy of an enum — or of a predicate both daemons apply — drifts unseen until the runner accepts what the hub
refuses.

**Exception.** Two one-sided names stay in the kernel by decision, and a sweep does not re-raise them:
`Flags.fleet_answer` and `Flags.with_fleet_answer`, the two ends of one hub→runner exchange kept together as one
protocol; and `is_tenant_name`, which restates the wire's `TENANT_NAME_PATTERN` and `TENANT_NAME_MAX_LENGTH` and stays
beside them.

One effectful workflow also stays in the kernel by decision, and a sweep does not re-raise it against the purity clause:
`rotate_keys` in `blizzard/src/blizzard/foundation/secrets/rotation.py`, with that module's `_Target` key view and
`_reseal` step, which serve only it. It is an operational sequence over the key-provider, cipher, and repository seams —
it drives the key source's `mint`, `promote`, and `prune` through `IRotatableKeyProvider` — not a pure business rule;
the kernel owns it so that sequence has one implementation. Its effects run in a fixed order. It reads every supplied
repository's sealed rows and refuses a referenced key generation the key source lacks, before it mints. It takes the
target generation from the provider — freshly minted, or the current one where the source's generations are fixed
outside the process — and re-seals each repository through that repository's own atomic `reseal`. It promotes only once
every repository has succeeded, then re-reads the referenced generations and prunes. Recovery is staged, with no
rollback across tenants and key files: a later repository can fail after an earlier one's re-seals committed, which
leaves the old generation current and the ciphertext already written readable through the target generation. `_reseal`
is effectful as well — the cipher reads key material through its provider and draws a fresh nonce — and the
deterministic parts, `uncovered_key_ids` and `stale_seals`, are pure functions in
`blizzard/src/blizzard/foundation/secrets/sealing.py`. The exception names this workflow alone: it admits no other
`foundation/` I/O, no other effectful shared rule, and no class of workflows. It answers the purity clause only: whether
one daemon alone reaches the module is the layering test's allowlist question, and the entry there stands on its own
reason.

**Detect.** `tests/guards/test_layering.py` fails the unit tier on a kernel module importing a non-kernel blizzard
package, on any kernel module import loading a `hub`, `runner`, `cli`, or `tools` module in a fresh interpreter, and on
a hub or runner composition root loading the other daemon. The same module checks `from` imports of the kernel
vocabulary names explicitly listed in `_MOVED_HOMES` against their defining modules. The ast-grep rule
`bzh:shared-kernel` catches specific vocabulary shapes under `wire/`: classes extending `Enum`, `StrEnum`, or `IntEnum`,
and certain unqualified `Literal` annotations and aliases with two or more values. A closed vocabulary typed as plain
`str` is not seen and stays a judgment call. The layering test also fails a `foundation/` or `auth_core/` module that no
`wire/` module reaches and that only one daemon does. Reach follows imports through the kernel, and a `cli` module
counts as the sides of the daemon modules that reach it; a `tools` module is no side, and `internal/` and docstring-only
`__init__` modules are not judged. The fix moves the module into that daemon's domain, or gives it an allowlist entry
with its reason, which the check drops once the entry is stale. The check sees whole modules only: a one-sided rule
living as a name in a shared module is not caught and stays a judgment call. A business rule in `foundation/` that only
one daemon applies is that daemon's rule placed in the kernel; the fix moves it into that daemon's domain. One both
daemons apply that takes a repository, clock, or client, or performs I/O, is made pure, with the facts and the instant
passed in as values. The rotation workflow the Exception names is not such a rule, and stays effectful.

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
`blizzard/src/blizzard/runner/lifecycle/`, `blizzard/src/blizzard/runner/transcripts/`. Hub delivery's domain types and
repository seams live in `hub/domain/delivery/`, separate from the delivery adapters. Inside
`blizzard/src/blizzard/hub/domain/`, the hub's business rules split the same way into the concept packages
`bzh:domain-package-layers` orders (`chunk/`, `execution/`, `operations/`, `garden/`, …); the runner's concept packages
sit directly under `blizzard/src/blizzard/runner/`, ordered by the same rule's runner table.

**Don't.** `models/`, `routers/`, and `crud/`, where one chunk change touches three unrelated directories.

## Domain package layers (`bzh:domain-package-layers`)

**Rule.** Put every hub-domain module in one of the concept packages under `blizzard/src/blizzard/hub/domain/`, and
every runner module outside the edges in one of the runner's nodes; import another package only where the importer's
table row allows it. Every hub package may also import `kernel`.

The data lives in the code, not here: the hub domain's table is `_DOMAIN_PACKAGE_LAYERS` and the runner's is
`_RUNNER_PACKAGE_LAYERS`, both in `blizzard/tests/guards/test_layering.py`, each mapping a node to the nodes its row may
import. Every hub package may also import `kernel`; the runner has no shared node. In the runner, each harness binding
package and `harness/wiring` are nodes of their own (the binding ids come from the harness catalog); any other
`runner/<first segment>` is that segment, so `config_table.py`, `route_paths.py`, and `stores.py` are the top-level
modules in the graph.

A row only points down: every node a row may import sits strictly lower in the graph than the row's own node, `kernel`
aside, so the dict is acyclic and no edge runs sideways between two nodes of one level. Declare an edge only when an
import needs it.

Import a module by its full module path, and a name from the module that defines it: a package's surface is its modules
outside `internal/` (`bzh:internal-visibility`), and its `__init__.py` re-exports nothing.

**Why.** Edges that only point down let a package change without breaking any package below it, and leave no
package-level cycle for a `TYPE_CHECKING` guard or a function-level import to hide. One import path per name means a
moved type leaves no second spelling behind.

**Scope.** The table governs imports of `blizzard.hub.domain.*` made by modules under `hub/domain/`; imports inside one
package are free. Adapters — `hub/api/`, `hub/store/`, the composition roots, tests — depend inward on any package
(`bzh:domain-core`), but they too take each name from the module that defines it. The runner table governs imports of
`blizzard.runner.*` made by modules of its nodes; imports inside one node are free. `runner/api/`, `runner/cli/`,
`runner/store/`, the top-level modules `_RUNNER_EDGE_MODULES` names in `blizzard/tests/guards/test_layering.py`, and
tests are edges: they depend inward on any node, and no node imports them — a concept package takes config values by
injection (a settings object or a structural Protocol), never `RunnerConfig`.

**Detect.** A domain module importing a package its row does not list — at module level, inside a function, under
`TYPE_CHECKING`, or by relative import — or importing the bare `blizzard.hub.domain` umbrella; a `.py` directly under
`hub/domain/` other than `__init__.py`, or a package directory the table does not declare; a package `__init__.py` that
imports a name to re-export it; any module under `src/` or `tests/` importing a name from a domain module that only
imports it; a declared edge no import walks. `tests/guards/test_layering.py` fails the unit tier on all of them, for the
hub domain and the runner alike: one checker walks each tree for the crossings, the unused edges, the undeclared
packages and modules, and the second spellings, and a cycle check holds each dict acyclic with every node declared. Both
trees' package `__init__.py` files are held to a docstring and the `__future__` import. Planted-tree cases in the same
module prove each check fires on both tree shapes. On a runner crossing, any import of an edge module or the bare
`blizzard.runner` package fails too. The fix moves the shared type down into the lower package, or the dependent code
up; a new edge is a change to its dict, made only when an import needs it and only when the dict stays acyclic, and an
edge whose last import is removed leaves it.

**Do.** `UNSET` lives in `blizzard/src/blizzard/hub/domain/kernel/unset.py`, so `config`, `garden`, and `work_items`
take it without importing `operations`. The hub action catalogue is `graph`'s (`hub/domain/graph/actions.py`), since
graph validation reads it, while the visit and the effects an action is handed sit in `actions`, a package above `chunk`
and `graph` that the delivery domain and delivery edge import. The requeue and attachment repository seams live in
`blizzard/src/blizzard/runner/leases/operator_requests.py`: the `lifecycle` claim and dormant steps read through
`IReadRequeueRepository` and `IReadAttachmentRepository`, and the `operator` services import the write seams from there.
`WorktreeGitError` sits beside `IWorktreeGit` in `runner/environments/worktree.py`, so
`lifecycle/judgement/git_commits.py` names no `internal/` module.

**Don't.** `runners/registration.py` importing a chunk port under `TYPE_CHECKING` — `runners` reaching up into `chunk` —
or `from blizzard.hub.domain.chunk import Chunk` through a re-exporting `chunk/__init__.py`. `runner/auth/roles.py`
importing `RunnerConfig` — a concept package reaching an edge; it takes a `RolePolicy` instead.

**See also.** `bzh:domain-core` governs what every domain package may not import outward; `bzh:shared-kernel` governs
the `foundation/` vocabulary both daemons' domains share with `wire/`, and the rules both daemons evaluate identically.
