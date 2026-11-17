# Take fixtures, don't build them (`bzh:service-fixtures-only`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity. The sections after the
skeleton — the worlds, a stack held across a describe block, the traced companion, and its export barrier — are the
contract the Rule slot requires, not skeleton drift.

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

## A held stack

`test.use({ held: '<name>' })` on one describe block, run in order on one worker
(`test.describe.configure({ mode: 'default' })`), gives its tests one fresh hub and one runner host instead of one each,
built by the first test and stopped when the worker ends; `once(name, produce)` runs `produce` for the first test to ask
and hands every later one its result, so a night too long to repeat runs once under as many titled proofs as it earns. A
worker that restarts after a failure builds the stack and the night again. A test outside the block holds no stack, and
`once` refuses it.

## The traced companion

For a fleet-trace assertion, register a second case with `traced(originalTitle, async ({ traceSink, ... }) => ...)`,
imported from `tests/harness/fixtures.ts`. **Use `traced`, not a hand-extended `test`, `runnerOtlp`, or two
independently configured sinks.** It names the case `originalTitle_traced`, gives it a `fresh-hub`, configures both hub
and runner exporters to its one test-owned `traceSink`, and runs the companion's scenario once. Keep the ordinary
behavioral case on its shared hub, without trace assertions; the companion asserts only trace facts, not a second copy
of the behavioral assertions.

## The export barrier

A companion runs on a controlled stack (`test.use({ clockMode: 'controlled' })` in a describe of its own, so the
ordinary cases keep the system clock). It drives the hub itself, with the harness's controlled-hub wait for every wait
that crosses a hub-executed node, and reads fleet spans once, after `flushTraces(host)`, then applies the
dictionary-driven trace oracle. `flushTraces` steps the hub's export sweep, which covers fleet spans only: platform and
worker-command spans ride a batch processor on machine time, and only shutdown flushes them. A companion therefore reads
those after the host-then-hub shutdown barrier below, and never compares a platform timestamp with a fleet timestamp:
the two planes run on different clocks, so it bounds by what it stepped, not by a time cutoff. The system-clock poll of
`traceSink.spans()` for the hub step root and runner invocation is the fallback for a companion that cannot run
controlled; a completed host step alone is not an export barrier for both daemons.

A frozen clock puts many records on one instant, so a companion moves the clock where an assertion compares instants or
durations (a gate's end against `resolved_at`, the backlog wait against `blizzard.chunk.backlog_ms`), and the
controlled-hub wait moves it on each turn so step roots do not tie.

Before a negative leak scan of the full export, stop the companion's `runnerHost` and `freshHub` in that order, then
read `traceSink.spans()` again. Their shutdown flushes close the worker-command and hub-export windows; the earlier
fleet-span read alone does not prove that a later command span cannot still arrive.
