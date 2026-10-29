# Authoring Playwright service tests

These rules bind specs under `blizzard/tests/service/`, in three folders: `hub/` (the hub's own wire), `runner/` (a real
runner host on a mock hub), and `fleet/` (a real runner host on a real hub). Start at the service method's
[command detail](./commands/test-tiers/service.md) for the paired task commands and at [tier-rules.md](./tier-rules.md)
for allocation and statement guards. The harness owns fixtures in `tests/harness/fixtures.ts`, clients in
`tests/harness/client/`, and project and profile discovery in `tests/playwright.config.ts`, `tests/harness/projects.ts`,
and `tests/harness/profiles.ts`.

## Take fixtures, don't build them (`bzh:service-fixtures-only`)

**Rule.** Name the fixtures a test needs — tenant, project, clients, people, event stream, the `blizzard` CLI, a fresh
hub's stop, kill, start, and data-reset lifecycle, the OTLP sink, a real runner host (`runnerHost` and `runnerHosts`),
and a mock worker's checkpoint (`workerCheckpoint`) — and import only `tests/harness/fixtures.ts`. A runner-only test
takes `runnerTest`'s own `mockHub` and `authStub` instead of any shared-hub fixture. Do not use Playwright's built-in
`request` or set shared state in `test.beforeAll`.

Each folder takes one world. `service/hub/` and `service/fleet/` take `test`; `service/runner/` takes `runnerTest`,
which has no `isolation` option, so a runner spec declares none: its mock hub and host belong to that test alone. A
`service/fleet/` spec declares `fresh-tenant` at least, because a host enrolls only in a tenant of the test's own, and
`fresh-hub` when its subject is hub-wide. The fleet world's `runnerHost`, `runnerHosts`, `runnerHostClient` and
`runnerStream` are the runner world's, defined once and bound to the test's hub.

**Why.** The harness fixtures own daemon lifetime, tenant routing, cleanup, and test isolation. A bare request context
reaches no tenant; file-wide mutable setup crosses parallel tests.

**Detect.** `tests/eslint.config.mjs` rejects destructured `request`, harness imports other than fixtures, and
`test.beforeAll`/`test.afterAll` in service specs, and the wrong world per folder: `runnerTest` outside
`service/runner/`, `test` inside it, and `@playwright/test` itself anywhere. Review ad-hoc construction of a fixture's
resource.

**Do.** Import `test` and `expect` from the harness fixtures and declare only the resources the case reads.

**Don't.** Import a harness daemon helper or destructure `{ request }` from a Playwright test callback.

## Call through clients (`bzh:service-clients-only`)

**Rule.** Send every daemon call through the harness clients, never raw `fetch` or a hand-built full URL. Add a missing
route to the appropriate client rather than bypassing it.

**Why.** Clients supply tenant headers, authentication and response failure diagnostics consistently across shared hubs.

**Detect.** `tests/eslint.config.mjs` rejects `fetch` in specs; a literal daemon URL or direct request context is a
reviewable signature that lint alone does not cover.

