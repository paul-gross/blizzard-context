# Architecture — blizzard

Blizzard's **architecture guidance**: the structural invariants and design decisions a change must honor, read when
planning a change or reviewing a plan. Conforms to the canon concept at `winter-canon:/architecture-guidance.md`. Where
the companion [standards/](../standards/index.md) domain governs the code-quality details a finished change is held to,
this domain governs how the code is *structured and designed* — consulted before writing new code so you build with the
existing structure rather than reverse-engineering it.

**Read this index before changing the code of any blizzard daemon, seam, store, or the Angular suite**, and follow the
one row that matches your change rather than reading the whole tree.

Parent: [../index.md](../index.md).

| Doc                                                                                                                                                  | When to read                                                                                                                                                                                                                                                                   |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [./clean-architecture.md](./clean-architecture.md#domain-orchestration-split-bzhdomain-orchestration-split) § Domain-orchestration split             | Adding or changing a rule on a concept — a refusal, guard, legal transition, or state check, such as refusing a verb in some state — and deciding whether it lives on the model, the service, or the route, and how the route maps its error to a status                       |
| [./clean-architecture.md](./clean-architecture.md)                                                                                                   | Placing any other new behavior, or a type added to `wire/`, `foundation/`, or `auth_core/` — deciding which layer it belongs in and what that layer may depend on                                                                                                              |
| [./clean-architecture.md](./clean-architecture.md#domain-package-layers-bzhdomain-package-layers) § Domain package layers                            | Making one hub-domain concept package (`garden/`, `execution/`, `runners/`, …) or runner package (`leases/`, `lifecycle/`, `throttle/`, …) use another's types or data — which packages it may import                                                                          |
| [./clean-architecture.md](./clean-architecture.md#narrow-seams-and-step-context-protocols-bzhnarrow-seams) § Narrow seams and step context Protocols | Adding a runner loop step, or a member a step or service reads — the step's own context Protocol and the narrow seams a collaborator takes instead of a bundle                                                                                                                 |
| [./data-roles.md](./data-roles.md)                                                                                                                   | Adding, changing, or reviewing any data class under `src/blizzard/` — a `@dataclass`, `NamedTuple`, or pydantic model — or importing a `wire/` model somewhere new: choosing its role, where its role puts it, or fixing a `tests/test_layering.py` data-role failure          |
| [./repository-access.md](./repository-access.md)                                                                                                     | Touching persistence, or code that reaches it — deciding who may read a store, who may write it, what a domain call takes, or what a read may cost                                                                                                                             |
| [./system-shape.md](./system-shape.md)                                                                                                               | Designing a daemon, an external-system seam, a store schema, a workflow graph, a hub↔runner wire model, a configured record or a read of configuration, or anything crossing the runner–worker seam — the macro-shape invariants, and the route to the rule that governs yours |
| [./crash-correctness.md](./crash-correctness.md)                                                                                                     | Building or changing a daemon loop or its store, or adding or changing a periodic pass or lane — what makes `kill -9` at any step boundary a tested operation rather than a hope                                                                                               |
| [./frontend-structure.md](./frontend-structure.md)                                                                                                   | Placing or reviewing Angular code — deciding where a component, its data access, or its chrome belongs, or adding to a file several agents' diffs touch                                                                                                                        |

## See also

- [../verification/blizzard.md](../verification/blizzard.md) — how the guidance here is proven: the test tiers and the
  kill-9 sweep that exercises the crash-correctness requirements.
