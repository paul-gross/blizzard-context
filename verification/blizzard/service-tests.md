# Authoring Playwright service tests

These rules bind specs under `blizzard/tests/service/`, in three Playwright folders: `hub/` (the hub's own wire),
`runner/` (a real runner host on a mock hub), and `fleet/` (a real runner host on a real hub). Beside them, the tier's
pytest half keeps the cases whose subject is Python itself in four packages these rules do not bind: `harnesses/` (the
harness adapters against the mock binaries), `wire/` (the Python client's wire parity), `mock_fleet/` (the mock fleet's
own routes and seeding), and `store_migration/` (moving an older build's store onto this one). Start at the service
method's [command detail](./commands/test-tiers/service.md) for the paired task commands and at
[tier-rules.md](./tier-rules.md) for allocation and statement guards. The harness owns fixtures in
`tests/harness/fixtures.ts`, clients in `tests/harness/client/`, and project and profile discovery in
`tests/playwright.config.ts`, `tests/harness/projects.ts`, and `tests/harness/profiles.ts`.

Each spoke owns one contract a spec author meets; descend to the one the question names.

| Spoke                                                        | Read when…                                                                                                                                    |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| [`./service-tests/fixtures.md`](./service-tests/fixtures.md) | Declaring what a spec takes from the harness — which world its folder gets — or asserting on the traces a fleet scenario exports              |
| [`./service-tests/clients.md`](./service-tests/clients.md)   | Reaching a daemon, a runner host, a forge origin, or an export from a spec, or running a pasteable command a worker printed                   |
| [`./service-tests/state.md`](./service-tests/state.md)       | Choosing an isolation level, pulling a mock-fleet lever, or calling a fleet route that needs a registered runner                              |
| [`./service-tests/time.md`](./service-tests/time.md)         | A spec has to wait for something, move time, step a host, or prove that something did not happen                                              |
| [`./service-tests/surfaces.md`](./service-tests/surfaces.md) | Building or reading state, and whether a store, a host directory, or a cold `init` may be touched, and when                                   |
| [`./service-tests/profiles.md`](./service-tests/profiles.md) | A spec needs a hub or host configured differently — a setting, an environment variable, a harness, a bundle or stub, or a subscription sample |

Grow this rulebook when a port settles a practice a capable service-test author would not discover independently.
