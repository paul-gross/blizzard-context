# Workflows

The procedures the harness choreographs end to end — how blizzard work reaches `master`, and the passes an operator or
agent drives by hand — the harness's workflows routing hub. Each workflow document owns choreography and landing roles;
the facts a step acts on stay with their owners, pointed to. Parent hub: [../index.md](../index.md).

| File                                                             | When to read                                                                                                                                          |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| [feature-delivery.md](./feature-delivery.md)                     | How a feature reaches `master`: blizzard orchestrates the delivery — read when working a node in one, or when delivering work outside a fleet         |
| [release.md](./release.md)                                       | Cutting a milestone or release-candidate build — the tag-is-the-release sequence from a green `master` to a published wheel and container image       |
| [findings-sweep.md](./findings-sweep.md)                         | Running the findings sweep — the recurring operator pass that re-verifies the hub's live findings and drafts them into proposals or withdrawals       |
| [marshalling.md](./marshalling.md)                               | Told to marshal the backlog, or minting a chunk by any path — turning resting chunks into ordered, claimable work                                     |
| [domain-orchestration-split.md](./domain-orchestration-split.md) | Told to split a concept's domain and orchestration, in any wording naming split, domain, and orchestration — moving its business rules onto its model |
