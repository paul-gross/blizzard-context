# The `ideation:usage` axis

The gardening axis that holds what the fleet was built to use to what it actually uses, judged against the intent
`blizzard-product:/charter/` declares. A spoke of the [garden registry](./index.md); the four fields below are the shape
`canon:gardening-axes` requires.

## Evaluates

The distance between the skills, agent types, context files, and graph nodes the fleet was built to use and the ones its
sessions actually invoke, spawn, open, and pass through — what nobody touches, and what is missing. Concretely, on this
target:

- Something built for the fleet that the counts say nothing uses — a skill never invoked, an agent type never spawned, a
  context file never opened, a node no chunk passes through — over a window long enough for the absence to mean
  something.
- A kind of use that concentrates on a few of its entries while the rest sit idle — the fleet reaching for the same
  three things where a dozen were built.
- A use the fleet makes that nothing was built for — a file sessions keep opening that no hub routes to, or work an
  agent type is spawned for that no skill covers.
- A use whose weight contradicts what the fleet was meant to do — heavy where the charter expects a light touch, or
  absent where a persona's work depends on it.

## Scope

One slug per kind of use.

| Slug            | Ground                                                                                              |
| --------------- | --------------------------------------------------------------------------------------------------- |
| `skills`        | The skills the workspace installs, against the invocations sessions make of them                    |
| `agent-types`   | The agent types the workspace declares, against the activity sessions of each type generate         |
| `context-files` | The agent-facing files the workspace and its harness carry, against the reads sessions make of them |
| `nodes`         | The nodes blizzard's graphs declare, against the activity sessions record at each                   |

## Criteria

`blizzard-product:/charter/` — its mission, vision, and personas — owns every statement of intent this axis judges
against and is the only home for that prose. This axis judges against intent and enforces no standard: a proposal here
is an opinion about what the fleet could stop carrying or start carrying, not a finding of drift.

The evidence is the fleet's own usage counts, read through the runner's lease-scoped analytics surface — one read per
scope. The summaries are the evidence; the transcripts behind them are not:

| Scope           | Evidence                                       |
| --------------- | ---------------------------------------------- |
| `skills`        | `blizzard runner analytics counts skills`      |
| `agent-types`   | `blizzard runner analytics counts agent-types` |
| `context-files` | `blizzard runner analytics counts files`       |
| `nodes`         | `blizzard runner analytics counts nodes`       |

The `agent-types` and `nodes` reads count every event a session records under an agent type or at a node, not spawns or
steps: their magnitudes measure how much activity each entry carries, so one long-running agent or one chatty node reads
heavy on its own. A zero still means the entry went unused.

Two bodies bound what counts as a gap:

- `blizzard-product:/epics.md` is the record of what is already planned. A use `epics.md` already commits to building or
  retiring is not a gap this axis reports; it is intent already on its way.
- The [`agent-facing-context`](./agent-facing-context.md) axis judges the harness's prose by reading it against the
  canon's standard — whether a rule is reachable, routes truthfully, and weighs what it earns. That judgement is out of
  range here: what this axis holds is only what the counts show, so a file every standard passes is still in range when
  the counts say no session opens it, and a file the counts show well read is out of range however its prose drifts.

## Measurement

Every run records, proposals or none:

- Proposals delivered, per scope swept.
- The share of each swept scope's ground that the window's counts show untouched — the number an accepted proposal to
  stop carrying something is meant to move, which a count of proposals alone cannot show moving.
