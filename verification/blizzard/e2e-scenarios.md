# The standing e2e scenario registry — `blizzard:e2e` (`bzh:e2e-scenario-registry`)

The e2e suite is a standing smoke suite of full-stack scenarios, each self-managing the forge, hub, and runner over a
minted `blizzard-mock` fixture — every seam real, no tokens or network. This registry is the single authoritative
scenario-by-scenario list for the suite; [`../blizzard.md`](../blizzard.md) `## Commands` names the `blizzard:e2e`
command itself.

The suite runs as `mise run e2e`, which is `BLIZZARD_E2E=1 uv run pytest tests/e2e/`. Heartbeat/stall detection, the
store-and-forward outbound event buffer, and the epoch fence are proven at the component tier, not by this suite.

Taken together the scenarios cover:

- the canonical `build → review → deliver` shape
- its human-loop variants
- the operator board and its mobile glance shell
- the graph explorer
- the authored post-merge edge
- the cross-graph migration
- node session-mode continuity
- the browser login/session lifecycle
- the multi-daemon runner SSO federation
- the operational event log
- resume-time spawn-preamble elision
- the forge-status label projection
- checks-gate enforcement
- the YAML-authored delivery policies and their conflict path
- the chunk board's Transcripts tab
- the runner panel's own live SSE stream
- the non-code spike
- the packaged garden-routine graph's four run paths

Scenario detail lives under `./e2e-scenarios/`, one spoke file per reader question. Each scenario module is a `##`
section homed in exactly one spoke — check C of `blizzard-context:/scripts/check-registry-drift.py` parses this hub and
every spoke and fails a module documented in more than one file, so single-homing is machine-enforced. This hub carries
no module sections; the routing table below is the routing map and the discovery entry point for the spokes.

| Spoke                                                    | When to read                                                                                                             |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| [delivery-loop.md](./e2e-scenarios/delivery-loop.md)     | The canonical delivery shape, the chunk shapes riding it, and the edges carrying a chunk past its graph or past the land |
| [human-loop.md](./e2e-scenarios/human-loop.md)           | The stops-for-a-person scenarios — retries exhausted, a question asked, a gated decision                                 |
| [delivery-policy.md](./e2e-scenarios/delivery-policy.md) | `deliver` against a red check, conflict, or pending CI, plus the forge label projection                                  |
| [node-sessions.md](./e2e-scenarios/node-sessions.md)     | Which session a node resumes and what a resumed spawn re-sends                                                           |
| [auth.md](./e2e-scenarios/auth.md)                       | The hub login dance and the multi-daemon runner SSO bounce                                                               |
| [board.md](./e2e-scenarios/board.md)                     | The browser proofs over the hub-served web app — board views, live SSE updates, the graph explorer                       |
| [runner-panel.md](./e2e-scenarios/runner-panel.md)       | The panel a runner serves itself                                                                                         |
| [garden.md](./e2e-scenarios/garden.md)                   | The packaged garden-routine graph's run paths — findings, proposals, and the rejected-delivery bounce                    |
