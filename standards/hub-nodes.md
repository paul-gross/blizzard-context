# Hub nodes

The authoring contract for a hub node — a node declaring `executor: hub`, which takes one of the hub's catalogued
actions. The concept itself — a node's `executor` facet, and that a hub node is structurally agentless — is owned by
[../domain/graphs/nodes.md](../domain/graphs/nodes.md); this file owns only the technical schema a change to a hub
action or a new hub node is held to. Each rule in this tree follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`) and carries a stable `bzh:<slug>` id.

Parent: [./index.md](./index.md).

| Spoke                                                  | When to read                                                                            |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| [action-shape.md](./hub-nodes/action-shape.md)         | The node declares its work as one catalogued `action:`                                  |
| [outcome-protocol.md](./hub-nodes/outcome-protocol.md) | An action's pass must answer a routed choice, poll, or bounce the chunk                 |
| [step-idempotence.md](./hub-nodes/step-idempotence.md) | An action's pass must be safe to re-run after a crash                                   |
| [action-purity.md](./hub-nodes/action-purity.md)       | The node names an action — writing or changing a hub action, or what its pass is handed |
