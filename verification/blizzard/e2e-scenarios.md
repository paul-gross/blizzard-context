# The standing e2e scenario registry — `blizzard:e2e` (`bzh:e2e-scenario-registry`)

The e2e suite is a standing smoke suite of full-stack scenarios, each self-managing the forge, hub, and runner over a
disposable git origin and `blizzard-mock` services — every seam real, no tokens or network. This registry is the single
authoritative scenario-by-scenario list for the suite; [`../blizzard.md`](../blizzard.md) `## Commands` names the
`blizzard:e2e` command itself.

The suite runs as `mise run e2e`, which is `BLIZZARD_E2E=1 uv run pytest tests/e2e/`. Heartbeat/stall detection, the
store-and-forward outbound event buffer, and the epoch fence are proven at the component tier, not by this suite.

Scenario detail lives under `./e2e-scenarios/`, one spoke file per reader question. Each scenario module is a `##`
section homed in exactly one spoke — check C of `blizzard-context:/scripts/check-registry-drift.py` parses this hub and
every spoke and fails a module documented in more than one file, so single-homing is machine-enforced. This hub carries
no module sections; the routing table below is the routing map and the discovery entry point for the spokes.

| Spoke                                                    | When to read                                                                                                                                             |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [delivery-loop.md](./e2e-scenarios/delivery-loop.md)     | The canonical delivery shape, the chunk shapes riding it, and the edges carrying a chunk past its graph or past the land                                 |
| [human-loop.md](./e2e-scenarios/human-loop.md)           | The stops-for-a-person scenarios — retries exhausted, a question asked, a gated decision                                                                 |
| [delivery-policy.md](./e2e-scenarios/delivery-policy.md) | `deliver` against a red check, conflict, or pending CI, plus the forge label projection                                                                  |
| [node-sessions.md](./e2e-scenarios/node-sessions.md)     | What a node's session carries from one entry to the next                                                                                                 |
| [auth.md](./e2e-scenarios/auth.md)                       | The hub login dance and the multi-daemon runner SSO bounce                                                                                               |
| [board.md](./e2e-scenarios/board.md)                     | The browser proofs over the hub-served web app — board views, live SSE updates, the graph explorer                                                       |
| [runner-panel.md](./e2e-scenarios/runner-panel.md)       | The panel a runner serves itself                                                                                                                         |
| [garden.md](./e2e-scenarios/garden.md)                   | The packaged garden graphs' run paths                                                                                                                    |
| [egress.md](./e2e-scenarios/egress.md)                   | The hub's fact export proven from its files alone — the steps and spend of a night of chunks, or the derived events, read back the way a warehouse would |
