# Frontend structure

The Angular suite's where-does-it-go / what-depends-on-what map — the frontend analog of
[./clean-architecture.md](./clean-architecture.md)'s dependency-inversion for the daemon side. This is the **sole
owner** of the container/presentational split (`canon:one-owner`): [../standards/frontend.md](../standards/frontend.md)
cites the rules here rather than restating them.

The rules live in the spokes below, grouped by the question a reader arrives with; each follows the slot skeleton owned
by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Routing

| File                                                          | Read when…                                                                                                     |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| [`containers.md`](./frontend-structure/containers.md)         | …you are placing a component's logic, or deciding what a data-backed view may render before its read resolves. |
| [`kit.md`](./frontend-structure/kit.md)                       | …you are building a component's chrome and choosing between the shared kit and a local copy.                   |
| [`disjoint-diffs.md`](./frontend-structure/disjoint-diffs.md) | …you are adding to a shared file — a barrel, the SSE registry — and two agents' diffs must not collide.        |

## See also

- [../standards/frontend.md](../standards/frontend.md) — the kit adoption rule (`bzh:frontend-kit`) cites
  `bzh:frontend-kit-floor` rather than restating it; the toolchain (lint/test/generated-client) rules live there.
- [../verification/blizzard.md](../verification/blizzard.md) — `web:structural-gate`, whose `max-lines` ceiling is the
  one tooled Detect in this tree; `bzh:frontend-kit-floor`'s and `bzh:frontend-empty-state-gated`'s are review
  questions.
- [./clean-architecture.md](./clean-architecture.md) — the daemon-side dependency-inversion this doc is the frontend's
  counterpart to.
