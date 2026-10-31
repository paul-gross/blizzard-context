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

| Spoke                                                    | When to read                                                                  |
| -------------------------------------------------------- | ----------------------------------------------------------------------------- |
| [delivery-policy.md](./e2e-scenarios/delivery-policy.md) | The pending delivery flow and repository landing order                        |
| [board.md](./e2e-scenarios/board.md)                     | Verifying operator interactions with the hub-served web app and its live data |
| [garden.md](./e2e-scenarios/garden.md)                   | The packaged garden graphs' run paths                                         |
