# Exemplars

Reference implementations in the `blizzard` repo. **Before writing or extending code or tests, read the row matching
what you are building.** When adapting an exemplar into production, read [conformance.md](./conformance.md).

A new concept package owes one thing no exemplar can show: its row in the layer table of the tree it joins —
`bzh:domain-package-layers` in [../architecture/clean-architecture.md](../architecture/clean-architecture.md) for a
hub-domain or runner package, and the hub app's unit table in
[../architecture/frontend-structure/placement.md](../architecture/frontend-structure/placement.md) for an Angular
feature folder.

Parent: [../index.md](../index.md).

## Hub

Under `blizzard/exemplars/python/exemplar/`.

| Exemplar                                                   | Copy it when you are…                                                                 |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `hub/domain/permits/model.py`                              | Adding a hub concept or changing its rules                                            |
| `hub/domain/permits/service.py`                            | Adding or changing a hub use case's orchestration                                     |
| `foundation/permits.py`                                    | Defining a vocabulary type shared across boundaries                                   |
| `hub/store/internal/permit_store.py`                       | Adding or extending a hub store adapter                                               |
| `hub/store/schema.py`                                      | Adding or changing a hub table's schema                                               |
| `hub/store/migrations/versions/20261015_0900_permits.py`   | Writing a hub migration that adds tables                                              |
| `hub/store/migrations/tests/20261015_0900_permits_test.py` | Testing a hub migration                                                               |
| `hub/api/permits.py`                                       | Adding or changing a hub HTTP route                                                   |
| `hub/api/refusals.py`                                      | Turning a domain refusal into an HTTP status                                          |
| `hub/api/permit_params.py`                                 | Resolving a path id to its loaded object, or a `404`, before a route calls the domain |
| `wire/permit.py`                                           | Adding or changing a wire model                                                       |
| `hub/composition.py`                                       | Wiring a new store and service into a tenant's services                               |
| `hub/graphs/scripts/land_clean.py`                         | Writing an `executor: hub` node's `run:` step script                                  |
| `hub/graphs/basic-development-workflow/prompts/`           | Writing a worker node's prompt, its judgement, or an edge's addendum                  |

## Runner

Under `blizzard/exemplars/python/exemplar/`.

| Exemplar                 | Copy it when you are…                                     |
| ------------------------ | --------------------------------------------------------- |
| `runner/disk/floor.py`   | Adding a runner loop step or changing what one acts on    |
| `runner/disk/model.py`   | Putting a runner decision in a pure function a step calls |
| `runner/loop/context.py` | Proving the loop's context satisfies a step's Protocol    |
| `runner/loop/steps.py`   | Registering a step with the loop                          |
| `runner/stores.py`       | Giving a runner step a store it reads or writes           |
| `runner/disk/probe.py`   | Putting an external driver behind a pluggable runner seam |

## Web

Under `blizzard/exemplars/web/`.

| Exemplar               | Copy it when you are…                  |
| ---------------------- | -------------------------------------- |
| `hub/src/app/permits/` | Adding or extending an Angular feature |

## Tests

Under `blizzard/exemplars/python/tests/`, except the Playwright row, which is a live spec under `blizzard/tests/`. A new
Playwright service spec also follows the [service-test rulebook](../verification/blizzard/service-tests.md).

| Exemplar                                              | Copy it when you are…                                |
| ----------------------------------------------------- | ---------------------------------------------------- |
| `blizzard/tests/service/hub/analytics-events.spec.ts` | Writing a Playwright service spec                    |
| `test_permit_rules.py`                                | Testing a domain model's rules                       |
| `test_permit_service.py`                              | Testing a use-case service                           |
| `test_permit_store.py`                                | Testing a hub store adapter                          |
| `test_permit_api.py`                                  | Testing a route's HTTP contract                      |
| `test_disk_floor.py`                                  | Testing a runner loop step across the moves it makes |
| `test_injected_clock.py`                              | Writing an architectural gate as a test              |

## Keeping them true

| Doc                                | Read when                                                 |
| ---------------------------------- | --------------------------------------------------------- |
| [conformance.md](./conformance.md) | Adding, changing, or adapting an exemplar into production |
