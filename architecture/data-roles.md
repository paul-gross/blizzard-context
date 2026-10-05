# Every data class declares its data role (`bzh:data-roles`)

What role a blizzard data class plays, how it declares one, and the constraint each role is held to. Slot skeleton:
`canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity; [Roles](#roles),
[App boundary](#app-boundary), and [Inferred roles](#inferred-roles) define the contract the `Rule` requires. Part of
the [architecture guidance](./index.md).

## Rule

Mark every data class — a class decorated `@dataclass` in any spelling, or one listing `NamedTuple` among its bases,
nested and function-local classes included — under `blizzard/src/blizzard/` with exactly one role marker from
`blizzard/src/blizzard/foundation/roles.py`: `@domain_model`, `@dto`, `@adapter_model`, or `@collaborator`. A class
whose shape already infers its role ([Inferred roles](#inferred-roles)) carries no marker, and the class then meets the
constraint its role sets ([Roles](#roles)).

- Import the marker by name (`from blizzard.foundation.roles import dto`) or through the module
  (`from blizzard.foundation import roles`, then `@roles.dto`), at module top level. A marker the scan cannot trace to
  `blizzard.foundation.roles`, or whose name the module rebinds later, does not count; nor does the call form `@dto()`.
- Put the marker above `@dataclass`. The order is a convention, not a check.
- Mark each class itself: a subclass of a marked class declares its own role, since a role never inherits.
- Define a data class with a `class` statement. One built by a call — `NamedTuple(...)`, `namedtuple(...)`,
  `make_dataclass(...)`, `dataclass(cls)` — is a violation, because no marker can reach it.
- A marker on a class that is neither a `@dataclass` nor a `NamedTuple`, or on one whose role is inferred, is a
  violation.

## Why

The app's edges speak DTOs, its core speaks domain models, and each adapter speaks its outside system's format in
private; a declared role keeps each shape where it belongs, so a wire contract never becomes a domain signature and a
row or a subprocess's payload never becomes a port's. Inferring what a class's shape already says keeps the marker from
saying it twice.

## Roles

| Role          | Marker           | Is                                                                                                                                             | Constraint                                                                                                                         |
| ------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Domain model  | `@domain_model`  | A concept of the domain, with or without rules: what a repository reconstitutes, what a service takes and returns, what a rule reasons on      | No field mentions a collaborator ([Inferred roles](#inferred-roles)) at any depth; outside the [app boundary](#app-boundary)       |
| DTO           | `@dto`           | The app's contract with the outside: a request, a response, a command's arguments or output, a payload between the two daemons                 | Inside the [app boundary](#app-boundary); every method is a constructor, a projection, or a property ([DTO methods](#dto-methods)) |
| Adapter model | `@adapter_model` | A shape private to one adapter: an outside system's format it parses or writes — a table row, a subprocess's output — or its own working state | No Protocol member mentions it; outside the [app boundary](#app-boundary)                                                          |
| Collaborator  | `@collaborator`  | A class other code calls to do work — a port's implementation, a driver over infrastructure, a flow over IO                                    | Has a method or property beyond its constructors ([Collaborator](#collaborator))                                                   |

Choose the role by asking, in order:

1. Does other code call it to do work? A `@collaborator` — never a `@domain_model` for want of another slot.
2. Does it sit in an [app boundary](#app-boundary) package? A `@dto`.
3. Is it private to one adapter — an outside system's format it parses or writes, or its own working state — mapped to
   domain models before anything else sees it? An `@adapter_model`. A shape two adapters share, or one the port's caller
   sees, is a domain model.
4. Otherwise, a `@domain_model` — a methodless one included.

Crossing a Protocol inside the app never makes a class a DTO. A repository returns domain models, taking ids, the domain
models a write persists, and the filter, sort, and page values a query narrows by; a page, a count, a criteria object,
and a service's outcome are domain models too. A controller resolves ids through read repositories, calls a service with
domain models, and maps the domain models it gets back to a DTO; an adapter on the far side of a wire — the runner's hub
client — maps the DTOs it receives to domain models the same way.

### App boundary

The packages where the app meets the outside. Each holds DTOs and the code that maps them; no domain model or adapter
model lives here.

| Package                             | Edge                                                                   |
| ----------------------------------- | ---------------------------------------------------------------------- |
| `blizzard/src/blizzard/wire/`       | The hub↔runner contract and the hub's HTTP responses — pydantic models |
| `blizzard/src/blizzard/hub/api/`    | The hub's HTTP routes                                                  |
| `blizzard/src/blizzard/hub/cli/`    | The hub's operator commands — their arguments and rendered output      |
| `blizzard/src/blizzard/runner/api/` | The runner's HTTP surface: the board, worker hooks, telemetry intake   |
| `blizzard/src/blizzard/runner/cli/` | The runner's operator commands                                         |
| `blizzard/src/blizzard/cli/`        | The top-level `blizzard` command                                       |

A DTO is named only inside the boundary, by a composition root (`bzh:dependency-injection`), and by the adapters that
send or receive the `wire/` contract itself:

- `blizzard/src/blizzard/runner/hub/` — the runner's hub client, which maps the wire to the runner's domain models
- `blizzard/src/blizzard/hub/events/broker.py` and `blizzard/src/blizzard/runner/events/broker.py` — the two daemons'
  SSE brokers, which publish the wire's frame payloads
- `http_archived_transcript_repository.py` and `segment_projection.py` under
  `blizzard/src/blizzard/runner/transcripts/internal/` — the runner's read-back of its own shipped transcript segments

Any other module importing a `wire/` model is a violation ([Detect](#detect)). A format the boundary already validated
on ingest — a transcript's turns — is rebuilt from the store into domain models, like any row. A JSON format a worker
writes into an artifact and the hub stores raw — a garden delta — is parsed at the boundary behind a port the domain
declares (`blizzard/src/blizzard/hub/domain/garden/formats.py`'s `IGardenFormats`, bound in
`blizzard/src/blizzard/hub/api/garden_formats.py`).

### Domain model

The collaborator test covers every field, own and inherited, `InitVar` and `init=False` fields included and `ClassVar`
excluded, at any depth: `tuple[IHarnessAdapter, ...]` blocks a domain model even though it infers no orchestration.
`Literal` values and `Annotated` metadata are not read. A domain model is held by rules over its own data
(`bzh:domain-orchestration-split`); having none yet does not make it a DTO.

### Adapter model

An adapter model never leaves its adapter: the adapter maps it to and from the domain models its port speaks.

- **Protocol crossing**: no Protocol member mentions the adapter model's class name at any depth. That covers parameters
  (`*args`, `**kwargs`, and keyword-only included), returns, and class-level annotated attributes, through generics,
  unions, `Callable` arguments, string annotations, module-level type aliases expanded by name, and import aliases
  (`import NodeRow as R`) resolved to the class they bind.
- **Bare names**: the crossing check matches the bare class name, so a domain model sharing an adapter model's name
  fails it too once a Protocol names the domain model. Rename one of the two.
- **Store rows**: a store adapter's row sits under its store package's `internal/` (`hub/store/internal/**`,
  `runner/store/internal/**`), where `bzh:internal-visibility` already keeps it out of every seam's reach.

### DTO methods

| Kind        | Admitted                                                                                                                                                                                   |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Constructor | `__init__`, `__new__`, `__post_init__`; a `@classmethod` or `@staticmethod` whose return annotation is the class's own name or `Self`, directly or as a union arm (`-> Foo \| None`)       |
| Projection  | A plain, non-async, undecorated `def` that takes only `self`, has a return annotation other than `None`, assigns or deletes nothing rooted at `self`, and never calls `object.__setattr__` |
| Property    | A `@property` or `@cached_property` getter                                                                                                                                                 |

Anything else is behavior: a setter or deleter, an unannotated method, a method taking any argument (`__eq__` included),
an async method, a classmethod returning another type, or a method bound by class-body assignment — a lambda, a
`staticmethod(...)` or `classmethod(...)` call, or a function the module declares. Behavior on a boundary class is a
rule leaking to the edge: it moves to the domain model the DTO is mapped from, or to a `@collaborator`.

### Collaborator

The marker declares what the shape cannot show: a class whose fields are plain values yet whose job is work, such as
`MigrationRunner(script_location, url)`. A class whose fields do show it — one requiring a port, a clock, or a driver
handle — infers orchestration instead and carries no marker.

- **Work**: it declares, or inherits from a class under `blizzard/src/blizzard/`, a method or property other than a
  constructor; a methodless carrier is never a collaborator.
- **Clocks**: a data class named as a clock (`…Clock`) whose shape infers no role is a `@collaborator`, never a
  `@domain_model` or a `@dto`.
- **Wherever named**: a `@domain_model` field mentioning it fails the domain-model check, and a data class requiring it
  infers orchestration.

## Inferred roles

| Inferred role | The class's shape                                                                                                              |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| port          | `Protocol` is among its bases                                                                                                  |
| error         | A base is an exception class, or a name ending `Error`, `Exception`, or `Warning` that no module under `src/blizzard` declares |
| enum          | A base is `Enum`, `IntEnum`, `StrEnum`, `Flag`, `IntFlag`, or `ReprEnum`                                                       |
| pydantic      | A base is `BaseModel`, `RootModel`, or `BaseSettings` — a DTO by shape, held to the [app boundary](#app-boundary)              |
| orchestration | A data class with a field annotated directly as a collaborator, under the guard below                                          |

- **Collaborator**: a port — an `I[A-Z]…` name that some Protocol under `blizzard/src/blizzard/` declares, so
  `IPv4Network` is not one — or a clock, any name ending `Clock`; a driver handle, any type imported from `fastapi`,
  `starlette`, `sqlalchemy`, `click`, or `httpx`, the packages `bzh:domain-core` keeps out of a domain core; a class
  marked `@collaborator` or that itself infers orchestration; or a Protocol that exposes a collaborator through an
  attribute or property of its own or of a Protocol base — a runner step's context Protocol is one, so a step holding it
  is orchestration.
- **Port names**: the `I` prefix declares a port, so a Protocol that only describes data a consumer reads — a view
  shared by domain models, such as `HarnessSection` — takes a plain name.
- **Directly**: the whole annotation, or an arm of a union, `Optional`, `Annotated`, `InitVar`, or `Final` — never a
  container's type argument. Inherited fields count.
- **Guard**: such a field infers orchestration only if the constructor requires it (no default, no `default_factory`,
  not `init=False`), the class's own methods read it as `self.<field>`, or every field of the class is a collaborator. A
  defaulted port field no method reads exempts nothing.
- **Name resolution**: a class name resolves to its declaration in the same module, else to the one in the module it is
  imported from, else to every class of that name under `blizzard/src/blizzard/`. A base or field type confers a role
  only if every candidate has it.

## Detect

`tests/test_layering.py` fails the unit tier on each constraint, one check per test:

- `test_every_data_class_declares_exactly_one_role` — a data class with no marker or two, a marker on an inferred-role
  class or a non-data class, or a data class built by a call.
- `test_a_dto_lives_at_the_app_boundary` — a `@dto` or a pydantic model outside the [app boundary](#app-boundary), or a
  `@domain_model` or `@adapter_model` inside it.
- `test_only_the_boundary_names_a_wire_model` — a module outside the boundary, the wire adapters, and the composition
  roots importing from `blizzard.wire`.
- `test_an_adapter_model_crosses_no_protocol` — a Protocol member naming an `@adapter_model`.
- `test_a_domain_model_holds_no_collaborator` — a `@domain_model` field mentioning a collaborator: a port, a clock, a
  driver handle, or a `@collaborator`, at any depth.
- `test_a_dto_has_only_constructors_projections_and_properties` — a `@dto` method that is none of the three kinds, or
  one bound by assignment.
- `test_a_collaborator_does_work_and_every_clock_is_one` — a `@collaborator` with no method or property beyond its
  constructors, or a clock-named data class carrying another marker.

The same file's `test_role_marker_check_*`, `test_boundary_check_*`, `test_wire_import_check_*`,
`test_adapter_model_check_*`, `test_domain_model_check_*`, `test_dto_check_*`, and `test_collaborator_check_*` cases
prove each check catches its violation and admits its conforming shape; `tests/test_foundation_roles.py` covers the
markers themselves.

The gate reads only `@dataclass` and `NamedTuple` classes, so a reviewer asks of a hand-written class that stores fields
in its `__init__`: is this a data class that left the gate? The fix is to make it a data class with its role. Of an
`@adapter_model`, a reviewer asks whether a module outside its adapter imports it — then it is a domain model the
adapter should map to. Of a `@domain_model`, a reviewer asks whether its methods are rules over its own data, or work
that makes it a `@collaborator`.

## Do

`blizzard/src/blizzard/hub/domain/garden/findings/trend.py::Trend` is what the trend service returns, so it is a
`@domain_model`; the route maps it to `blizzard/src/blizzard/wire/garden_trend.py::TrendView`, the DTO the board reads.
`blizzard/src/blizzard/hub/domain/garden/findings/model.py::FindingPage`, what `IReadFindingRepository.list_page`
returns, is a `@domain_model` beside the `Finding`s it pages.

`blizzard/src/blizzard/hub/store/internal/graph_store.py::NodeRow` is the graph store's codec for a node row, and
`blizzard/src/blizzard/runner/harness/opencode/shapes.py::OpenCodeRunEvent` is one line `opencode run --format json`
emits; each adapter maps its own to the domain models its port speaks, so both are `@adapter_model`s no Protocol names:

```python
@adapter_model
@dataclass(frozen=True)
class NodeRow:
    def values(self, node: Node, *, graph_id: str) -> dict[str, Any]: ...
    def of(self, row: Any, *, choices: list[Choice]) -> Node: ...
```

`blizzard/src/blizzard/foundation/store/migrations.py::MigrationRunner` holds a path and a URL and drives Alembic, so it
is a `@collaborator`; `blizzard/src/blizzard/tools/invariants.py::QueryCheck` holds a SQLAlchemy `Connection`, so it
infers orchestration and carries no marker.

## Don't

- A `@dto` on a repository's return, a service's result, or a port's argument because it crosses a Protocol — the
  Protocols inside the app are not its boundary.
- A domain service taking or returning a `wire/` model, so the runner↔hub contract becomes a domain signature — the
  controller or the hub client maps it.
- A store Protocol method returning its adapter's `@adapter_model`, so the row's columns become the seam's contract.
- An argument dropped or an annotation changed on a DTO's method so it reads as a projection, or a method moved off a
  class into a free function so the class passes as a DTO.
- A `@domain_model` on a test clock, a migration runner, a file or socket adapter, or a wiring holder because no other
  marker seemed to fit.

## See also

- `bzh:domain-core` and `bzh:shared-kernel` ([./clean-architecture.md](./clean-architecture.md)) — which layer a data
  class belongs in; the markers sit in the shared kernel so both daemons and `wire/` can use them.
- `bzh:domain-takes-objects` and `bzh:controller-read-only` ([./repository-access.md](./repository-access.md)) — the
  edge that resolves ids and maps domain models to DTOs.
- `bzh:internal-visibility` ([./clean-architecture.md](./clean-architecture.md)) — why a store row under a store's
  `internal/` stays out of reach of the package's neighbors.
