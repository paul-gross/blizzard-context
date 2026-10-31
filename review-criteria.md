# Review criteria — blizzard

Blizzard's **review criteria**: for each axis a review judges a change along, the context that owns what that axis is
judged against. Read it when reviewing a change to blizzard — follow the one row per axis you are judging, and where the
owning context gives the criterion a stable id, name that id in the finding. This file declares no criteria of its own:
where [verification/](./verification/index.md) owns how a change is proven, this file only routes a review to what
judges it.

Parent: [./index.md](./index.md).

| Axis               | Judged against                                                                                                                                                                                                                |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Correctness**    | [domain/](./domain/index.md) — the concept behavior the change must preserve — together with the [exemplars/](./exemplars/index.md) rows matching the surface it touches, the known-good shape the change is measured next to |
| **Architecture**   | [architecture/](./architecture/index.md) — the architecture guidance: the structural invariants and design decisions the change must honor                                                                                    |
| **Design quality** | [standards/](./standards/index.md) — the code-quality rules a finished change is held to, one row per surface the change touches                                                                                              |

A change to this harness's own prose is judged on every axis against the authoring conventions
[CONTRIBUTING.md](./CONTRIBUTING.md) §Authoring conventions routes to, not against the rows above.
