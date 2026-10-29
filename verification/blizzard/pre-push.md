# The by-hand sweeps before you push (`bzh:matrix-pre-push`)

A local gate cannot reach every surface. This file owns what stands in for the ones it leaves unchecked; which tiers
`blizzard:gate` cannot run is stated in its own row at [`./commands.md`](./commands/packaging.md#blizzardgate).

## Reproduce a CI job with its local command (`bzh:ci-job-local-command`)

**Rule.** A red CI job is reproduced with its local command, and a change that touches a surface only an upper tier
reads is run through `blizzard:gate-full` before you push.

**Why.** `blizzard:gate` is the shared `gate` job alone; the upper tiers are the only readers of surfaces nothing else
type-checks — board `data-testid` and `data-*` attributes in `tests/e2e/`, wire field names off a live API response in
`tests/service/`, the kiosk demo mode (`?demo=true`) — and every pull request runs them. Renaming one and pushing on a
green `blizzard:gate` buys a red pull request, found after the push instead of before.

**Do.** Run `mise run gate-full` ([`blizzard:gate-full`](./commands/packaging.md#blizzardgate-full)), or only the tier
the change reaches. For changed store revisions, also run `mise run store-baseline`; for a release cut, also run
`mise run rehearsal`. Every `pr.yml` job and its local command:

| CI job                                                           | Local command                        |
| ---------------------------------------------------------------- | ------------------------------------ |
| `gate / …` (every gate job)                                      | `mise run gate`                      |
| `upper-tiers / service tier (blizzard:service-test)`             | `mise run service-test`              |
| `upper-tiers / kill-9 crash sweep (blizzard:crash-sweep)`        | `mise run crash-sweep`               |
| `upper-tiers / e2e acceptance loop (blizzard:e2e)`               | `mise run e2e`                       |
| `upper-tiers / ui (blizzard:ui)`                                 | `mise run ui`                        |
| `upper-tiers / acceptance journey (blizzard:journey)`            | `mise run journey`                   |
| `upper-tiers / hub image smoke (blizzard:image-smoke)`           | `mise run image-smoke`               |
| `upper-tiers / reference compose smoke (blizzard:compose-smoke)` | `mise run compose-smoke`             |
| `store baseline (blizzard:store-baseline)`                       | `mise run store-baseline`            |
| `upgrade rehearsal (release cut)`                                | `mise run rehearsal`                 |
| `line provenance` (release-line base only)                       | `./scripts/check-line-provenance.sh` |

The sweep for a rename, before the tiers: grep the surfaces only they read.

```bash
grep -rn --exclude-dir=node_modules '<old-testid>\|<old-field>' tests/e2e/ tests/service/ tests/journey/ tests/crash/ web/projects/hub/src/app/demo/
```

**Don't.** Rename a `data-testid` and push on a green `blizzard:gate` — the e2e scenario reading the old handle fails
the pull request's `e2e` check.

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
`web/projects/fleet/src/lib/chunk/chunk-page/chunk-page-artifacts-tab.spec.ts` — rather than a sweep.

## The browser tiers run the built bundle

The browser scenarios drive the built bundle `blizzard hub host` serves out of `src/blizzard/static/`, never the
sources, so `mise run e2e` and `mise run ui` carry `depends = ["web-build"]` and must not be reached past with a bare
`pytest tests/e2e/` or `npx playwright test --project='ui*'`. The hazard is not an unbuilt tree, which fails loudly
before the first assertion, but a bundle present and stale, which fails quietly: the scenario exercises the previous UI
and can go green against a layout that no longer exists.

## A red drift check means stage the output (`bzh:drift-stage-not-route-around`)

**Rule.** A red drift check means stage the regenerated output, and never substitute `lint` or `test` for it.

**Why.** `npm run lint` and `npm run test` type-check and unit-test different surfaces and neither exercises codegen, so
substituting them for a red drift step reports coverage the gate never ran and leaves the drift unguarded.

**Do.** `web:client-drift` and the OpenAPI half of `blizzard:gate` diff the working tree against the index rather than
against `HEAD`, so `git add` the regenerated `openapi/` and `web/` output before running the gate — an unstaged
regeneration is what fails, not an uncommitted one.

**Don't.** Answer a red `web:client-drift` with `npm run lint && npm run test` passing — the regenerated client is still
unstaged, and the drift ships behind two greens that never looked at it.
