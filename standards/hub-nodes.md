# Hub command nodes

The authoring contract for `executor: hub` — the generic hub command node primitive: the `run:` step shape, the env-var
interface a step's command reads, the outcome protocol that maps a step's stdout/exit code to a routed edge, and the
per-step idempotence a `run:` command must honor. [../domain/graphs/nodes.md](../domain/graphs/nodes.md) owns the
concept — a node's `executor` facet, and that a hub node is structurally agentless; this file owns the technical schema
a change to a `run:` script or a new hub node is held to, the same relationship [./wire.md](./wire.md) has to a route's
timestamp fields. Each rule follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

| Spoke                                                  | When to read                                                                     |
| ------------------------------------------------------ | -------------------------------------------------------------------------------- |
| [run-steps.md](./hub-nodes/run-steps.md)               | The node declares its work as `run:` steps                                       |
| [env-contract.md](./hub-nodes/env-contract.md)         | A step's command needs the chunk's identity, prior work, or the forge credential |
| [outcome-protocol.md](./hub-nodes/outcome-protocol.md) | A step must select a routed choice, poll, or bounce the chunk                    |
| [step-idempotence.md](./hub-nodes/step-idempotence.md) | A step's command must be safe to re-run after a crash                            |

## See also

- [../domain/graphs/nodes.md](../domain/graphs/nodes.md) — the conceptual node model this file's schema instantiates,
  and the `executor` facet that makes a node the hub's to run.
- [../domain/graphs/edges.md](../domain/graphs/edges.md) — the judgement and choices a hub node's script selects from.
- [../domain/graphs/ids-and-names.md](../domain/graphs/ids-and-names.md) — the ids-exact/names-correlate rule an
  artifact series and a migration key on.
- [../architecture/system-shape.md](../architecture/system-shape.md) — `bzh:deterministic-shell`, the invariant a hub
  node's agentlessness realizes.
- [../architecture/crash-correctness.md](../architecture/crash-correctness.md) — `bzh:crash-point-registry`, the
  `hubnode.*` family these steps' crash points belong to.
- [../verification/blizzard.md](../verification/blizzard.md) — `blizzard:crash-sweep`, which exercises the `hubnode.*`
  points this file's idempotence rule is proven against.
