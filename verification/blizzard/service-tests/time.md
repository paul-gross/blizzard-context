# Wait on the system (`bzh:service-waits-on-the-system`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity. The sections after the
skeleton — stepped hosts, controlled clocks, and the barriers a negative assertion waits on — are the contract the Rule
slot requires, not skeleton drift.

## Rule

Wait for an event or readable state, never a clock delay. For a negative assertion, wait for a barrier act that only the
expected behavior would emit before asserting its absence.

## Why

A sleep encodes machine speed; immediate absence proves only that the system has not acted yet.

## Detect

`tests/eslint.config.mjs` rejects `waitForTimeout`, `setTimeout`, `setInterval`, and `node:timers`, and under
`tests/service/` and `tests/ui/` rejects `Date.now()` and a zero-argument `new Date()`; review absence assertions with
no causal barrier, and review each reasoned disable for whether its subject really is elapsed time.

## Do

Await the event stream or poll the client for the state the case can name. A wait whose subject is a window ageing out
asks for `clockMode: 'controlled'`, advances the stack's clock past the window with `clock.advance`, steps the pass that
judges it, and reads the state. Every instant a spec builds comes from `clock.now()`.

## Don't

Sleep before asserting that no event was emitted. Poll with a deadline wide enough to cover a window.

## Stepped hosts and worker checkpoints

A `runnerHost` boots `stepped`: `step()` and `stepHost()` each resolve once the pass has completed, so a test steps,
then reads. It never waits on a timer for a pass the host would run on its own. The halted and multi-runner examples
live in `tests/service/runner/host-halted-runners.spec.ts`; their foreign-identity and persisted host-fact specimens
live in `tests/service/runner/store/host-halted-runners.spec.ts`.

Hold a mock worker's turn open at `workerCheckpoint`, not a sleep. Change a sample by `vendorUsage.set` on a credential
the spec minted, followed by `stepHost()`; [`./profiles.md`](./profiles.md) §Subscription samples owns what a sample is
made of.

## Controlled clocks

A test that needs time to move asks for a controlled stack with `test.use({ clockMode: 'controlled' })`; every other
test runs on the system clock, whose `clock.advance` and `clock.set` refuse. Only a `fresh-hub` test, a block that holds
its stack ([`./fixtures.md`](./fixtures.md) §A held stack), or a runner-world test may ask: a controlled stack moves
every daemon's clock, and a shared hub's belongs to other tests. It pairs only with stepped daemons, so a timed sweep
and a `runnerLoop: 'timed'` host are refused before any daemon starts. `clock.now()` is every spec's source of an
instant, controlled or not; a spec never reads the machine's clock itself. `clock.advance(seconds)` and
`clock.set(instant)` move the hub or mock hub, the runner hosts, the mock runners and forge, and the browser together,
and resolve once all have answered. On a controlled hub, `api.flowStep()` runs one flow-driver pass at `clock.now()`; it
is refused on a system stack. To drive a pending poll, advance to its due time, then step and read the public state. The
fleet test that steps the hub and the runner host is `tests/service/fleet/flow-turns.spec.ts`.

## The collector's decision barrier

In a `collectorTest` case, poll `collector.decision(traceId)` for the short trace while the worker is held at its
checkpoint. Its unmarked trace-specific probe reads the collector's cached sampling decision; only a returned `dropped`
is a barrier for asserting that later root and command spans were not forwarded. A received span and an empty forwarded
sink cannot establish that decision.

## The relay's outage barrier

To keep a hub outage open under an in-flight read, hold the `mockHubRelay` option's relay (`mockHub.relay`): stop the
hub, issue the read, and wait on the relay's `refusal()` as the barrier that the read is in flight. Restart the hub and
re-seed what the read needs, then release the relay. Releasing earlier lets a retry reach a hub that does not yet know
the caller, and that is refused for good, not retried.
