# The test tiers, and writing a test at one (`bzh:matrix-tier-rules`)

The tier roster, and the standard every tier's tests are written to. The command each tier runs is its row in
[`../blizzard.md`](../blizzard.md)'s Commands table; what a change owes as a companion landing is
[`./companion-changes.md`](./companion-changes.md)'s; whether a green run counts as evidence at all is
[`./evidence.md`](./evidence.md)'s.

## Test tiers

Five test tiers — each answers a different question, and none substitutes for another; the winter-binding tier runs only
locally. Unit and component tests are pytest; a test that exercises a running hub, runner, or board from outside is a
Playwright Test spec (`bzh:service-tests-in-playwright`). The mocks the upper tiers bind are owned by `blizzard-mock`.

| Tier               | Method                    | Scope                                                                                                                                                                                                                                                    | Tooling                                                                    |
| ------------------ | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **Unit**           | `blizzard:unit-test`      | One class or function in isolation.                                                                                                                                                                                                                      | pytest                                                                     |
| **Component**      | `blizzard:component-test` | A domain slice wired with real internal collaborators, doubles only at the seams.                                                                                                                                                                        | pytest                                                                     |
| **Service**        | `blizzard:service-test`   | A running hub or runner exercised from outside — one daemon against its mock counterpart, or a real runner host on a real hub — or an out-of-process external-tool binding driven against a mock-fleet binary; seams bound to the mock fleet either way. | Playwright Test + HTTP                                                     |
| **UI**             | `blizzard:ui`             | The built board a test's hub serves, in a real Chromium page at a stated viewport, against the real hub on a hub profile, with real runner hosts behind it where the scenario needs them.                                                                | Playwright Test + Chromium; the viewport fixtures in `tests/harness/ui.ts` |
| **Winter binding** | `blizzard:winter-binding` | The winter workspace provider against the real winter CLI, plus one chunk landed over `provider="winter"`. Local-only, never in CI; the platform tiers run on the basic provider instead.                                                                | pytest, gated on `BLIZZARD_WINTER_BINDING=1`                               |

Each pytest tier is a folder: `unit/` and `guards/` give the unit tier, `component/` the component tier
(`bzh:mirrored-test-layout`). Service, UI and winter-binding tests sit where their own rules place them.

## Hermetic by construction

Service and UI tests never spend a real token and never touch the network: the harness seam binds a mock coding harness,
the work-source seam binds the mock GitHub forge, delivery's `land` action reaches the mock forge through the per-entry
`forge_url` a repository record fills rather than through a seam, and the workspace seam binds mocks or local fixtures.

The Python test tiers run against SQLite. The focused `blizzard:postgres-uow-concurrency` command is an exception: it
checks hub unit-of-work lock ordering on Postgres, not a second general test matrix. Other Postgres behavior still rests
on the portable SQL surface (`bzh:sql-portable`) and the named gaps.

In Python tiers, stand test data up through the mock-data CLI and its fixtures (`tool:mock-data`), never through ad-hoc
SQL. Playwright service specs create data through the hub's public surfaces, never by seeding the store. The harness
restoring a template its own CLIs built is not a spec seeding the store.

## The tenant statement guard is on in every tier

