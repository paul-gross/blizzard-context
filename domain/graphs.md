# Workflow graphs

The definition a chunk travels: an immutable graph of nodes and edges, with the sessions and artifacts declared beside
them. Every edit mints a new graph, so anything pinned to a definition can trust it forever. Part of the
[domain model](./index.md); [work.md](./work.md) owns the chunk that travels a definition and the migration that moves
it between definitions.

| Spoke                                                   | When to read                                                                                                   |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| [identity.md](./graphs/identity.md)                     | Reasoning about which graph a name resolves to, or whether a graph's chunks drift to newer mints of its name   |
| [nodes.md](./graphs/nodes.md)                           | Reasoning about one station — what a node declares and which facet governs what                                |
| [edges.md](./graphs/edges.md)                           | Reasoning about a node's exit — how it is judged, what a choice is, and which edge it selects                  |
| [declared-sessions.md](./graphs/declared-sessions.md)   | Reasoning about the agent-context lineage several nodes share and the model, effort, and rotation policy on it |
| [declared-artifacts.md](./graphs/declared-artifacts.md) | Authoring a graph's `artifacts:` map — what the load and the mint-time validator accept                        |
| [ids-and-names.md](./graphs/ids-and-names.md)           | Deciding whether a reference carries an id or a name                                                           |

## See also

- [../standards/hub-nodes.md](../standards/hub-nodes.md) — the technical authoring contract a hub-executed node is held
  to.
- [../standards/worker-nodes.md](../standards/worker-nodes.md) — the technical authoring contract a worker node's
  declared outputs are held to.
