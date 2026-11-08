# Take fixtures, don't build them (`bzh:service-fixtures-only`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity. The sections after the
skeleton — the worlds, the traced companion, and its export barrier — are the contract the Rule slot requires, not
skeleton drift.

## Rule

Name the fixtures a test needs — tenant, project, clients, people, event stream, the `blizzard` CLI, a fresh hub's stop,
kill, start, and data-reset lifecycle, the OTLP sink, a real runner host (`runnerHost` and `runnerHosts`), a mock
worker's checkpoint (`workerCheckpoint`), and the clock (`clock`) — and import only `tests/harness/fixtures.ts`. A
runner-only test takes `runnerTest`'s own `mockHub` and `authStub` instead of any shared-hub fixture. Do not use
Playwright's built-in `request` or set shared state in `test.beforeAll`.

## Why

The harness fixtures own daemon lifetime, tenant routing, cleanup, and test isolation. A bare request context reaches no
tenant; file-wide mutable setup crosses parallel tests.

## Detect

`tests/eslint.config.mjs` rejects destructured `request`, harness imports other than fixtures, and
`test.beforeAll`/`test.afterAll` in service specs, and the wrong world per folder: `runnerTest` outside
`service/runner/`, `test` inside it, and `@playwright/test` itself anywhere. Review ad-hoc construction of a fixture's
resource.

## Do

Import `test` and `expect` from the harness fixtures and declare only the resources the case reads.

## Don't

Import a harness daemon helper or destructure `{ request }` from a Playwright test callback.

## One world per folder

Each folder takes one world. `service/hub/` and `service/fleet/` take `test`; `service/runner/` takes `runnerTest`,
which has no `isolation` option, so a runner spec declares none: its mock hub and host belong to that test alone. A
`service/fleet/` spec declares `fresh-tenant` at least, because a host enrolls only in a tenant of the test's own, and
`fresh-hub` when its subject is hub-wide. The fleet world's `runnerHost`, `runnerHosts`, `runnerHostClient` and
`runnerStream` are the runner world's, defined once and bound to the test's hub.

## The traced companion

For a fleet-trace assertion, register a second case with `traced(originalTitle, async ({ traceSink, ... }) => ...)`,
imported from `tests/harness/fixtures.ts`. **Use `traced`, not a hand-extended `test`, `runnerOtlp`, or two
independently configured sinks.** It names the case `originalTitle_traced`, gives it a `fresh-hub`, configures both hub
and runner exporters to its one test-owned `traceSink`, and runs the companion's scenario once. Keep the ordinary
behavioral case on its shared hub, without trace assertions; the companion asserts only trace facts, not a second copy
of the behavioral assertions.

## The export barrier

After finishing the scenario, poll `traceSink.spans()` until both the hub step root and runner invocation for that chunk
have arrived, then apply the dictionary-driven trace oracle. A completed host step alone is not an export barrier for
both daemons. A companion on a controlled stack exports on a stepped hub sweep instead: the fixture opens the export
before the test can move the clock, and `flushTraces(host)` returns once the sink holds every span, so the test reads
`traceSink.spans()` once rather than polling.

Before a negative leak scan of the full export, stop the companion's `runnerHost` and `freshHub` in that order, then
read `traceSink.spans()` again. Their shutdown flushes close the worker-command and hub-export windows; the earlier
root-and-invocation poll alone does not prove that a later command span cannot still arrive.
