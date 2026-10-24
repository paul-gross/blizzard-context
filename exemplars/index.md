# Exemplars

Reference implementations to pattern new blizzard code off, kept in the `blizzard` repo under `exemplars/`. **Before
writing a new module, read the row matching what you are building and copy its shape** — its names, its layering, its
docstrings, and its comment density, which is the density your code should match. Each sits where its production
counterpart would, under `exemplar` in place of `blizzard`; a `# exemplar:` comment explains the exemplar itself and is
never copied.

A new concept package owes one thing no exemplar can show: its row in the layer table of the tree it joins —
`bzh:domain-package-layers` in [../architecture/clean-architecture.md](../architecture/clean-architecture.md) for a
hub-domain or runner package, and the hub app's unit table in
[../architecture/frontend-structure/placement.md](../architecture/frontend-structure/placement.md) for an Angular
feature folder.

Parent: [../index.md](../index.md).

## Hub

Under `blizzard/exemplars/python/exemplar/`.

| Exemplar                                                   | Copy it when you are…                                                                                                                                                                                                |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `hub/domain/permits/model.py`                              | Adding a hub concept, or a state, verb, rule, or refusal to one — its verb→allowed-states table, decision methods, facts, read/write ports, and errors                                                               |
| `hub/domain/permits/service.py`                            | Adding a use case — read the clock, let the model decide, hand the decision to a port, under the row lock when exactly one writer may win                                                                            |
| `foundation/permits.py`                                    | Defining a vocabulary type — an enum the hub domain also uses                                                                                                                                                        |
| `hub/store/internal/permit_store.py`                       | Adding or extending a hub store adapter — scoped reads and writes, batched and newest-fact reads, a lost insert race, a locked write                                                                                 |
| `hub/store/schema.py`                                      | Adding a hub table — tenant-led keys and uniqueness, an append-only facts table, the indexes its reads need                                                                                                          |
| `hub/store/migrations/versions/20261015_0900_permits.py`   | Writing a hub migration that adds tables                                                                                                                                                                             |
| `hub/store/migrations/tests/20261015_0900_permits_test.py` | Testing a migration, beside its revision — upgrade from its parent, the declared schema, re-run, downgrade                                                                                                           |
| `hub/api/permits.py`                                       | Adding a route — guards, path resolvers, the domain → view mapper, and each refusal mapped to its status                                                                                                             |
| `hub/api/refusals.py`                                      | Turning a domain refusal into an HTTP status                                                                                                                                                                         |
| `hub/api/permit_params.py`                                 | Resolving a path id to its loaded object, or a `404`, before a route calls the domain                                                                                                                                |
| `wire/permit.py`                                           | Adding a wire model — the `*Request` / `*View` / `*Response` taxonomy, envelopes, field comments, instants, `bzh:wire-sent-is-required`, and a response vocabulary field typed open (`bzh:open-response-vocabulary`) |
| `hub/composition.py`                                       | Wiring a new store and service into a tenant's services                                                                                                                                                              |
| `hub/graphs/scripts/land_clean.py`                         | Writing an `executor: hub` node's `run:` step script                                                                                                                                                                 |
| `hub/graphs/basic-development-workflow/prompts/`           | Writing a worker node's prompt, its judgement, or an edge's addendum                                                                                                                                                 |

## Runner

Under `blizzard/exemplars/python/exemplar/`.

| Exemplar                 | Copy it when you are…                                                                                                             |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| `runner/disk/floor.py`   | Adding a runner loop step, or giving one something new to read — its own context Protocol, and the move it acts on                |
| `runner/disk/model.py`   | Putting a runner decision in a pure function a step calls                                                                         |
| `runner/loop/context.py` | Proving the loop's context satisfies a step's Protocol                                                                            |
| `runner/loop/steps.py`   | Registering a step with the loop — the thin phase that makes one call into the step module                                        |
| `runner/stores.py`       | Giving a runner step a store it reads or writes                                                                                   |
| `runner/disk/probe.py`   | Putting a process, filesystem, or external-tool driver behind a pluggable seam — with its adapter in `internal/` and its selector |

## Web

Under `blizzard/exemplars/web/`.

| Exemplar               | Copy it when you are…                                                                                                                                                                               |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `hub/src/app/permits/` | Adding an Angular feature — a routed container, its model, a presentational view, its query and mutations, their specs, and an `openLookup` over a wire vocabulary (`bzh:frontend-open-vocabulary`) |

## Tests

Under `blizzard/exemplars/python/tests/`. For a new Playwright service spec rather than a Python exemplar, read the
[service-test rulebook](../verification/blizzard/service-tests.md); the rows below are Python files.

| Exemplar                 | Copy it when you are…                                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| `test_permit_rules.py`   | Testing a domain model's rules — by value, with no repository, clock, or fake                                    |
| `test_permit_service.py` | Testing a use-case service — a hand-written fake proved against its port, and a fixed clock                      |
| `test_permit_store.py`   | Testing a hub store adapter — a migrated store, tenant isolation, a duplicate insert, paging, a flat query count |
| `test_permit_api.py`     | Testing a route — each status and body its docstring promises                                                    |
| `test_disk_floor.py`     | Testing a runner loop step across the moves it makes                                                             |
| `test_injected_clock.py` | Writing an architectural gate as a test — a live scan plus planted trees proving its reach                       |

## Keeping them true

| Doc                                | Read when                                                                                      |
| ---------------------------------- | ---------------------------------------------------------------------------------------------- |
| [conformance.md](./conformance.md) | Adding or changing an exemplar — the gates it passes, its layout, and the `# exemplar:` device |
