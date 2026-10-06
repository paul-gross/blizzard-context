# Garden

Blizzard's **gardening-axes registry** — the named axes along which blizzard is recurringly evaluated, each judged by
the criteria its entry points at. Conforms to the canon concept at `winter-canon:/gardening-axes.md`
(`canon:gardening-axes`), which owns the registry's required shape; this file is its blizzard instance.

An evaluation pass names an axis and resolves it here; `canon:gardening-axes` owns what resolution means and what a pass
does when the axis is undeclared.

Parent: [../index.md](../index.md).

| Axis                                                | Evaluates                                                                                                           |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [`agent-facing-context`](./agent-facing-context.md) | Guidance drift in this harness's own prose                                                                          |
| [`architecture`](./architecture.md)                 | Structural drift in blizzard's code                                                                                 |
| [`comments`](./comments.md)                         | Prose drift in blizzard's code comments and docstrings                                                              |
| [`domain-conformance`](./domain-conformance.md)     | Disagreement between the behavior the domain model declares and the behavior the code implements and the suite pins |
| [`fitness`](./fitness.md)                           | Headroom and warnings no gate enforces                                                                              |
| [`ideation`](./ideation.md)                         | What the product could become, against its charter                                                                  |
| [`mutation-testing`](./mutation-testing.md)         | Behavior the fast tiers run but do not check — surfaced as mutants that survive them                                |
| [`performance`](./performance.md)                   | Cost drift in blizzard's hot paths                                                                                  |

## Scope slugs

An axis declares the scope slugs a run of it may be narrowed to. A slug is lowercase letters, digits, and hyphens, and
it means the same ground on every run — which is what makes a per-scope measurement a trend rather than a coincidence. A
run naming no scope sweeps the axis's whole ground.

## What an entry may not carry

Each entry declares only what `canon:gardening-axes` requires of it: what the axis evaluates, the scopes it covers, a
pointer to the criteria it judges against, and the measurement every run records. It restates no standard — an entry is
a router to criteria, not their second home — and it describes no pass, prompt, graph, or filing procedure, all of which
are methodology owned by whatever executes the pass.
