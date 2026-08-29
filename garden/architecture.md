# The `architecture` axis

The gardening axis that holds blizzard's code to the structure [`../architecture/`](../architecture/index.md) declares.
A spoke of the [garden registry](./index.md); the four fields below are the shape `canon:gardening-axes` requires.

## Evaluates

Structural drift — the code still passing every gate while diverging from the shape it was designed to. Concretely, on
this target:

- A layer reaching outward, or an inner layer naming a concrete outer one.
- A seam declared in the wrong package, or absent where an external system is reached directly.
- A seam wide enough that no collaborator can depend on only what its job needs, or a narrow variant that resolves to
  the wide one at run time.
- A collaborator building its own store, client, clock, or subprocess runner instead of receiving it.
- On the Angular side: a data-injecting component owning domain markup, and chrome re-typed rather than composed.
- One pattern implemented three ways across a tree, where the divergence — not any one implementation — is the finding.

## Scope

| Slug            | Ground                                                                      |
| --------------- | --------------------------------------------------------------------------- |
| `hub-daemon`    | The hub's domain, stores, API, delivery, graphs, and work sources           |
| `runner-daemon` | The runner's domain, loop, stores, API, harness, environments, and selftest |
| `shared-spine`  | The daemon-neutral layer both daemons depend on, and the wire models        |
| `cli-surface`   | The hub and runner command surfaces and the shared CLI entry package        |
| `web-suite`     | The Angular libraries and apps                                              |

## Criteria

[`../architecture/index.md`](../architecture/index.md) and the tree beneath it, which owns every rule this axis judges
by and is the only home for their prose. [`../standards/index.md`](../standards/index.md) is in range only where a
standard is structural — where the finding is about where code lives or what depends on what, not how a line is written.

A rule already enforced by a command is out of range: it belongs to its gate, which judges every change rather than
every run of this axis, and judging it here too would give one check two owners
(`winter-canon:/enforcement-channels.md`).

## Measurement

Every run records, findings or none:

- Findings opened, per scope swept.
- How many distinct rule ids under [`../architecture/`](../architecture/index.md) the run found at least one violation
  of — the breadth of drift, which a count of findings alone hides when one rule accounts for most of them.
