# Workflows

The procedures a fleet agent follows end to end — how a feature reaches `master`, judging whether a change breaks a
supported release, and the code-restructuring procedures such as splitting a concept's domain and orchestration — the
harness's workflows routing hub. Each workflow document owns choreography and landing roles; the facts a step acts on
stay with their owners, pointed to. The passes only an operator drives — cutting and deploying a release, the findings
sweep, marshalling, the store fold — are the workspace's (`workspace:/context/project/workflows/index.md`). Parent hub:
[../index.md](../index.md).

| File                                                             | When to read                                                                                                                                          |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| [feature-delivery.md](./feature-delivery.md)                     | How a feature reaches `master`: blizzard orchestrates the delivery — read when working a node in one, or when delivering work outside a fleet         |
| [domain-orchestration-split.md](./domain-orchestration-split.md) | Told to split a concept's domain and orchestration, in any wording naming split, domain, and orchestration — moving its business rules onto its model |
| [judging-a-break.md](./judging-a-break.md)                       | Told to judge whether a change breaks a supported release — deciding each finding `blizzard-compat` reports                                           |
| [change-notes.md](./change-notes.md)                             | Making any change in `blizzard` — deciding whether it owes a change note and writing it                                                               |