**Do.** Use the fixture's `api`, `fleet`, or `forge` client for its corresponding surface; the `federation` client
drives a sign-in bounce from a browser at a runner host to the hub and back, holding the runner's cookies and the hub's
in separate contexts, since both answer on `127.0.0.1` and cookies ignore the port; in `runnerTest`, the mock-hub
client on `mockHub` and the runner clients from `runnerHostClient`, `runnerStream`, and a `runnerHost`'s own `runners`
and `api`. A `runnerHost` also runs the real `blizzard-runner` on its directory with `cli(args)` (a non-zero exit is a
result, not a throw), edits its stopped directory through `reconfigure`, `clearHubTokens`, `renameRunner` and
`removeStore` (never a file by hand), exports its telemetry to a test-owned sink under the `runnerOtlp` option
(`host.otlp`, which reads spans, sum data points, and log records), answers its shared routes (`health`,
`exportTelemetry`) over its Unix socket as well through `socketApi`, so a spec loops over both transports without
importing `node:http` or `node:net`, and reads a branch head in its world's bare origins with
`originHead(repo, branch)`, so a spec proves a worker's push without running `git`. It reads what the mock fleet wrote
into the world the fixture minted with `mockSessions()` (the mock harness's session records in the workspace) and
`opencodeExports()` (the `mock-opencode` export documents under the host's own transcripts root). A runner's client
names each route a spec reads (`leases`, `leaseUsage`, `leaseTranscript`, `transcriptSegments`, `dashboard`,
`heartbeat`), so a spec reaches no route through `raw`. To act as anyone but the tenant's admin, use `user.api`, a
person's `api` from `people`, or the `as:` option of `cli` and `events.open`.

**Don't.** Assemble `http://localhost:${port}/api/...` in a spec.

## Earn the least isolation (`bzh:service-isolation-earned`)

**Rule.** Declare the loosest isolation level the reads permit. At `common` and `fresh-project`, give created records
unique names, assert only on the test's own ids, and never assert tenant-wide counts, emptiness, or absence.

**Why.** A shared tenant has concurrent neighbors; an assertion over all its rows can pass or fail with another test's
schedule instead of the behavior under test.

**Detect.** The fixture refuses an unset isolation level; factories that furnish the shared tenant refuse below
`fresh-tenant`, and `hubLog.untagged()` refuses below `fresh-hub` (`tests/harness/fixtures.ts`). Review broad list or
count assertions under the shared levels; the harness cannot infer whether they are owned.

**Do.** Select `fresh-tenant` when a whole-tenant assertion is necessary; otherwise filter and assert on minted ids.

**Don't.** Expect an unfiltered shared-tenant list to be empty after deleting your own record.

## Wait on the system (`bzh:service-waits-on-the-system`)

**Rule.** Wait for an event or readable state, never a clock delay. For a negative assertion, wait for a barrier act
that only the expected behavior would emit before asserting its absence.

**Why.** A sleep encodes machine speed; immediate absence proves only that the system has not acted yet.

**Detect.** `tests/eslint.config.mjs` rejects `waitForTimeout`, `setTimeout`, `setInterval`, and `node:timers`; review
absence assertions with no causal barrier.

**Do.** Await the event stream or poll the client for the state the case can name. A wait whose subject is wall-clock
expiry, such as a trailing spend window, polls the runner read that names the expiry, with a deadline covering the
configured window; it never counts host passes or sleeps.

**Don't.** Sleep before asserting that no event was emitted.

Hold a mock worker's turn open at `workerCheckpoint`, not a sleep. Change a sample by `vendorUsage.set` on a credential
the spec minted, followed by `stepHost()`.

A `runnerHost` boots `stepped`: `step()` and `stepHost()` each resolve once the pass has completed, so a test steps,
then reads. It never waits on a timer for a pass the host would run on its own.

To keep a hub outage open under an in-flight read, hold the `mockHubRelay` option's relay (`mockHub.relay`): stop the
hub, issue the read, and wait on the relay's `refusal()` as the barrier that the read is in flight. Restart the hub and
re-seed what the read needs, then release the relay. Releasing earlier lets a retry reach a hub that does not yet know
the caller, and that is refused for good, not retried.

## Stay on public surfaces (`bzh:service-public-surfaces`)

**Rule.** Build test state through public hub surfaces. Only a `fresh-hub` test whose subject is the store may inspect
store files, before the daemon starts or after it stops. Never seed with `tool:mock-data`. A runner spec reads the host
through its HTTP, socket, and stream surfaces; only `service/runner/store/` opens a runner store (`node:sqlite`) or
touches the disk (`node:fs`), before the host starts or after it stops, by the table and column names
`contracts/store/runner.json` declares.

**Why.** A daemon service test must prove the wire and its actual effects; mutating a live store behind the daemon
evades both the public contract and concurrent isolation.

**Detect.** `tests/eslint.config.mjs` rejects `node:child_process`, `node:http`, `node:https`, `node:net`, and
`node:sqlite` in every service spec, and `node:fs` in `service/runner/` and `service/fleet/`; `service/runner/store/` is
the one folder that admits `node:sqlite` and `node:fs`. Review mock-data invocations and the store-access timing; no
static gate proves them or the test's subject.

A runner spec never reads the host's own directory: not the worker stdout files, not the harness-config snapshot, not
the host's store. What a worker did is read from a route of the runner, or from the world the mock fleet wrote into,
through a reader on `runnerHost`. A value no route serves is added to the runner's local API in the change that ports
the test that needs it.

**Do.** Create a repository, issue, or chunk through the fixture's hub client and observe it through the same surface.

**Don't.** Insert rows directly into a shared hub's store to prepare an HTTP assertion.

In `service/runner/store/`, a directory's lock is held by a second real host: the subject's `data/host.lock` is a
symbolic link to that started host's lock file, and the refusal names that host's `runnerHost.pid`. A pre-host daemon is
the harness's `preHostDaemon` counterpart, and a directory no verb builds comes from the `scratchDirs` fixture, which
starts no mock hub. A spec reads a running host's file list, host file, and `.env`, never its store, and reads a store's
currentness through `blizzard-runner host --check`.

A call made as a worker carries the spawn credential the mock harness recorded — the `BLIZZARD_*` lease token, lease id,
and runner URL its runner exported — never a token the test mints, which proves a credential no worker holds.

## Own mock state (`bzh:service-own-mock-state`)

**Rule.** A mock-fleet lever targets only the test's own repository, issue, or runner. Never use a lever without `repo`
or reset forge levers outside a fresh hub. A test's own mock hub, which `runnerTest`'s `mockHub` starts for that test
alone, is exempt: its levers, seeds, captures, and resets are global only to a process no other test reaches.

**Why.** A global lever or reset changes another test's mock world while that test is still running.

**Detect.** Review lever calls without a scoped `repo` and forge reset calls in non-`fresh-hub` specs; the harness
cannot infer ownership from a lever's arguments.

**Do.** Pass the repository the test minted to the scoped forge lever.

**Don't.** Reset the shared forge's levers to make a case independent of earlier state.

## Configure through a profile (`bzh:service-config-is-a-profile`)

**Rule.** A hub-wide setting rides a test profile or a fresh hub, never a test that changes a shared hub in place.

**Why.** A setting changed mid-run alters the behavior of concurrent tests on that hub.

**Detect.** Review writes to hub-wide config within a spec and profile declarations under tests/service/hub/; the
project discovery in `tests/playwright.config.ts` provides the profile boundary, not a lint ban on config calls. The
harness refuses `hubConfig` or `hubEnv` below `fresh-hub`, and a `profile.toml` under `service/runner/` or
`service/fleet/`.

**Do.** Put a hub-wide variant in its own profile, or request a one-off case with
`test.use({ isolation: 'fresh-hub', hubConfig, hubEnv })`. A test that needs people belongs under the `auth` profile; a
test whose subject is the login throttle takes a `fresh-hub` with the throttle left on.

**Don't.** Toggle a shared hub's feature flag before an assertion and toggle it back afterward.

A hub profile lives in `service/hub/` alone. A `service/fleet/` subfolder named after a hub profile, such as
`fleet/auth/`, runs as `service-fleet-auth` on that profile's hub with one worker; every other fleet spec runs as
`service-fleet` on the default profile's hubs, and a fleet test the cross-check raises to `fresh-hub` boots the profile
its project maps to.

A harness a spec runs on is enabled through `test.use({ runnerConfig })`, as `runner[].opencode` with
`${mockBin}/mock-opencode`, never in a `runner.toml`, which binds every spec in its folder. The host always holds a
synthetic OpenCode login at its private data home, as it holds a Claude one. A published harness bundle is given with
the `runnerBundle` option, whose files the fixture writes into a test-owned directory before the host boots and which a
profile names as `${bundle}`, as in `runner[].harness.config_dir`; the case then reads what a worker received of it off
the lease's transcript. A worker's PATH stub is given with `runnerStubs` (executable scripts the profile names as
`${stubs}`, as in `runner[].worker.path_prepend`); a stub or a bundle hook appends to `${logs}/<name>`, which the case
reads back with `runnerHost.workerLog(name)`.

A runner host's configuration rides a profile the same way. `runner.toml` beside the spec, or
`test.use({ runnerConfig })` over it, is a host-file overlay checked against `contracts/config/host.json` before any
process starts. `runnerEnv` adds environment to the host process, and the harness refuses any name `daemon-env.json`
pins and the mock-harness fence. A profile never sets a key the CLI or the fixture owns, such as `hub_url`, `port`, or a
runner's `id`; a layout no CLI verb produces is made by editing the documented files, never by going through a runner
class.

A layout no verb produces after first boot is a `reconfigure` of the stopped host, never a write to its store.

A runner spec produces a subscription sample through the vendor counterpart, never a store write: set what the
credential reports on `vendorUsage`, `stepHost()`, then read the recorded sample off `GET /api/host/subscriptions`. Mint
one credential per subscription so the counterpart can move one without the other, and take a held window's label from
that sampled read, never a literal. A usage-limited worker's named reset places its mark in a window only when it
matches a sampled `resetsAt` to the minute, so sample first and seed the limited chunk after.

## Register what a fleet call needs (`bzh:service-fleet-registration`)

**Rule.** `fleet(name)` mints a runner token and nothing more. A case whose route needs a registered runner, such as a
claim, makes its own `POST /api/fleet/runners` call first and names its epoch explicitly.

**Why.** The token alone authenticates the runner's calls; the hub grants a claim only to a registered one, and a
fixture that registered it would hide the step the case is about.

**Detect.** Review a fleet claim or completion call whose spec never registers the runner; the hub refuses it at run
time.

**Do.** Register the runner with its capabilities, then claim, then complete at the epoch the claim reserved.

**Don't.** Assume `fleet()` registered the runner, or leave the epoch to a default.

Grow this rulebook when a port settles a practice a capable service-test author would not discover independently.
