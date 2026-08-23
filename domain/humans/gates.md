# Gate decision

A **decision** is a gate's parking row, which parks the chunk `waiting_on_human` until a person resolves it. Spoke of
the [human-entry hub](../humans.md).

A decision is a durable multiple-choice ask written where a worker-judged node would have written its transition,
carrying the step's artifacts so the deciding human sees what they are judging.

- **The choices are the node's judgement choices** ([graphs/edges.md](../graphs/edges.md)) — what the board and chat bot
  render as buttons.
- **Pending derives**: a decision no resolving fact references is open, and the chunk derives `waiting_on_human` from it
  — no live lease while parked. Which fact resolves it:
  - **The transition the holding runner writes** (below) — the ordinary case.
  - **The migration record**, when the resolved choice migrates cross-graph, since a migration writes no transition
    ([work/migration.md](../work/migration.md)).
  - **The escalation**, when that migration's target is unresolvable.
  - **An operator's restart**, which moves the chunk off the gate without deciding it: the move itself closes the
    decision, and no choice is invented for the runner to then transition along.
- **Resolution is recorded once** — first write wins, like an answer ([asks.md](./asks.md)) — and the holding runner
  then writes the ordinary transition referencing the decision: the runner still advances the chunk.
- **Gates arrive two ways**: structurally, as a human-judged node in the graph; or by **runner configuration** selecting
  node names — human sign-off added to an existing workflow without editing any graph. At a human-judged node a
  runner-submitted transition is rejected; human sign-off cannot be bypassed.
