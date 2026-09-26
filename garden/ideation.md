# The `ideation` axis

The gardening axis that holds the product as built to the intent `blizzard-product:/charter/` declares, and asks what it
could become. A spoke of the [garden registry](./index.md); the four fields below are the shape `canon:gardening-axes`
requires. Each scope is a place to ideate — the surfaces a person drives, blizzard's structure, what the fleet uses,
what the fleet spends — and each field below is stated per scope where they differ.

## Evaluates

The distance between what blizzard is and what its charter says it is for — which no gate can see, because an absence
fails no test. Concretely, on this target:

**`features`** — what a person the charter describes still cannot do on a surface:

- Something a persona's card says they do, or need, that no surface lets them do.
- A workflow the mission or vision describes that a surface carries only partway, so the persona starts it there and
  finishes it by hand somewhere else.
- A question a persona is described as asking that the surface cannot answer.
- A capability one surface offers a persona and another surface, serving the same persona for the same task, withholds.

**`architecture`** — where blizzard's structure, or the constraints that govern it, could better serve what the charter
asks of it:

- A constraint the code honors that costs more than it protects — a seam, split, or layer every change pays for and the
  charter's work never leans on.
- A structural gap no declared constraint covers — a recurring shape, coupling, or boundary the code keeps improvising
  because `architecture/` states nothing about it.
- A direction the vision points toward — another harness, another forge, a larger fleet — that the current structure
  would resist, stated while the change is still cheap.
- Two parts of the codebase solving one structural problem two ways, where one declared pattern would serve both.

**`usage`** — the skills, agent types, context files, and graph nodes the fleet was built to use against the ones its
sessions leave a trace of using:

- Something built for the fleet that the counts show no sign of — a skill never invoked, or an agent type, node, or
  on-demand context file with no read, skill, or spawn call against it — over a window long enough for the absence to
  mean something.
- A kind of use that concentrates on a few of its entries while the rest sit idle — the fleet reaching for the same
  three things where a dozen were built.
- A use the fleet makes that nothing was built for — a file sessions keep opening that no hub routes to, or work an
  agent type is spawned for that no skill covers.
- A use whose weight contradicts what the fleet was meant to do — heavy where the charter expects a light touch, or
  absent where a persona's work depends on it.

**`cost`** — spend that exceeds what the work it bought produced, per node or per graph over a window:

- A node whose spend is large across the window while what it decides rarely changes — a gate that always passes, a
  review that seldom finds, a plan a later node rebuilds anyway.
- A graph whose per-chunk cost is set by its own shape — a loop that re-enters a heavy node by default, a fan-out that
  repeats the same read on every branch — rather than by the size of the work it carried.
- Spend on a node whose product nothing downstream consumes.
- Two graphs buying the same outcome at prices nothing about their work explains.
- A tier or effort default that pays for more model than the step's work uses.

## Scope

One slug per place to ideate.

| Slug           | Ground                                                                                                                                                                      |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `features`     | Blizzard's surfaces — the web board, the hub and runner command surfaces, and the hub's HTTP API — read one surface at a time against the personas they serve               |
| `architecture` | Blizzard's structure as built — the hub, runner, shared spine, and web suite — together with the constraints [`../architecture/`](../architecture/index.md) declares for it |
| `usage`        | The skills, agent types, agent-facing context files, and worker-executed graph nodes the workspace and blizzard declare, against the calls sessions make of them            |
| `cost`         | The fleet's model spend, summed per node across every graph that declares it and per graph by each chunk's current graph pin                                                |

## Criteria

`blizzard-product:/charter/` — its mission, vision, and personas — owns every statement of intent this axis judges
against and is the only home for that prose; each persona's card under `charter/personas/` is the single home of its
`persona:<slug>` id.

This axis judges against intent and enforces no standard. The charter says what the product is for, never what the code
must look like, so nothing it states is a rule the product can violate, and a proposal here is an opinion about what the
product could become rather than a finding of drift.

`features` reads the code and the charter and nothing else. `architecture` reads the code, the charter, and
[`../architecture/`](../architecture/index.md) — the constraints are its subject, not its yardstick: a proposal here may
argue for adding, changing, or retiring one. `usage` and `cost` read the fleet's own numbers through the runner's
lease-scoped analytics surface; the summaries are the evidence, the transcripts behind them are not:

| Scope   | Evidence                                                                                                                                                                      |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `usage` | `blizzard runner analytics counts skills`, `blizzard runner analytics counts agent-types`, `blizzard runner analytics counts files`, `blizzard runner analytics counts nodes` |
| `cost`  | `blizzard runner analytics spend nodes`, `blizzard runner analytics spend graphs`                                                                                             |

Every usage count covers three kinds of tool call and nothing else: a read-tool call, a skill invocation, and an agent
spawn. A skill is used only through a skill invocation, so a zero for a skill is evidence of disuse. For an agent type
or a node, a zero says only that none of those three calls was made there — a session working through the shell or an
editor leaves no trace, and a spawn lands in the spawning session's lane, not the spawned type's — and a magnitude ranks
those calls, not work done. For a file, the count sees only read-tool calls: a file the harness loads into context on
its own — the workspace and extension hubs, and everything they import — or one a session reads through the shell never
registers, so its zero is no evidence at all.

These bodies bound what counts as a gap:

- `blizzard-product:/epics.md` is the record of what is already planned. A capability, use, or saving `epics.md` already
  commits to is not a gap this axis reports; it is intent already on its way.
- Code that violates a constraint [`../architecture/`](../architecture/index.md) declares is out of range for every
  scope, `architecture` included: that drift is the [`architecture`](./architecture.md) axis's finding. What
  `architecture` holds is the opposite reading of the same ground — whether the constraints themselves, and the
  structure they shape, are the right ones — so a proposal there argues for a different rule or shape, never that the
  code breaks the current one.
- For `usage`, the [`agent-facing-context`](./agent-facing-context.md) axis's judgement of the harness's prose is out of
  range: what `usage` holds is only what the counts show, so a file every standard passes is still in range when the
  counts say no session opens it, and a file the counts show well read is out of range however its prose drifts.
- For `cost`, the [`performance`](./performance.md) axis's ground — the cost of blizzard's own code, the statements a
  hot path issues, the sweeps the hub runs — is out of range: `cost` holds only what the fleet pays its models to run a
  graph, never what the daemons pay to run themselves.

## Measurement

Every run records, proposals or none:

- Proposals delivered, per scope swept.
- One figure for the scope swept, which a count of proposals alone hides:
  - `features` — how many distinct personas the run's proposals serve, the breadth of what it found wanting.
  - `architecture` — how many distinct `architecture/` spokes the run's proposals would change or add to, the breadth of
    the structure it found wanting.
  - `usage` — the share of the scope's ground that reads zero in the window's counts, the number an accepted proposal to
    stop carrying something is meant to move.
  - `cost` — the share of the window's spend the run's proposals name, how much of what the fleet paid the run found a
    better use for.
