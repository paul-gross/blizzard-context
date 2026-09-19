# Domain model

Blizzard's domain-model hub: the concepts, how they behave, and how they intertwine — with no technical detail. It is
the correctness reference — read it when planning against intent or verifying behavior against the model;
[`architecture/`](../architecture/index.md) owns code structure, this tree owns concept behavior. The tree fills the
`domain/` slot of the harness shape at `winter-canon:/harness-structure.md`. Parent hub: [../index.md](../index.md).

Per `bzh:one-prose-home`, a domain-concept fact restated in code prose relocates here for good, the code sites reducing
to pointers at its section; and where domain and code disagree, code is current — fix the domain file.

| File                                                     | When to read                                                                                                                                                            |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [work.md](./work.md)                                     | Reasoning about a unit of work — what a chunk is, its derived status, a fact moving it within or across graphs, or how the `not_ready` list or `ready` queue is ordered |
| [graphs.md](./graphs.md)                                 | Reasoning about, or authoring, the immutable workflow definition a chunk travels — itself a hub over parts                                                              |
| [execution.md](./execution.md)                           | Reasoning about who runs a chunk, or what an operator's lever does to one in flight — itself a hub over parts                                                           |
| [artifacts.md](./artifacts.md)                           | Reasoning about anything a chunk produces or a graph hands its workers, or about how delivery is authored and lands                                                     |
| [humans.md](./humans.md)                                 | Reasoning about where a person enters the loop, or a chunk parked on one                                                                                                |
| [operations.md](./operations.md)                         | Reasoning about what an operator sees of the fleet — which failures reach the event log, or what the activity feed shows and omits                                      |
| [routines-and-scopes.md](./routines-and-scopes.md)       | Reasoning about a routine or a scope, about what a run is addressed at and inherits from them, or about what refuses one                                                |
| [findings-and-proposals.md](./findings-and-proposals.md) | Reasoning about a finding a routine's run reports, or a garden proposal answering findings — what either is, and how it opens, exits, or closes                         |
| [no-technical-detail.md](./no-technical-detail.md)       | Authoring or reviewing a file in this tree — deciding whether a claim is technical detail the tree refuses, or which file states a key inside a delegated contract      |
