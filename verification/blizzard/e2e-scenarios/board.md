<!--
  Machine-parsed by check C of blizzard-context:/scripts/check-registry-drift.py: one level-2 "##" section per
  tests/e2e/ module, with that module's test functions as "- `test_…`" bullets beneath it.
-->

# Operator-board-in-a-browser e2e scenarios (`bzh:e2e-board`)

The scenarios driving a real Chromium over the web app the hub serves — the operator board's views and its live SSE
updates.

The browser scenarios are skipped in the `gate`/`pr` single-repo checkout; the tag `release` workflow runs the full e2e
tier headless over the multi-repo checkout (Chromium via `uv run playwright install --with-deps chromium`; locally,
`uv run playwright install chromium`).

Every browser scenario here needs the built bundle `blizzard hub host` serves and installed Chromium, skipping cleanly
without either or without `BLIZZARD_E2E=1`. Every scenario also needs the sibling provisioned `blizzard-mock` worktree.

The other board browser scenarios run under `blizzard:ui` in `tests/ui/`; see the
[UI method](../commands/test-tiers/ui.md) for their roster.

## test_flow_places_browser_e2e

The board's place lines and a flow's record over a real hub landing two chunks on one branch, held in its line by the
mock forge's `checks_pending` lever. The board is loaded once and never reloaded.

- `test_the_board_shows_each_place_on_a_branch_and_clears_it_live_once_it_lands` — proves each delivering card's place
  line names the branch as `GET /api/flows?active=true` does, with the two chunks landing or in line in arrival order.
  Once the lever clears, both land and the cards drop their place lines live over the `flow-changed` frame; the flow's
  record then opens in the dock through a landed chunk's timeline, listing both landings.
