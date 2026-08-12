# Architecture — blizzard

Blizzard's **architecture guidance**: the structural invariants and design decisions a change must honor, read when
planning a change or reviewing a plan. Conforms to the canon concept at `winter-canon:/architecture-guidance.md`. Where
the companion [standards/](../standards/index.md) domain governs the code-quality details a finished change is held to,
this domain governs how the code is *structured and designed* — consulted before writing new code so you build with the
existing structure rather than reverse-engineering it.

**Read this index before changing the code of any blizzard daemon, seam, store, or the Angular suite**, and follow the
one row that matches your change rather than reading the whole tree.

Parent: [../index.md](../index.md).

| Doc                                                | When to read                                                                                                                                                                              |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [./clean-architecture.md](./clean-architecture.md) | Placing new behavior — the CLEAN layering blizzard carries over from winter: screaming layout, a dependency-free domain core, dependency inversion, and injection at the composition root |
| [./repository-access.md](./repository-access.md)   | Touching persistence or a controller — the read/write repository split, which layer may write, and the domain-takes-objects rule                                                          |
| [./system-shape.md](./system-shape.md)             | Designing a daemon, an external-system seam, or a store schema — the deterministic-shell/intelligent-core split, the pluggable-seam rule, and store-facts-derive-status                   |
| [./crash-correctness.md](./crash-correctness.md)   | Building or changing a daemon loop or its store — what makes `kill -9` at any step boundary a tested operation rather than a hope                                                         |
| [./frontend-structure.md](./frontend-structure.md) | Placing or reviewing Angular code — the container/presentational split, the shared kit as the presentational floor, and the sub-barrel/SSE-registry disjoint-diff mechanism               |

## See also

- [../verification/blizzard.md](../verification/blizzard.md) — how the guidance here is proven: the test tiers and the
  kill-9 sweep that exercises the crash-correctness requirements.
