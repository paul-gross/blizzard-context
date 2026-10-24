# Authoring Playwright service tests

These rules bind specs under `blizzard/tests/service/`. Start at the service method's
[command detail](./commands/test-tiers/service.md) for the paired task commands and at [tier-rules.md](./tier-rules.md)
for allocation and statement guards. The harness owns fixtures in `tests/harness/fixtures.ts`, clients in
`tests/harness/client/`, and profile discovery in `tests/playwright.config.ts` and `tests/harness/profiles.ts`.

## Take fixtures, don't build them (`bzh:service-fixtures-only`)

**Rule.** Name the fixtures a test needs — tenant, project, clients, people, and event stream — and import only
`tests/harness/fixtures.ts`. Do not use Playwright's built-in `request` or set shared state in `test.beforeAll`.

**Why.** The harness fixtures own daemon lifetime, tenant routing, cleanup, and test isolation. A bare request context
reaches no tenant; file-wide mutable setup crosses parallel tests.

**Detect.** `tests/eslint.config.mjs` rejects destructured `request`, harness imports other than fixtures, and
`test.beforeAll`/`test.afterAll` in service specs. Review ad-hoc construction of a fixture's resource.

**Do.** Import `test` and `expect` from the harness fixtures and declare only the resources the case reads.

**Don't.** Import a harness daemon helper or destructure `{ request }` from a Playwright test callback.

## Call through clients (`bzh:service-clients-only`)

**Rule.** Send every daemon call through the harness clients, never raw `fetch` or a hand-built full URL. Add a missing
route to the appropriate client rather than bypassing it.

**Why.** Clients supply tenant headers, authentication and response failure diagnostics consistently across shared hubs.

**Detect.** `tests/eslint.config.mjs` rejects `fetch` in specs; a literal daemon URL or direct request context is a
reviewable signature that lint alone does not cover.

**Do.** Use the fixture's `api`, `fleet`, or `forge` client for its corresponding surface.

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

**Detect.** `tests/eslint.config.mjs` rejects `waitForTimeout`; review `setTimeout` sleeps and absence assertions with
no causal barrier.

**Do.** Await the event stream or poll the client for the state the case can name.

**Don't.** Sleep before asserting that no event was emitted.

## Stay on public surfaces (`bzh:service-public-surfaces`)

**Rule.** Build test state through public hub surfaces. Only a `fresh-hub` test whose subject is the store may inspect
store files, before the daemon starts or after it stops. Never seed with `tool:mock-data`.

**Why.** A daemon service test must prove the wire and its actual effects; mutating a live store behind the daemon
evades both the public contract and concurrent isolation.

**Detect.** Review imports of store adapters, direct SQLite access, and mock-data invocations in service specs; no
static gate proves the store-access timing or the test's subject.

**Do.** Create a repository, issue, or chunk through the fixture's hub client and observe it through the same surface.

**Don't.** Insert rows directly into a shared hub's store to prepare an HTTP assertion.

## Own mock state (`bzh:service-own-mock-state`)

**Rule.** A mock-fleet lever targets only the test's own repository, issue, or runner. Never use a lever without `repo`
or reset forge levers outside a fresh hub.

**Why.** A global lever or reset changes another test's mock world while that test is still running.

**Detect.** Review lever calls without a scoped `repo` and forge reset calls in non-`fresh-hub` specs; the harness
cannot infer ownership from a lever's arguments.

**Do.** Pass the repository the test minted to the scoped forge lever.

**Don't.** Reset the shared forge's levers to make a case independent of earlier state.

## Configure through a profile (`bzh:service-config-is-a-profile`)

**Rule.** A hub-wide setting rides a test profile or a fresh hub, never a test that changes a shared hub in place.

**Why.** A setting changed mid-run alters the behavior of concurrent tests on that hub.

**Detect.** Review writes to hub-wide config within a spec and profile declarations under tests/service/hub/; the
project discovery in `tests/playwright.config.ts` provides the profile boundary, not a lint ban on config calls.

**Do.** Put a hub-wide variant in its own profile, or request `fresh-hub` for a one-off case.

**Don't.** Toggle a shared hub's feature flag before an assertion and toggle it back afterward.

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
