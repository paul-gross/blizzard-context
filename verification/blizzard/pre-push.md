# The by-hand sweeps before you push (`bzh:matrix-pre-push`)

A local gate cannot reach every surface. This file owns what stands in for the ones it leaves unchecked; which tiers
`blizzard:gate` cannot run is stated in its own row at
[`./commands/packaging.md`](./commands/packaging.md#blizzardgate).

## Reproduce a CI job with its local command (`bzh:ci-job-local-command`)

**Rule.** Reproduce a red CI job, and check a change before you push, at the scale your seat owes: a developer's local
agent reproduces a red job with its local command and runs a change that touches a surface only an upper tier reads
through `blizzard:gate-full`, while a fleet runner reproduces a red job narrowed to its failing step or tests and runs
what the node it is on instructs — linter-class checks plus the targeted tests — never the full `gate` or `gate-full`.

**Why.** `blizzard:gate` runs the shared `gate` suite alone. Upper-tier scenarios read surfaces the gate cannot fully
check, such as board `data-testid` and `data-*` attributes in `tests/ui/` and live API response fields in
`tests/service/`; the kiosk demo mode (`?demo=true`) also reads board handles. Renaming one and pushing on a green
`blizzard:gate` can buy a red pull request or break the demo. The upper tiers run on pull requests except the
same-repository hotfix lane into `master`. The full gate runs serial tiers past a fleet session's shell cap, so CI —
which every fleet delivery opens a pull request into — is where a fleet change's full suite first runs.

**Scope.** The seat is a fact about who is driving, not about the change (`workspace:/context/project/contributing.md`
§Delivery): by hand in a feature environment, or a fleet runner working one node-step of a chunk's graph.

**Do.** By hand: run `mise run gate-full` ([`blizzard:gate-full`](./commands/packaging.md#blizzardgate-full)) and its
separate Playwright service and web exemplar checks, or only the tier the change reaches. For changed store revisions,
also run `mise run store-baseline`; for a release cut, also run `mise run rehearsal`. From a fleet node: the
linter-class rows over what changed — `blizzard:format`, `blizzard:lint`, `blizzard:typecheck`,
`blizzard:process-ref-lint`, `web:lint`, `web:client-drift` — plus `blizzard:unit-test` and `web:unit-test` narrowed to
the modules the change touched; a red `gate / …` job reproduced as `uv run pytest <failing test ids>` or the one red
step's own command. The PR's gate and proof checks and their local commands (run from the blizzard repo root):

| CI job                                                           | Local command                                                                                                                                                          |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gate / …` (except web exemplars)                                | `mise run gate`                                                                                                                                                        |
| `gate / exemplar check (web)`                                    | `mise run exemplar-check`                                                                                                                                              |
| `upper-tiers / service tier (blizzard:service-test)`             | `mise run service-test` and `mise run playwright -- --project='service-*' --project=harness --project=harness-auth --project=harness-runner --project=harness-actions` |
| `upper-tiers / kill-9 crash sweep (blizzard:crash-sweep)`        | `mise run crash-sweep`                                                                                                                                                 |
| `upper-tiers / ui (blizzard:ui)`                                 | `mise run ui`                                                                                                                                                          |
| `upper-tiers / acceptance journey (blizzard:journey)`            | `mise run journey`                                                                                                                                                     |
| `upper-tiers / hub image smoke (blizzard:image-smoke)`           | `mise run image-smoke`                                                                                                                                                 |
| `upper-tiers / reference compose smoke (blizzard:compose-smoke)` | `mise run compose-smoke`                                                                                                                                               |
| `store baseline (blizzard:store-baseline)`                       | `mise run store-baseline`                                                                                                                                              |
| `upgrade rehearsal (release cut)`                                | `mise run rehearsal`                                                                                                                                                   |
| `line provenance` (release-line base only)                       | `./scripts/check-line-provenance.sh <base-sha> <head-sha>`                                                                                                             |

The sweep for a rename, before the tiers: grep the surfaces only they read.

```bash
grep -rn --exclude-dir=node_modules '<old-testid>\|<old-field>' tests/ui/ tests/service/ tests/journey/ tests/crash/ web/projects/hub/src/app/demo/
```

**Don't.** Rename a `data-testid` and push on a green `blizzard:gate` — the UI scenario reading the old handle fails the
pull request's `ui` check. From a fleet node, answer a red `gate / …` job with `mise run gate` — the table's row, which
runs the whole pytest suite.

## A board test handle has one renderer (`bzh:unique-test-handle`)

**Rule.** Give a new `data-testid` a name exactly one component renders, and check that before adding it; a new
component rendering a concept an existing one already renders gets its own prefixed handles.

**Why.** An unscoped locator intended to identify one element becomes ambiguous when two components render its handle;
Playwright can fail with a strict mode violation. Repeated elements within a collection need a scoped locator instead.

**Detect.** The sweep, expecting exactly one component:

```bash
grep -rn 'data-testid="<new-testid>"' web/projects/
```

Also inspect bound and synthesized attributes: the literal sweep cannot find them. `artifacts-tab-artifact-key` is
unreachable by grep from the component side, where it is synthesized as `` `${this.testid()}-key` ``, so it carries a
named spec — `web/projects/fleet/src/lib/chunk/chunk-page/chunk-page-artifacts-tab.spec.ts` — rather than a sweep.

**Do.** For example, a second tile rendering a chunk's cost beside an existing `chunk-cost` handle takes its own
`queue-chunk-cost` handle.

**Don't.** Reuse `chunk-cost` on the new tile because it renders the same concept.

## The browser tiers run the built bundle (`bzh:browser-tiers-run-the-built-bundle`)

**Rule.** Run a browser tier through its task — `mise run ui` — never past it with a bare
`npx playwright test --project='ui*'`.

**Why.** The browser scenarios drive the built bundle `blizzard hub host` serves out of `src/blizzard/static/`, never
the sources, so the task carries `depends = ["web-build"]`. Without a bundle the hub serves a placeholder; with a stale
bundle the scenario exercises the previous UI and can go green against a layout that no longer exists.

**Detect.** A `blizzard:ui` claim resting on a bare `npx playwright test` invocation, or on a run with no `web-build`
ahead of it.

**Do.** *"`blizzard:ui` green via `mise run ui`, the bundle rebuilt in the same run."*

**Don't.** `npx playwright test --project='ui*'` after editing a template, reading a green off the bundle the last build
wrote.

## A red drift check means stage the output (`bzh:drift-stage-not-route-around`)

**Rule.** A red drift check means stage the regenerated output, and never substitute `lint` or `test` for it.

**Why.** `npm run lint` and `npm run test` lint and unit-test different surfaces and neither exercises codegen, so
substituting them for a red drift step reports coverage the gate never ran and leaves the drift unguarded.

**Do.** `web:client-drift` and the OpenAPI half of `blizzard:gate` diff the working tree against the index rather than
against `HEAD`, so `git add` the regenerated `openapi/` and `web/` output before running the gate — an unstaged
regeneration is what fails, not an uncommitted one.

**Don't.** Answer a red `web:client-drift` with `npm run lint && npm run test` passing — the regenerated client is still
unstaged, and the drift ships behind two greens that never looked at it.
