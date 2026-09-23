# The `ideation:features` axis

The gardening axis that holds blizzard's surfaces to the intent `blizzard-product:/charter/` declares. A spoke of the
[garden registry](./index.md); the four fields below are the shape `canon:gardening-axes` requires.

## Evaluates

What a person the charter describes still cannot do on one surface — the distance between a surface as built and the
intent it was built to serve, which no gate can see, because an absence fails no test. Concretely, on this target:

- Something a persona's card says they do, or need, that no surface lets them do.
- A workflow the mission or vision describes that a surface carries only partway, so the persona starts it there and
  finishes it by hand somewhere else.
- A question a persona is described as asking that the surface cannot answer.
- A capability one surface offers a persona and another surface, serving the same persona for the same task, withholds.

## Scope

One slug per surface.

| Slug         | Ground                                                                               |
| ------------ | ------------------------------------------------------------------------------------ |
| `board`      | The web board — the Angular apps and libraries a person drives in a browser          |
| `hub-cli`    | The hub command surface — what an operator can do to the fleet from a terminal       |
| `runner-cli` | The runner command surface — the operator's verbs and the worker's                   |
| `hub-api`    | The hub's HTTP API — what a client, a runner, or a worker session can ask of the hub |

## Criteria

`blizzard-product:/charter/` — its mission, vision, and personas — owns every statement of intent this axis judges
against and is the only home for that prose; the personas file owns the `persona:<slug>` ids a proposal names the person
it serves by.

This axis judges against intent and enforces no standard. The charter says what the product is for, never what the code
must look like, so nothing it states is a rule a surface can violate, and a proposal here is an opinion about what the
product could become rather than a finding of drift. That is also why no command is out of range: no gate judges this
ground, and no test can.

Two bodies bound what counts as a gap:

- `blizzard-product:/epics.md` is the record of what is already planned. A capability the registry carries is not a gap
  this axis reports; it is intent already on its way.
- [`../architecture/`](../architecture/index.md) is out of range. The [`architecture`](./architecture.md) axis judges
  drift from the constraints it declares, and proposing to change those constraints is the same code read in the
  opposite direction, which is one axis's ground rather than two.

## Measurement

Every run records, proposals or none:

- Proposals delivered, per scope swept.
- How many distinct personas those proposals serve — the breadth of what the run found wanting, which a count of
  proposals alone hides when one persona accounts for most of them.
