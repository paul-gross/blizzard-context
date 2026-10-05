# Every data class declares its data role (`bzh:data-roles`)

What role a blizzard data class plays, how it declares one, and the constraint each role is held to. Slot skeleton:
`canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity; [Roles](#roles) and
[Inferred roles](#inferred-roles) define the contract the `Rule` requires. Part of the
[architecture guidance](./index.md).

## Rule

Mark every data class — a class decorated `@dataclass` in any spelling, or one listing `NamedTuple` among its bases,
nested and function-local classes included — under `blizzard/src/blizzard/` with exactly one role marker from
`blizzard/src/blizzard/foundation/roles.py`: `@domain_model`, `@entity`, `@dto`, or `@collaborator`. A class whose shape
already infers its role ([Inferred roles](#inferred-roles)) carries no marker, and the class then meets the constraint
its role sets ([Roles](#roles)).

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

A table row, a concept that carries rules, a carrier for one boundary crossing, and a class that does work are
indistinguishable as dataclasses, so a store's row leaks through its Protocol, behavior accretes on a carrier, and
infrastructure passes for a concept, with nothing to flag any of them. A declared role turns each into a fact the
layering gate holds to its constraint, and inferring what a class's shape already says keeps the marker from saying it
twice.

## Roles

| Role         | Marker          | Is                                                                                                                          | Constraint                                                                               |
| ------------ | --------------- | --------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Domain model | `@domain_model` | A concept that carries rules, or that other code reasons about as a noun of the domain                                      | No field mentions a collaborator ([Inferred roles](#inferred-roles)) at any depth        |
| Entity       | `@entity`       | One table row's shape, or a store adapter's codec for a row or a column — a persistence row                                 | Lives under a store package's `internal/`, and no Protocol member mentions it            |
| DTO          | `@dto`          | A message about something, for one crossing: a port's input or output, a page, a query, a service result, a view, a payload | Every method is a constructor, a projection, or a property ([DTO methods](#dto-methods)) |
| Collaborator | `@collaborator` | A class other code calls to do work — a port's implementation, a driver over infrastructure, a flow over IO                 | Has a method or property beyond its constructors ([Collaborator](#collaborator))         |

When the table leaves a class ambiguous:

- A methodless class that could be concept or carrier is a `@dto` when a Protocol, an API, the CLI, or the wire is where
  it lives or goes, and a `@domain_model` otherwise.
- A would-be DTO with any method the DTO test rejects is a `@domain_model` when the method is a rule over the class's
  own data, and a `@collaborator` when it does work: reads or writes a file, a socket, a process, or the network, or
  drives a store or a framework.
- A class that implements a port, drives infrastructure, or wires collaborators together is a `@collaborator`, never a
  `@domain_model` for want of another slot.
- A row shape outside a store package is marked by the role it plays where it sits — usually `@dto` — never `@entity`.

### Domain model

The collaborator test covers every field, own and inherited, `InitVar` and `init=False` fields included and `ClassVar`
excluded, at any depth: `tuple[IHarnessAdapter, ...]` blocks a domain model even though it infers no orchestration.
`Literal` values and `Annotated` metadata are not read.

### Entity

**Entity means a persistence row, not DDD's identity-bearing entity.** It is private to its store adapter, which maps it
to the domain model or DTO its Protocol speaks:

- **Store package**: the file's directory path under `blizzard/src/blizzard/` contains a `store` segment and, below it,
  an `internal` segment — `hub/store/internal/**`, `runner/store/internal/**` — so `bzh:internal-visibility` keeps the
  entity out of every seam's reach.
- **Protocol crossing**: no Protocol member mentions the entity's class name at any depth. That covers parameters
  (`*args`, `**kwargs`, and keyword-only included), returns, and class-level annotated attributes, through generics,
  unions, `Callable` arguments, string annotations, module-level type aliases expanded by name, and import aliases
  (`import NodeRow as R`) resolved to the class they bind.
- **Bare names**: the crossing check matches the bare class name, so a DTO sharing an entity's name fails it too once a
  Protocol names the DTO. Rename one of the two.

### DTO methods

| Kind        | Admitted                                                                                                                                                                                   |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Constructor | `__init__`, `__new__`, `__post_init__`; a `@classmethod` or `@staticmethod` whose return annotation is the class's own name or `Self`, directly or as a union arm (`-> Foo \| None`)       |
| Projection  | A plain, non-async, undecorated `def` that takes only `self`, has a return annotation other than `None`, assigns or deletes nothing rooted at `self`, and never calls `object.__setattr__` |
| Property    | A `@property` or `@cached_property` getter                                                                                                                                                 |

Anything else is behavior: a setter or deleter, an unannotated method, a method taking any argument (`__eq__` included),
an async method, a classmethod returning another type, or a method bound by class-body assignment — a lambda, a
`staticmethod(...)` or `classmethod(...)` call, or a function the module declares. Such a class is a `@domain_model` or
a `@collaborator`, as [Roles](#roles) decides.

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
| pydantic      | A base is `BaseModel`, `RootModel`, or `BaseSettings` — a DTO by shape                                                         |
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
- `test_an_entity_lives_in_a_store_package_and_crosses_no_protocol` — an `@entity` outside a store package's
  `internal/`, or named by a Protocol member.
- `test_a_domain_model_holds_no_port_or_clock` — a `@domain_model` field mentioning a collaborator.
- `test_a_dto_has_only_constructors_projections_and_properties` — a `@dto` method that is none of the three kinds, or
  one bound by assignment.
- `test_a_collaborator_does_work_and_every_clock_is_one` — a `@collaborator` with no method or property beyond its
  constructors, or a clock-named data class carrying another marker.

The same file's `test_role_marker_check_*`, `test_entity_check_*`, `test_domain_model_check_*`, `test_dto_check_*`, and
`test_collaborator_check_*` cases prove each check catches its violation and admits its conforming shape;
`tests/test_foundation_roles.py` covers the markers themselves.

The gate reads only `@dataclass` and `NamedTuple` classes, so a reviewer asks of a hand-written class that stores fields
in its `__init__`: is this a data class that left the gate? The fix is to make it a data class with its role. The fix
for a rejected DTO method is the marker [Roles](#roles) gives the class, never a method reshaped until it passes. Of a
`@domain_model`, a reviewer asks whether its methods are rules over its own data, or work that makes it a
`@collaborator`.

## Do

`blizzard/src/blizzard/hub/store/internal/graph_store.py::NodeRow` is the graph store's codec for a node row; it maps to
and from the domain `Node` the store's Protocol speaks, so it is an `@entity` no seam names:

```python
@entity
@dataclass(frozen=True)
class NodeRow:
    def values(self, node: Node, *, graph_id: str) -> dict[str, Any]: ...
    def of(self, row: Any, *, choices: list[Choice]) -> Node: ...
```

`blizzard/src/blizzard/hub/domain/garden/findings/model.py::FindingPage`, a port's output, is a `@dto`; `::Finding` is a
`@domain_model`, the concept even with no methods.

`blizzard/src/blizzard/foundation/store/migrations.py::MigrationRunner` holds a path and a URL and drives Alembic, so it
is a `@collaborator`; `blizzard/src/blizzard/tools/invariants.py::QueryCheck` holds a SQLAlchemy `Connection`, so it
infers orchestration and carries no marker.

## Don't

- An `@entity` on a `*Row` or `*Record` class under `hub/domain/` — mark the role it plays there, and let the name say
  what it carries.
- A store Protocol method returning its adapter's `@entity`, so the row's columns become the seam's contract.
- An argument dropped or an annotation changed on a DTO's method so it reads as a projection, or a method moved off a
  class into a free function so the class passes as a DTO.
- A `@domain_model` on a test clock, a migration runner, a file or socket adapter, or a wiring holder because no other
  marker seemed to fit.

## See also

- `bzh:domain-core` and `bzh:shared-kernel` ([./clean-architecture.md](./clean-architecture.md)) — which layer a data
  class belongs in; the markers sit in the shared kernel so both daemons and `wire/` can use them.
- `bzh:internal-visibility` ([./clean-architecture.md](./clean-architecture.md)) — why an entity under a store's
  `internal/` stays out of reach of the package's neighbors.
- `bzh:repository-split` ([./repository-access.md](./repository-access.md)) — the repository seams an entity never
  crosses.
