# The standing e2e scenario registry — `blizzard:e2e` (`bzh:e2e-scenario-registry`)

The single authoritative list of the `blizzard:e2e` scenarios — [../blizzard.md](../blizzard.md) `## Commands` names the
command; this is the full scenario-by-scenario detail.

`mise run e2e` (`BLIZZARD_E2E=1 uv run pytest tests/e2e/`) — the **standing e2e smoke suite**, full-stack scenarios over
the canonical `build → review → deliver` delivery shape, its human-loop variants, the operator board and its mobile
glance shell, the graph explorer, the authored post-merge edge, the cross-graph migration, node session-mode continuity,
the browser login/session lifecycle, the multi-daemon runner SSO federation, the operational event log, resume-time
spawn-preamble elision, the forge-status label projection, checks-gate enforcement, the YAML-authored delivery policies
and their conflict path, the chunk board's Transcripts tab, the runner panel's own live SSE stream, and the non-code
spike, each self-managing the forge + hub + runner over a minted `blizzard-mock` fixture (every seam real, no
tokens/network).

Full detail lives under [./e2e-scenarios/](./e2e-scenarios/), one file per reader question. Each scenario module is a
`##` section in exactly one of them, and the routing table below is the only place naming which.

## Routing

| File                                                       | Read when…                                                                                                                                                  |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`delivery-loop.md`](./e2e-scenarios/delivery-loop.md)     | …you want the canonical `build → review → deliver` shape, a chunk shape that rides it, or an edge that carries a chunk past its own graph or past the land. |
| [`human-loop.md`](./e2e-scenarios/human-loop.md)           | …you want a scenario where the chunk stops for a person — retries exhausted, a question asked, a decision gated.                                            |
| [`delivery-policy.md`](./e2e-scenarios/delivery-policy.md) | …you want what `deliver` does against a red check, a conflict, or a pending CI run, or the forge label projection.                                          |
| [`sessions.md`](./e2e-scenarios/sessions.md)               | …you want which session a node resumes, or what a resumed spawn re-sends.                                                                                   |
| [`auth.md`](./e2e-scenarios/auth.md)                       | …you want the browser-driven human-auth surfaces — the hub login dance, the multi-daemon runner SSO bounce.                                                 |
| [`board.md`](./e2e-scenarios/board.md)                     | …you want a browser-driven proof over the web app the hub serves — a board view, a live SSE update, the graph explorer.                                     |
| [`runner-panel.md`](./e2e-scenarios/runner-panel.md)       | …you want the browser-driven proof over the panel a runner serves itself.                                                                                   |

## Wave-by-wave coverage rollup

The wave-1 **heartbeat/stall detection** (REAP staleness + `POST /api/fleet/runners/{id}/heartbeats` +
`blizzard runner heartbeat`), **store-and-forward outbound buffer** (FIFO drain, seq-idempotent `POST /api/fleet/events`
against the hub high-water mark), and **epoch fence** (lease-report keystone; zombie/stale-completion rejection) are
covered by the component tier; the wave-2 **human loop** — ask/answer park→resume, graph and runner-config gate
decisions, first-write-wins resolution, and requeue supersession, plus the `blizzard runner ask` / `blizzard hub answer`
/ `blizzard hub decisions` / `blizzard hub decide` / `blizzard hub requeue` CLI verbs — is covered by the component tier
and, end to end, by `test_ask_answer_e2e` and `test_gate_decision_e2e`; the wave-3 **board + fleet ops** — the live SSE
views, queue reorder/grouping, and the runner registry with its pause brake — is covered by the component tier (frontend
vitest with a fetch-stubbed client; `test_runner_paused` / `test_runner_registry` / `test_queue_shaping` on the Python
side) and, end to end through the browser, by `test_board_browser_e2e`. They join the P5 Python-QA/frontend/wheel rows
and the P4 `blizzard-mock` rows as real.
