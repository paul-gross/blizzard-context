# Own the state a case touches

What a service spec may assume about the state around it: the isolation level it declares, the mock levers it pulls, and
what the fleet fixture does and does not set up. Each rule follows the slot skeleton `winter-canon:/rule-shape.md` owns
(`canon:rule-shape`), rule-per-section.

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

## Own mock state (`bzh:service-own-mock-state`)

**Rule.** A mock-fleet lever targets only the test's own repository, issue, or runner. Never use a lever without `repo`
or reset forge levers outside a fresh hub. A test's own mock hub, which `runnerTest`'s `mockHub` starts for that test
alone, is exempt: its levers, seeds, captures, and resets are global only to a process no other test reaches.

**Why.** A global lever or reset changes another test's mock world while that test is still running.

**Detect.** Review lever calls without a scoped `repo` and forge reset calls in non-`fresh-hub` specs; the harness
cannot infer ownership from a lever's arguments.

**Do.** Pass the repository the test minted to the scoped forge lever.

**Don't.** Reset the shared forge's levers to make a case independent of earlier state.

## Register what a fleet call needs (`bzh:service-fleet-registration`)

**Rule.** `fleet(name)` mints a runner token and nothing more. A case whose route needs a registered runner, such as a
claim, makes its own `POST /api/fleet/runners` call first and names its epoch explicitly.

**Why.** The token alone authenticates the runner's calls; the hub grants a claim only to a registered one, and a
fixture that registered it would hide the step the case is about.

**Detect.** Review a fleet claim or completion call whose spec never registers the runner; the hub refuses it at run
time.

**Do.** Register the runner with its capabilities, then claim, then complete at the epoch the claim reserved.

**Don't.** Assume `fleet()` registered the runner, or leave the epoch to a default.
