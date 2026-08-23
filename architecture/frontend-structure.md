# Frontend structure

The Angular suite's where-does-it-go and what-depends-on-what map, and the sole owner of the container/presentational
split (`canon:one-owner`) — [`../standards/frontend.md`](../standards/frontend.md) cites the rules in this tree rather
than restating them. Each spoke's rules use the slot skeleton `winter-canon:/rule-shape.md` owns (`canon:rule-shape`).

| File                                                                               | When to read                                                                                                 |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [`./frontend-structure/containers.md`](./frontend-structure/containers.md)         | You are placing a component's logic, or deciding what a data-backed view may render before its read resolves |
| [`./frontend-structure/kit.md`](./frontend-structure/kit.md)                       | You are building a component's chrome and choosing between the shared kit and a local copy                   |
| [`./frontend-structure/disjoint-diffs.md`](./frontend-structure/disjoint-diffs.md) | You are adding to a shared file — a barrel, the SSE registry — and two agents' diffs must not collide        |
| [`../standards/frontend.md`](../standards/frontend.md)                             | You need the Angular toolchain rules — lint, test, the generated client                                      |
| [`./clean-architecture.md`](./clean-architecture.md)                               | You are placing daemon-side behavior instead — the counterpart to this map                                   |

`web:structural-gate`'s `max-lines` ceiling in [`../verification/blizzard.md`](../verification/blizzard.md) is this
tree's only tooled Detect; `bzh:frontend-kit-floor` and `bzh:frontend-empty-state-gated` are review questions.
