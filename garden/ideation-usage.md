# The `ideation:usage` axis

The gardening axis that holds what the fleet was built to use to what it actually uses, judged against the intent
`blizzard-product:/charter/` declares. A spoke of the [garden registry](./index.md); the four fields below are the shape
`canon:gardening-axes` requires.

## Evaluates

The distance between the skills, agent types, context files, and graph nodes the fleet was built to use and the ones its
sessions leave a trace of using — what nobody touches, and what is missing. Concretely, on this target:

- Something built for the fleet that the counts show no sign of — a skill never invoked, or an agent type, node, or
  on-demand context file with no read, skill, or spawn call against it — over a window long enough for the absence to
  mean something.
- A kind of use that concentrates on a few of its entries while the rest sit idle — the fleet reaching for the same
  three things where a dozen were built.
- A use the fleet makes that nothing was built for — a file sessions keep opening that no hub routes to, or work an
  agent type is spawned for that no skill covers.
- A use whose weight contradicts what the fleet was meant to do — heavy where the charter expects a light touch, or
  absent where a persona's work depends on it.

## Scope

One slug per kind of use.

| Slug            | Ground                                                                                                              |
| --------------- | ------------------------------------------------------------------------------------------------------------------- |
| `skills`        | The skills the workspace installs, against the invocations sessions make of them                                    |
| `agent-types`   | The agent types the workspace declares, against the read, skill, and spawn calls sessions of each type make         |
| `context-files` | The agent-facing files the workspace and its harness carry, against the on-demand reads sessions make of them       |
| `nodes`         | The worker-executed nodes blizzard's graphs declare, against the read, skill, and spawn calls sessions make at each |

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

Every count covers three kinds of tool call and nothing else: a read-tool call, a skill invocation, and an agent spawn.
A skill is used only through a skill invocation, so a zero for a skill is evidence of disuse. For an agent type or a
node, a zero says only that none of those three calls was made there — a session working through the shell or an editor
leaves no trace, and a spawn lands in the spawning session's lane, not the spawned type's — and a magnitude ranks those
calls, not work done. For a file, the count sees only read-tool calls: a file the harness loads into context on its own
— the workspace and extension hubs, and everything they import — or one a session reads through the shell never
registers, so its zero is no evidence at all.

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
- The share of each swept scope's ground that reads zero in the window's counts — the number an accepted proposal to
  stop carrying something is meant to move, which a count of proposals alone cannot show moving.