Every daemon any tier spawns runs with the tenant statement guard on, whether the suite is Python or Playwright. The
Python suite plugin's (`tests/support/suite_plugin.py`) `pytest_configure` sets `BLIZZARD_TENANT_GUARD=1` and installs
the guard (`src/blizzard/hub/store/tenant_guard.py`) in the test process, and every hub a service or crash test spawns
inherits the variable and installs the guard as it opens its engine (`open_hub_engine`, `src/blizzard/hub/app.py`). The
Playwright harness sets it through `tests/daemon-env.json`; its daemon-log refusal check fails the request's test, or
the run when no request owns the refusal. Only the value `1` switches the guard on. Fixture SQL a test writes raw is
outside the guard's reach, so it names the tenant itself. `bzh:tenant-scoped-store`'s Detect
([../../architecture/system-shape/tenancy.md](../../architecture/system-shape/tenancy.md#adapters-hold-scoped-connections-only-bzhtenant-scoped-store))
owns what the guard refuses and its exemption.

## The runner statement guard is on in every tier

The runner store has a guard of its own, switched on beside the tenant guard in every spawned daemon. Python's same
`pytest_configure` sets `BLIZZARD_RUNNER_GUARD=1` and installs the guard (`src/blizzard/runner/store/runner_guard.py`)
in the test process. Every runner a service or crash test spawns inherits the variable and installs the guard as it
composes its host graph (`build_host_process`, `src/blizzard/runner/composition.py`). Playwright's
`tests/daemon-env.json` also sets it; the harness fails a refusal in a daemon log against the responsible test or the
run.

Only the value `1` switches the guard on. `bzh:runner-scoped-store`'s Detect
([../../architecture/system-shape/runner-scoping.md](../../architecture/system-shape/runner-scoping.md#adapters-hold-the-bound-seam-bzhrunner-scoped-store))
owns what the guard refuses and its exemption. `tests/component/runner/store/test_isolation.py`, at
`blizzard:component-test`, seeds the same shapes for two runner ids in one store. It proves that one runner's adapters
neither read nor change the other's rows, holding its coverage of the read and write census by reflection.

## Head-migrated test stores come from prototypes (`bzh:head-store-prototypes`)

**Rule.** Copy a per-process migrated prototype when a test needs an empty store at head; reserve from-empty migration
chain replay for tests whose subject is the chain. Use `tests/support/scaffolding.py::migrate_to(tmp_path, "head")` or
`tests/support/scaffolding.py::migrated_hub_at(db_url)` for the hub, and
`tests/support/runner_fakes.py::migrated_store_at(db_url)` for the runner.

**Why.** A store test exercises its store behavior, while replaying the chain in every case consumes time without
testing that behavior. Migration tests still need the replay to prove the revisions themselves.

**Detect.** The head-replay guard installed by `tests/support/suite_plugin.py` refuses a direct `upgrade("head")` from
an unmigrated store in a non-migration `test_*.py` module at the root of `tests/` or under its `unit/`, `component/` or
`guards/` folder, naming that module and the helper to use. Upgrades from a pinned older revision and production
initialization pass.

**Do.** `migrated_hub_at(db_url)` before opening a hub store for an adapter test.

**Don't.** Call `migration_runner(config).upgrade("head")` from an ordinary store test on a fresh file.

## A migration test sits beside its revision (`bzh:colocated-migration-tests`)

**Rule.** A test that pins an older store revision to prove that revision lives beside it, as
`src/blizzard/{hub,runner}/store/migrations/tests/<revision-stem>_test.py`, one file per revision: the filename names
the revision the test upgrades into, not the parent it pins, and is the only thing tying test to revision. A revision
that reshapes or backfills rows ships with its colocated test in the same change. A test covering several revisions
takes the newest stem it pins. A test that only puts a store behind head, so that current behavior is its subject, stays
in `tests/` and is never retired. Its helpers live in `tests/support/migrations/`, beside the other shared helpers
(`bzh:mirrored-test-layout`).

- A colocated test skips automatically once its revision is more than 30 days old, by the date in the stem.
  `BLIZZARD_RUN_RETIRED_MIGRATION_TESTS=1` runs them all, for example to vet an Alembic or SQLAlchemy upgrade.
- Only the two shipped stores retire by age. The exemplar's colocated test (`bzh:exemplar-conformance`) sits beside its
  exemplar revision under the same naming rule and always runs.
- A file in any `migrations/tests/` directory beside a `versions/` directory must be named
  `YYYYMMDD_HHMM_<rest>_test.py` with that stem naming a revision in the sibling `versions/`; collection refuses it
  otherwise.
- Each directory is a package, because the stems the hub and runner trees share would collide as test basenames.
  Colocated tests are test code: they are held to the standards of `tests/`, not of production, and never ship in the
  wheel. Helpers a colocated test shares with others live in a `tests/` support module; no colocated file imports
  another.

**Why.** A revision's tests prove it once, while it is new; replaying them for every later run costs time and proves
nothing the chain's head-equivalence checks do not. Beside the revision, the test is found with the file it proves, and
the filename alone says when it expires.

**Detect.** The collection hook in `tests/support/suite_plugin.py`, registered by the repo-root `conftest.py` so it
reaches every colocated directory, refuses a misnamed file or a stem with no sibling revision with a usage error naming
the file (`tests/support/revision_age.py`, proven by `tests/guards/test_revision_age.py`). No check enforces that a
reshaping revision has its test.

**Do.** The exemplar's hub migration test, beside its revision under the same stem
([../../exemplars/index.md](../../exemplars/index.md)).

**Don't.** Name a file for the parent revision it pins, mark a test by hand to retire it, or leave a revision's test in
`tests/`.

**See also.** `./gaps.md`; `../../exemplars/index.md` for the exemplar's migration test.

## A pytest test sits in the folder that mirrors what it tests (`bzh:mirrored-test-layout`)

**Rule.** A unit or component test sits in a folder of `blizzard/tests/` whose name gives its tier, and takes that tier
from the folder, never from a marker.

- `tests/unit/` and `tests/component/` mirror `src/blizzard/`: a test of `src/blizzard/runner/harness/opencode/paths.py`
  is a test module named for it in the matching `runner/harness/opencode/` folder of `tests/unit/`. A folder under a
  tier folder is named for a package, a directory holding an `__init__.py`, under `src/blizzard/`. A test spanning
  packages sits at their deepest common package, so one spanning two top-level packages (hub and runner, or `cli` or
  `wire` with either) sits directly in the tier folder. The packages a test spans are those whose code it proves, not
  every package it imports: a collaborator it seeds through or reads back by, such as a store adapter or another
  domain's service, places nothing. A component test of a route that seeds through a store adapter mirrors the route
  (the `hub/api/` folder of `tests/component/`), not the adapter.
- A test whose subject is the repository rather than `src/blizzard/` — its files (a workflow file, a contract, the
  source tree), a script under `scripts/`, or the suite's own code in `tests/support/` — sits in `tests/guards/` at the
  unit tier and directly in `tests/component/` at the component tier. The sub-folders of `tests/guards/` mirror nothing.
- Every folder under a tier folder is a package.
- A test declares no `unit` or `component` marker under a tier folder.
- No `test_*.py` module sits directly under `tests/`.
- The exemplar tree follows the same rule with `exemplar/` in place of `src/blizzard/`. Its tier folders are packages,
  and `exemplars/python/tests/` itself is not, so pytest imports them as top-level packages.
- Service, crash, UI, rehearsal and winter-binding tests keep the folders their own rules name.
- Shared helpers live in `tests/support/`, and migration helpers in `tests/support/migrations/`, even a helper only one
  folder uses. The `tests/` root holds no module but `conftest.py` and `__init__.py`, and a tier folder none but
  `__init__.py`, `conftest.py` and test modules. A folder-own helper stays in its kind folder.

**Why.** A test is found by the path of the code it proves, and a tier read from a folder cannot drift from a
hand-written marker or be forgotten.

**Detect.** The collection hook in `tests/support/suite_plugin.py` adds the folder's marker before `-m` selects, so
`pytest -m <tier>` sees the folder tier, and refuses a declared tier marker, a folder naming no package, a folder
without an `__init__.py` and every test module directly under a tests root with a usage error naming the file and this
rule. The placement judgements are in `tests/support/tier_layout.py`, proven by `tests/guards/test_tier_layout.py`,
whose root guard fails the unit tier on any other module directly under `tests/`, and whose tier-folder guard fails it
on a non-test module inside a tier folder of either tree.

**Do.** The `hub/domain/` folder of `tests/unit/` for a unit test of a hub domain module, with no marker. The exemplar's
tests show each placement ([../../exemplars/index.md](../../exemplars/index.md)).

**Don't.** Add a flat `tests/test_<thing>.py`, mark a test by hand to give it a tier, or put a component test of a route
in the folder of the adapter it seeds through.

**See also.** `../../exemplars/conformance.md` for the exemplar tree.

## Two tenants on one hub: the isolation scenario

`tests/component/hub/api/test_tenant_isolation.py`, at `blizzard:component-test`, stands two tenants up on one hub,
seeds both with the same shape of records under names that never repeat across them, and proves through the API that
neither reaches the other. A listing in either names none of the other's records; naming the other's record, by path or
in a body, answers as for a record never minted and changes nothing there; a write in one leaves every read of the other
byte for byte as before; each tenant's live stream replays its own events only; a runner-minted id posted in both is two
rows; a route token acts in its chunk's tenant only; the packaged system artifacts read alike from either; the hub-level
export routes refuse a tenant member; and every sweep acts in each open tenant and opens no closed one.
`tests/component/hub/store/test_tenant_isolation_adapters.py` proves the same at the store: every row a tenant wrote
carries its id, and each tenant's adapters read back none of the other's records. `tests/support/pass_isolation.py` is
the shared poisoned-tenant fixture: it runs each hub-wide pass, and each one-tenant pass interleaved with it, with and
without one failing or bursting tenant and fails when any other tenant's calls differ (`bzh:pass-isolates-tenants`).

The scenario's route table names every live tenant route beside the probe that proves its isolation, and
`test_the_table_names_every_live_tenant_route_and_nothing_else` checks the table against the live app both ways, so a
change adding a tenant route fails the tier until it adds the route's row and probe.

## Service tests: one daemon, or the fleet

A service spec lands in the `tests/service/` folder its subject names; [service-tests.md](./service-tests.md) owns each
folder's project, fixtures and profiles.

- `hub/` and `runner/` are one-sided: the daemon under test drives its mock counterpart — a runner spec against the
  test's own mock hub, a hub spec against the mock runner.
- `fleet/` is two-sided: a real runner host enrolled in the test's own tenant on a real hub, its harness and work-source
  seams bound to the mock coding harness and the mock forge. A scenario that needs hub and runner together — an issue
  ingested, its chunk run and landed — is a fleet spec.

A diagnostic driving a real external tool runs against the mock fleet's own CLI-surface artifact instead. Either way, a
test's edge cases come from driving a mock's levers, never from contriving the real daemon or the real external tool
into a rare state.

## New black-box tests use Playwright (`bzh:service-tests-in-playwright`)

**Rule.** Write a new test that exercises a running hub, runner, or board from outside as a Playwright Test spec: daemon
and fleet behavior under `tests/service/`, a browser scenario under `tests/ui/`. A full-stack scenario is a
`tests/service/fleet/` spec, and one the browser drives is a `tests/ui/` spec. Unit and component tests stay pytest.

**Why.** The shared hub, tenant-aware clients, event stream, runner-host and isolation fixtures give black-box behavior
one coherent harness; every new pytest service case grows the older parallel harness the Playwright package replaces.

**Detect.** A new pytest case under `tests/service/` driving a daemon's HTTP API is a reviewable signature; the registry
check verifies cited tier membership, not placement of every new test.

**Do.** Read [service-tests.md](./service-tests.md) before authoring a spec. A scenario that ingests an issue, runs its
chunk and lands it is a `tests/service/fleet/` spec, patterned on `tests/service/fleet/acceptance-loop.spec.ts`.

**Don't.** Add a pytest daemon case because nearby existing cases still use pytest.

## A port moves its citations (`bzh:port-moves-citations`)

**Rule.** In the same change that ports a pytest service case, delete its Python original, repoint its citations in
blizzard and blizzard-context to the replacement spec, retain the function name as the test title.

**Why.** A duplicate test and a stale registry citation leave two purported owners of the same behavior.

**Detect.** `blizzard-context:registry-drift` check A fails citations of deleted files and missing `file::title` names;
review the deleted file's references for omissions the checker cannot see.

**Do.** Search both repos for the old filename and function name, then replace citations with `file::title` where
precise.

**Don't.** Leave the old pytest case behind after the spec takes over.

## A whole-CLI harness fake is a service-tier binding (`bzh:external-cli-fake-is-service-tier`)

**Rule.** A test case that drives a fake external-tool CLI as an out-of-process binary — spawned and exercised the way a
real harness integration would spawn the genuine tool, not called as a hermetic in-process double — belongs at
`blizzard:service-test`. It runs behind the same fleet-binding skip every other service-tier case already uses: it needs
the sibling provisioned `blizzard-mock` worktree and skips cleanly when that worktree is not provisioned, never a fail.

**Why.** A whole-CLI fake only earns its weight by being spawned as a real process — argv, exit codes, stdio framing,
and process lifetime all real. That is the mock fleet's own claim, the same one the rest of the service tier rests on,
so a case that needs it inherits the mock fleet's gate rather than running unconditionally wherever it happens to be
collected.

**Detect.** A test resolving a binary path from the sibling `blizzard-mock` worktree to spawn it *as the external tool
under test* — asserting the exit code, argv-shape, or process behavior of the fake CLI itself. A case driving only a
generic subprocess, pty, or sandbox boundary that never presents an external-tool-shaped CLI is not this — it stays at
`blizzard:component-test` with an inline script, since moving it would weaken the gate for no gain. Nor is a case that
stands up a real hub and runner host for a scenario to drive — that is a `tests/service/fleet/` or `tests/ui/` spec, not
a whole-CLI-fake case.

**Do.** Guard the case behind the established fleet-binding skip and resolve the binary through the established
sibling-worktree helper, never a new resolution mechanism.

**Don't.** Leave a whole-CLI-fake case at `blizzard:component-test` reasoning that it "doesn't touch the network" — the
tier a case belongs to turns on whether it spawns the mock fleet's own binary, not on whether the case runs offline.

## Crash correctness is a dimension, not a tier

Crash correctness cuts across the tiers rather than adding one. The unit tier covers each step function's idempotency in
isolation, the component tier drives steps in-process against the virtual clock, and only the kill-9 sweep
`blizzard:crash-sweep` needs real subprocesses and real signals. The architectural requirements that sweep exercises are
owned by [`../../architecture/crash-correctness.md`](../../architecture/crash-correctness.md).

## A spawned daemon's output goes to a file (`bzh:daemon-stdout-to-file`)

**Rule.** A spawned daemon's output goes to an append-mode file, never to a pipe nothing drains.

**Why.** `stdout=subprocess.PIPE` on a process nobody reads is a deadlock on a timer: the daemon runs until its output
fills the ~64 KiB pipe buffer, then blocks in `write` forever. A pipe-wedged daemon never dies — `poll()` still reports
it alive and its port still answers `connect`, but it stops serving mid-tick and every wait against it times out.

**Detect.** `tests/guards/test_daemon_spawn_sink.py` fails the unit tier on any newly introduced
`stdout=subprocess.PIPE`. Log volume is what arms the wedge, so a change that adds daemon logging can wedge a suite that
was passing and the symptom lands far from the cause — suspect the wedge before the test.

**Do.** The tiers that spawn real daemons with `subprocess.Popen` — `blizzard:crash-sweep`, `blizzard:service-test`, and
`blizzard:rehearsal` — spawn through `tests/support/scaffolding.py`'s `daemon_log_sink`, which is that file: a daemon
with a runtime dir logs to `daemon.log` beside its store, and the mock fleet's dirless daemons log to
`shared_daemon_log_dir()`.

**Don't.** `subprocess.Popen([...], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)` for a daemon the test then waits
on — the guard fails the unit tier, and past it the daemon wedges once its log fills the pipe.

## A spawned daemon binds port 0 and says where (`bzh:daemon-binds-port-zero`)

**Rule.** A daemon a test spawns binds `--port 0` and publishes where it landed with `--listening-file`; the test reads
the daemon's URL from that file, never picks the port itself.

**Why.** A port picked test-side — bound to `0`, read, released, then handed to the daemon — is free only until someone
else binds it. Under xdist someone else does: another worker's daemon or the kernel's next ephemeral bind takes the port
in the gap, and the daemon fails to bind, or a client reaches the wrong daemon. Only the process that binds can know the
port is its own.

**Detect.** `tests/guards/test_daemon_port_zero.py` fails the unit tier on a test-side port chooser in `tests/**/*.py`
or `tests/harness/**/*.ts` — a function named for one, or a bind on `0` that returns the port after closing its socket.

**Do.** Start every hub, runner host, and mock daemon on `--port 0 --listening-file <path>`, deleting `<path>` first —
the daemon never removes it on stop — and read the URL from it once it appears; a startup failure publishes no file, so
fail on the process exiting with its log tail. Thread the URL, not a port, through every helper. A restart pins the port
the former start published, as `--port` beside `--listening-file`, so peers already holding the URL reach it again; a
runner host's host file keeps `port = 0`. An in-process server binds a socket on `0`, holds it, and hands it to uvicorn
as `sockets=`. An address nothing may answer comes from the `refused_url` fixture, a socket bound without listening — a
connect is refused and no daemon can take the port.

**Don't.** `free_port()` or a bind-probe-close helper handing a port to a daemon. Two exceptions stand, each the only
way to start what it starts: otelcol's receiver and health ports in `tests/harness/collector.ts`, since otelcol takes
its ports from config and publishes none; and `tests/rehearsal/installation.py`'s `baseline_daemon_port`, for a daemon's
first start under a baseline release older than `--listening-file` — that exception lasts until every supported release
ships the flag.

## A test module imports no other test module (`bzh:test-imports-support-only`)

**Rule.** A `test_*.py` module imports nothing from another `test_*.py` module. Code two test modules share lives in a
support module — a helper under `tests/support/`, or a test folder's own helper — and both import it from there; the
layout rule above owns where helpers live.

**Why.** Importing from a test module makes the importer depend on a file whose job is to hold tests, and ties both
files to where they sit: a module cannot move, split, or be renamed without chasing every importer. An imported test
function is also collected a second time, under the importer's node id, and runs twice.

**Detect.** `tests/guards/test_layering.py` fails the unit tier on any import of a module whose last component starts
with `test_`, from any `test_*.py` under `tests/` at any depth. It reads the AST, so `from tests.test_x import …`,
`import tests.test_x`, `from tests import test_x`, relative imports, and function-local imports all count.

**Do.** Move the shared name — with the private module-level names it needs — into a support module named for what it
holds, and import it from there in the definer and every importer. A name that keeps its leading underscore carries
`# pyright: ignore[reportPrivateUsage]` at each import, and its definition carries
`# pyright: ignore[reportUnusedFunction]` when nothing in the support module calls it.

**Don't.** `from tests.component.hub.delivery.actions.test_land import _forge` — the guard fails the unit tier.
Re-import a test function to run it from another test; extract what it asserts into a support helper both tests call.

## A visual change is proved by a real render (`bzh:visual-change-needs-a-render`)

**Rule.** Verify a change whose observable effect is visual — layout, styling, what a component renders — by at least
one artifact from a real render **that covers the changed surface**: a `web:shell-sweep` spec that mounts the changed
component (add one to the roster when none does), a `blizzard:ui` assertion against that surface in the served bundle
(the `wideViewport`/`narrowViewport` fixtures in `tests/harness/ui.ts` give it a real page), a screenshot of it from a
live environment (`blizzard-mock:manual-seeded-board` stands a realistic board up to render), or a screenshot of the
changed part's stories taken by `web:manual-workshop`, a real Chromium render of the part. A workshop render covers a
change to the part itself; a change to how a page lays a part out still needs a render of that page, since the workshop
shows the part without its page. A jsdom-tier green is inadmissible as visual evidence — and so is a render green whose
specs never mount the changed component.

**Why.** jsdom parses `@container` and media-query rules without ever evaluating layout, so
`bzh:mutation-review-selection`'s litmus applies to the whole unit tier at once: a suite that stays green when the
layout breaks is not evidence.

**Detect.** A diff touching `*.html` templates or `*.css` component styles whose verification claim cites only
`web:unit-test`. For a `.ts`-only diff the reviewer's question is: does the change alter what the template emits, or how
it lays out? If yes, the same claim standard applies.

**Do.** An admissible claim names the artifact *and* the changed surface it rendered:
*"`<component>.shell-sweep.spec.ts` asserts the changed grid stacks at 390px"*, *"screenshot: seeded board, the changed
cost column, 1280px"*, or *"workshop screenshot: the changed badge's error story, `phone`"*.

**Don't.** Ship a template or CSS change on a full-suite unit green alone — every one of those specs rendered into a DOM
that never evaluated the rules the change touched.

**See also.** `bzh:narrow-viewport-tier-rule` below — the mobile-shell case of this rule, adding that narrow widths are
part of the claim.

## Narrow width is proved by a test (`bzh:narrow-viewport-tier-rule`)

**Rule.** A change to a component reachable from the mobile shell's bottom nav is exercised at a narrow width by at
least one test.

**Why.** The jsdom blindness is `bzh:visual-change-needs-a-render`'s ground, above; what this rule adds is that a
browser scenario at Playwright's default 1280x720 viewport cannot see a narrow collapse either — the width is part of
the claim.

**Detect.** A change to a component the mobile shell's bottom nav reaches, whose verification claim names no width at or
below ~390px. The parent rule's `*.html`/`*.css` signature does not answer the reachability half — walk the bottom nav's
routes to settle it, since a `.ts`-only change to a reached component is in scope too.

**Do.** The `wideViewport` and `narrowViewport` fixtures in `tests/harness/ui.ts` give any `blizzard:ui` spec a real
~390px page to assert against, and `web:shell-sweep` proves the real-Chromium layout claims jsdom cannot — the surfaces
it covers and what each of its specs asserts are stated in
[`./commands.md`](./commands/web/shell-sweep.md#webshell-sweep).

**Don't.** Treat a component with no narrow-width handling of its own as a defect to fix in place. It is a gap to close
with a narrow-width proof in whichever narrow-width method fits the surface.

**See also.** `bzh:visual-change-needs-a-render` above — the general rule this one narrows.
