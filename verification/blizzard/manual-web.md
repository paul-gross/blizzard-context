# Performing a `web:` manual method (`bzh:matrix-manual-web-detail`)

<!-- One flat `###` section per method id — the shape this file's sibling spokes share. -->
<!-- rumdl-disable MD001 -->

Full detail for the `web:` manual methods named in [`../blizzard.md`](../blizzard.md)'s Manual testing table, one
section per row, in that table's order. The `blizzard:` methods live in [`./manual.md`](./manual.md) and the
`blizzard-mock:` methods in [`./manual-mock.md`](./manual-mock.md).

Both methods are driven by a human, or a `frontend-verifier` agent, in a real browser — the pass condition is a rendered
view and a gesture's effect — and both start, from the workspace root, with a provisioned env, its daemons up, and its
shell vars sourced:

```bash
winter provision <env>
winter service up <env> --wait
source <(winter env <env>)
```

`tool:service-up` serves each app twice — [`./tools.md`](./tools.md#toolservice-up) owns the two copies and their ports.
Verify a change to the app's source at the `ng serve` dev-server port each Setup below names, and reach for the daemon's
own port only when what changed is how the bundle is built or served. Drive only the env's own daemons — never the
hosted hub, whose standing rule `workspace:/context/project/hub-data-modes.md` owns.

### `web:manual-board`

**Surface.** The hub board — the Angular `hub` app — driven in a real browser against a running hub: what a view renders
from the hub's state, and what a gesture on it does to that state. Auth-gated rendering is
[`blizzard:manual-standing-idp`](./manual.md#blizzardmanual-standing-idp)'s, because the hub this method stands up
serves everything unauthenticated, and whether a seed itself renders faithfully is
[`blizzard-mock:manual-seeded-board`](./manual-mock.md#blizzard-mockmanual-seeded-board)'s.

**Setup.** The shared preamble above; the board is at `http://localhost:${BZ_HUB_WEB_PORT}/`. An empty store renders an
empty board, so seed the state the changed view needs with `tool:mock-data` —
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) owns the commands and the choice against the real
ingest path.

**Steps.**

1. State the changed behavior as an observable before opening the browser: this view, over this state, renders this — or
   this gesture yields this rendered result and this change in the hub's state.
2. Seed or drive the hub into that state.
3. Open the view that carries the change and confirm it renders the stated result, with no error in the browser console
   and no failed `/api` request in the network log.
4. Perform each changed gesture, confirm the rendered result, then read the effect back from the hub itself —
   `GET /api/chunks/<chunk-id>` or `uv run blizzard hub status` from `<env>/blizzard` — so a control that only repaints
   the page does not pass.
5. For a visual change, take the screenshot [`./tier-rules.md`](./tier-rules.md) (`bzh:visual-change-needs-a-render`)
   admits as evidence, at each width the claim names.
6. Keep the observations — the view's URL, the seed command, screenshots, the read-back output — with the change under
   verification.

**Passes when.** Every stated observable renders in the browser from the worktree's current source, every driven
gesture's effect is confirmed in the hub's own state, and the console and network log stay clean throughout.

### `web:manual-panel`

**Surface.** The runner panel — the Angular `runner` app — driven in a real browser against a running runner: what its
BOARD and EVENTS tabs render from the runner's machine-local state, and what a gesture on it does to that state. Whether
a fleet seed itself renders coherently beside the board is
[`blizzard-mock:manual-seeded-fleet`](./manual-mock.md#blizzard-mockmanual-seeded-fleet)'s.

**Setup.** The shared preamble above; the panel is at `http://localhost:${BZ_RUNNER_WEB_PORT}/`. Seed the runner store
with `tool:mock-data`'s `scenario fleet`, after the daemons are up —
[`../../tooling/store-seeding.md`](../../tooling/store-seeding.md) §Seeding both stores together owns the command and
why the order matters.

**Steps.**

1. State the changed behavior as an observable before opening the browser: this panel, over this runner state, renders
   this — or this gesture yields this rendered result and this change in the runner's state.
2. Seed or drive the runner into that state — a seed for a dormant one, a chunk walked through the env's hub
   ([`blizzard:manual-hub`](./manual.md#blizzardmanual-hub)'s loop walk) for what only a live lease renders.
3. Open the view that carries the change and confirm it renders the stated result, with no error in the browser console
   and no failed `/api` request in the network log.
4. Wait one tick — 30 seconds by default, `tick end` in the runner's log — and confirm the view still renders the stated
   result: the daemon reconciles its store every tick, and a panel correct only until then does not pass.
5. Perform each changed gesture, confirm the rendered result, then read the effect back from the runner itself with
   `curl -fs "http://127.0.0.1:$BZ_RUNNER_PORT/api/dashboard"`. Do not clear a seeded runner's local pause as a gesture
   unless the pause control is what changed — [`../../tooling/store-seeding.md`](../../tooling/store-seeding.md)
   §Seeding an env whose daemons are up owns what that one click sets off.
6. For a visual change, take the screenshot [`./tier-rules.md`](./tier-rules.md) (`bzh:visual-change-needs-a-render`)
   admits as evidence, at each width the claim names.
7. Keep the observations — the view's URL, the seed command, screenshots, the read-back output — with the change under
   verification.

**Passes when.** Every stated observable renders in the browser from the worktree's current source and still renders
after the next tick, every driven gesture's effect is confirmed in the runner's own state, and the console and network
log stay clean throughout.
