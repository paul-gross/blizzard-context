# Workflow graphs

The routing hub for workflow graphs in the [domain model](./index.md). A workflow graph is the immutable definition a
chunk travels — nodes, edges, and declared sessions and artifacts. The chunk that travels a definition, and the
migration that moves it between definitions, are owned by [./work.md](./work.md).

| File                                                             | When to read                                                                                  |
| ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| [./graphs/nodes.md](./graphs/nodes.md)                           | Declaring a node's facets, or deciding which facet governs a behavior                         |
| [./graphs/edges.md](./graphs/edges.md)                           | Working out how a node's exit will be judged, or which edge its judgement selects             |
| [./graphs/declared-sessions.md](./graphs/declared-sessions.md)   | Declaring a session several nodes share, or setting the policy its lineage runs under         |
| [./graphs/declared-artifacts.md](./graphs/declared-artifacts.md) | Authoring a graph's `artifacts:` map — what load and the mint-time validator accept           |
| [./graphs/identity.md](./graphs/identity.md)                     | Which graph a name resolves to, and whether a graph's chunks drift to newer mints of its name |
| [./graphs/ids-and-names.md](./graphs/ids-and-names.md)           | Deciding whether a reference carries an id or a name                                          |
| [../standards/hub-nodes.md](../standards/hub-nodes.md)           | Authoring a hub-executed node — the contract that binds it                                    |
| [../standards/worker-nodes.md](../standards/worker-nodes.md)     | Authoring a worker node's declared outputs — the contract that binds them                     |
