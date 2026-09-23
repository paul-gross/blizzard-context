# The `ideation:cost` axis

The gardening axis that holds what the fleet spends to what the spend bought, judged against the intent
`blizzard-product:/charter/` declares. A spoke of the [garden registry](./index.md); the four fields below are the shape
`canon:gardening-axes` requires.

## Evaluates

Where spend exceeds what the work it bought produced — a node or a graph whose usage and cost, summed over a window, are
out of proportion to what passing through it changed. Concretely, on this target:

- A node whose spend is large across the window while what it decides rarely changes — a gate that always passes, a
  review that seldom finds, a plan a later node rebuilds anyway.
- A graph whose per-chunk cost is set by its own shape — a loop that re-enters a heavy node by default, a fan-out that
  repeats the same read on every branch — rather than by the size of the work it carried.
- Spend on a node whose product nothing downstream consumes.
- Two graphs buying the same outcome at prices nothing about their work explains.
- A tier or effort default that pays for more model than the step's work uses.

## Scope

One slug per spend profile.

| Slug     | Ground                                                                                               |
| -------- | ---------------------------------------------------------------------------------------------------- |
| `nodes`  | The per-node profile — usage and cost summed by node, across every graph that declares the node      |
| `graphs` | The per-graph profile — usage and cost summed by graph, attributed to each chunk's current graph pin |

## Criteria

`blizzard-product:/charter/` — its mission, vision, and personas — owns every statement of intent this axis judges
against and is the only home for that prose. This axis judges against intent and enforces no standard: a proposal here
is an opinion about where the fleet's spend could buy more, not a finding of drift.

The evidence is the fleet's own spend, read through the runner's lease-scoped analytics surface — one read per scope.
The summaries are the evidence; the transcripts behind them are not:

| Scope    | Evidence                                 |
| -------- | ---------------------------------------- |
| `nodes`  | `blizzard runner analytics spend nodes`  |
| `graphs` | `blizzard runner analytics spend graphs` |

Two bodies bound what counts as a gap:

- `blizzard-product:/epics.md` is the record of what is already planned. A saving `epics.md` already commits to is not a
  gap this axis reports; it is intent already on its way.
- The [`performance`](./performance.md) axis judges the cost of blizzard's own code — the statements a hot path issues,
  the sweeps the hub runs — against the rules [`../architecture/`](../architecture/index.md) declares. That ground is
  out of range here: this axis holds only what the fleet pays its models to run a graph, never what the daemons pay to
  run themselves.

## Measurement

Every run records, proposals or none:

- Proposals delivered, per scope swept.
- The share of the window's spend the run's proposals name, per scope swept — how much of what the fleet paid the run
  found a better use for, which a count of proposals alone hides when each names a node that costs nothing.
