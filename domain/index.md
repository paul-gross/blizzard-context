# Domain — blizzard

Blizzard's **domain model**: what the concepts are, how they behave, and how they intertwine — with no technical detail.
"No technical detail" means no *implementation* vocabulary: no store column or table names, wire models, service
classes, or HTTP routes — those belong to [architecture/](../architecture/index.md) and
[standards/](../standards/index.md), and a domain file points there rather than spelling them. The vocabulary an
operator or graph author actually writes — a status name, an authored node's own keys — is domain vocabulary, and stays.
Conforms to the `domain/` slot of the canon harness shape (`winter-canon:/harness-structure.md`). This is the
correctness reference: read it when planning a change against intent, or when reviewing or verifying behavior against
the model — where the companion [architecture/](../architecture/index.md) domain governs how the *code* is structured,
this domain governs how the *concepts* work.

This domain owns the behavioral statement an agent plans and reviews against. Where it and the **code** disagree, the
code is current and this file is the one to fix.

This tree is also the fixed home a domain-concept fact relocates to when code prose restates it (`bzh:one-prose-home`):
the fact moves here, and the restating code sites reduce to a pointer at the section that now states it.

Parent: [../index.md](../index.md).

| Doc                                | When to read                                                                                                                                                                                                |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [./work.md](./work.md)             | Reasoning about a unit of work — what a chunk is, the statuses it can be in, how transitions move it, how migration re-pins it across graphs, and how a restart re-aims it within one                       |
| [./graphs.md](./graphs.md)         | Reasoning about the workflow definition — graphs and their immutability, nodes, edges, judgements and choices, and the ids-exact/names-correlate philosophy                                                 |
| [./execution.md](./execution.md)   | Reasoning about who runs a chunk — the hub/runner responsibility split, acquisition and routes, leases and epochs, what a worker session is primed with, and how tenure survives failure                    |
| [./artifacts.md](./artifacts.md)   | Reasoning about an artifact — what work produces and how it lands, what a graph declares beside its nodes for workers to read, the never-code rule, and delivery as graph-authored hub-command-node content |
| [./humans.md](./humans.md)         | Reasoning about where people enter the loop — asks, gate decisions, escalation, takeover, and the two parked conditions they produce                                                                        |
| [./operations.md](./operations.md) | Reasoning about operational visibility — the durable, typed, severity-ranked operational event log that surfaces worker/runner failures, and how escalation appears in it as one unified event kind         |
