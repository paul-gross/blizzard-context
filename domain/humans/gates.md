# Gate decisions

A gate's decision is a durable multiple-choice ask written where a worker-judged node would have written its transition,
carrying the step's artifacts for the deciding human; it is the gate's parking row — the chunk parks `waiting_on_human`
until a person resolves it. Spoke of the human-entry hub, [../humans.md](../humans.md).

A decision's choices are exactly the node's judgement choices, owned by [../graphs/edges.md](../graphs/edges.md).

## How a gate arises

Gates arrive structurally, as a human-judged node, or by runner configuration selecting node names — human sign-off
added without editing any graph. At a human-judged node a runner-submitted transition is rejected.

## Resolution

Pending derives: a decision is open while no resolving fact references it, and the chunk derives `waiting_on_human` from
an open one. Resolution is recorded once — first write wins, like an answer ([./asks.md](./asks.md)) — and the holding
runner then writes the ordinary transition ([../work/transitions.md](../work/transitions.md)) referencing the decision:
the runner still advances the chunk. A decision resolves by one of:

- the holding runner's transition — the ordinary case;
- a migration record, when the chosen choice migrates cross-graph — a migration writes no transition
  ([../work/migration.md](../work/migration.md));
- an escalation, when that migration's target is unresolvable;
- an operator's restart, whose move off the gate closes it undecided — no choice is invented for the runner to
  transition along.
