# Architecture — blizzard

Blizzard's **architecture guidance**: the structural invariants and design decisions a change must honor, read when
planning a change or reviewing a plan. Conforms to the canon concept at `winter-canon:/architecture-guidance.md`. Where
the companion [standards/](../standards/index.md) domain governs the code-quality details a finished change is held to,
this domain governs how the code is *structured and designed* — consulted before writing new code so you build with the
existing structure rather than reverse-engineering it.

**Read this index before changing the code of any blizzard daemon, seam, store, or the Angular suite**, and follow the
one row that matches your change rather than reading the whole tree.

Parent: [../index.md](../index.md).

| Doc                                                | When to read                                                                                                                                                                                          |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [./clean-architecture.md](./clean-architecture.md) | Placing new behavior — deciding which layer it belongs in and what that layer may depend on                                                                                                           |
| [./repository-access.md](./repository-access.md)   | Touching persistence, or a controller that reaches it — deciding who may read a store, who may write it, and what a domain call takes                                                                 |
| [./system-shape.md](./system-shape.md)             | Designing a daemon, an external-system seam, a store schema, a workflow graph, or anything crossing the runner–worker seam — the macro-shape invariants, and the route to the rule that governs yours |
| [./crash-correctness.md](./crash-correctness.md)   | Building or changing a daemon loop or its store — what makes `kill -9` at any step boundary a tested operation rather than a hope                                                                     |
| [./frontend-structure.md](./frontend-structure.md) | Placing or reviewing Angular code — deciding where a component, its data access, or its chrome belongs                                                                                                |

## See also

- [../verification/blizzard.md](../verification/blizzard.md) — how the guidance here is proven: the test tiers and the
  kill-9 sweep that exercises the crash-correctness requirements.
