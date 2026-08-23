# Hub command nodes

The authoring contract for the generic hub command node — a node declaring `executor: hub`. The concept itself — a
node's `executor` facet, and that a hub node is structurally agentless — is owned by
[../domain/graphs/nodes.md](../domain/graphs/nodes.md); this file owns only the technical schema a change to a `run:`
script or a new hub node is held to. Each rule in this tree follows the slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`) and carries a stable `bzh:<slug>` id.

Parent: [./index.md](./index.md).

| Spoke                                                  | When to read                                                                     |
| ------------------------------------------------------ | -------------------------------------------------------------------------------- |
| [run-steps.md](./hub-nodes/run-steps.md)               | The node declares its work as `run:` steps                                       |
| [env-contract.md](./hub-nodes/env-contract.md)         | A step's command needs the chunk's identity, prior work, or the forge credential |
| [outcome-protocol.md](./hub-nodes/outcome-protocol.md) | A step must select a routed choice, poll, or bounce the chunk                    |
| [step-idempotence.md](./hub-nodes/step-idempotence.md) | A step's command must be safe to re-run after a crash                            |
