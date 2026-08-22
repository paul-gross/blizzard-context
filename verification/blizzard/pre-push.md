# The by-hand sweeps before you push (`bzh:matrix-pre-push`)

A local gate cannot reach every surface. This file owns the sweeps that stand in for the ones it leaves unchecked; which
tiers `blizzard:gate` cannot run is stated in its own row at [`./commands.md`](./commands.md#blizzardgate).

## Sweep the release-only tiers before you push (`bzh:sweep-release-only-tiers`)

**Rule.** Before you push, sweep the release-only tiers for every handle or field the change renamed or removed, then
run whatever the change touched.

**Why.** Those tiers are the only readers of surfaces nothing else type-checks — board `data-testid` and `data-*`
attributes in `tests/e2e/`, and wire field names off a live API response in `tests/service/` — so renaming either ships
green and breaks them where you will not see it.

**Do.**

```bash
grep -rn '<old-testid>\|<old-field>' tests/e2e/ tests/service/ tests/journey/ tests/crash/ web/projects/hub/src/app/demo/
```

`demo/` is in that sweep because the tiers are not the only readers of those handles: the board's kiosk demo mode
(`?demo=true`) steers on `chunk-detail`/`detail-id` and `artifacts-tab-artifact`/`artifacts-tab-artifact-key` from
production code, and it fails quietly where a scenario fails loudly.

## Board test handles

Check a new handle is unique before adding it, expecting exactly one component:

```bash
grep -rn 'data-testid="<new-testid>"' web/projects/
```

A `data-testid` is a usable locator only while exactly one component renders it, so a duplicate name makes every
`get_by_test_id` for it ambiguous and the scenario dies on `strict mode violation: … resolved to 2 elements`; a new
component rendering a concept an existing one already renders gets its own prefixed handles.

`artifacts-tab-artifact-key` is unreachable by grep from the component side, where it is never a literal but only
synthesized as `` `${testid()}-key` ``, so it carries a named spec —
`web/projects/hub/src/app/board/chunk/chunk-artifacts-tab.spec.ts` — rather than a sweep.

## The browser tiers run the built bundle

The browser scenarios drive the built bundle `blizzard hub host` serves out of `src/blizzard/static/`, never the
sources, so `mise run e2e` carries `depends = ["web-build"]` and must not be reached past with a bare
`pytest tests/e2e/`. The hazard is not an unbuilt tree, which fails loudly before the first assertion, but a bundle
present and stale, which fails quietly: the scenario exercises the previous UI and can go green against a layout that no
longer exists.

## A red drift check means stage the output (`bzh:drift-stage-not-route-around`)

**Rule.** A red drift check means stage the regenerated output, and never substitute `lint` or `test` for it.

**Why.** `npm run lint` and `npm run test` type-check and unit-test different surfaces and neither exercises codegen, so
substituting them for a red drift step reports coverage the gate never ran and leaves the drift unguarded.

**Do.** `web:client-drift` and the OpenAPI half of `blizzard:gate` diff the working tree against the index rather than
against `HEAD`, so `git add` the regenerated `openapi/` and `web/` output before running the gate — an unstaged
regeneration is what fails, not an uncommitted one.
