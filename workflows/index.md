# Workflows

How blizzard work reaches `master` — the harness's workflows routing hub. Each workflow document owns only ordering and
roles; the facts a step acts on stay with their owners, pointed to. Parent hub: [../index.md](../index.md).

| File                                         | When to read                                                                                                                                    |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [feature-delivery.md](./feature-delivery.md) | How a feature reaches `master`: blizzard orchestrates the delivery — read when working a node in one, or when delivering work outside a fleet   |
| [release.md](./release.md)                   | Cutting a milestone or release-candidate build — the tag-is-the-release sequence from a green `master` to a published wheel and container image |
