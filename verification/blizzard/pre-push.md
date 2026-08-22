# Pre-push sweeps — the tiers `blizzard:gate` cannot run (`bzh:matrix-pre-push`)

What a local gate leaves unchecked, and what to sweep by hand before pushing.

- **Sweep the release-only tiers before you push (`bzh:sweep-release-only-tiers`).** The
  [`blizzard:gate`](./commands.md#blizzardgate) row names *which* tiers that command cannot run; this is what that blind
  spot actually bites. Those tiers are the only ones reading two surfaces nothing else type-checks: **board
  `data-testid`s and `data-*` attributes** (`tests/e2e/`) and **wire field names off a live API response**
  (`tests/service/`). A rename of either therefore ships green and breaks them where you will not see it. Grep before
  pushing, then run what the change touched:

  ```bash
  grep -rn '<old-testid>\|<old-field>' tests/e2e/ tests/service/ tests/journey/ tests/crash/ web/projects/hub/src/app/demo/
  ```

  The `demo/` directory is in that list because the tiers are no longer the only readers: the board's kiosk demo mode
  (`?demo=true`) steers on four board handles from **production** code — `chunk-detail`/`detail-id` and
  `artifacts-tab-artifact`/`artifacts-tab-artifact-key`. It fails *quietly* where a scenario fails loudly (the wait
  times out, the scroll is skipped, the screen holds still), so each half is pinned on the producing side: the first
  pair by `tests/e2e/test_board_browser_e2e.py`, the second by
  `web/projects/hub/src/app/board/chunk/chunk-artifacts-tab.spec.ts`. Note the second pair is unreachable by grep from
  the component side at all — `artifacts-tab-artifact-key` is never a literal there, only synthesized as
  `` `${testid()}-key` `` — which is why it has a named spec rather than a sweep.

  That grep catches a handle you **removed**. A handle you **added** breaks these tiers just as hard and the grep is
  blind to it: a `data-testid` is only a usable locator while exactly one component renders it, so a second component
  claiming an existing name makes every `get_by_test_id` for it ambiguous and the scenario dies on
  `strict mode violation: … resolved to 2 elements`. A new component that renders a concept an existing one already
  renders (the same chunk's open question, in a rail *and* in the detail dock) is the case to watch — give it its own
  prefixed handles. Check a new handle is unique before you add it:

  ```bash
  grep -rn 'data-testid="<new-testid>"' web/projects/   # expect exactly one component
  ```

  The browser scenarios drive the **built** bundle `blizzard hub host` serves out of `src/blizzard/static/`, never the
  sources. `mise run e2e` therefore `depends = ["web-build"]` — do not reach past it with a bare `pytest tests/e2e/`.
  The hazard is not the unbuilt tree (that fails loudly, before the first assertion); it is a bundle that is **present
  but stale**, which fails *quietly* — the scenario exercises the previous UI and can go **green against a layout that
  no longer exists**, reporting coverage of a change it never loaded. This is a rule rather than a note because the same
  blind spot has landed three times, most recently against a board-layout rewrite whose geometry assertion would have
  passed against the old layout had a second, unrelated failure not tripped first.

- **A red drift check means stage the regenerated output, not the check is noisy — never substitute `lint`/`test` for it
  (`bzh:drift-stage-not-route-around`).** `web:client-drift` and the OpenAPI half of `blizzard:gate` diff the working
  tree against the index, not against `HEAD`, so `git add` the regenerated `openapi/` and `web/` output before running
  the gate — an *unstaged* regeneration is what fails, not an uncommitted one. `npm run lint` and `npm run test`
  type-check and unit-test different surfaces; neither exercises codegen, so substituting them for a red drift step
  reports coverage the gate never ran and leaves the drift unguarded. This is a rule rather than a note because the same
  blind spot has landed at least three times in one build, once as exactly that substitution. Scope: the rule binds the
  evidence a verification claim rests on, not the inner loop — a tight dev-test iteration may run narrower checks
  (`ng test <project> --include='**/<touched>.spec.ts'`, a single pytest module) or defer a gate entirely, so long as
  the full declared method runs green before the work is called verified; a narrowed run is a dev-loop convenience,
  never claim evidence.
