# Gate decisions

A gate's decision is a durable multiple-choice ask written where a worker-judged node would have written its transition,
carrying the step's artifacts for the deciding human; it is the gate's parking row — the chunk parks `waiting_on_human`
until a person resolves it. Spoke of the human-entry hub, [../humans.md](../humans.md).

A decision's choices are exactly the node's judgement choices, owned by [../graphs/edges.md](../graphs/edges.md).

## How a gate arises

Gates arrive structurally, as a human-judged node, or by runner configuration selecting node names — human sign-off
added without editing any graph. At a human-judged node a runner-submitted transition is rejected.

A decision records whether the graph declared its gate or a named runner's configuration imposed it. A runner declares
its gate set to the hub, which reports it and never enforces it.

## Resolution

A decision passes through two states, each derived and never stored. It is *waiting* while no resolution references it,
and the chunk derives `waiting_on_human` from a waiting one; the wait ends at the person's resolution. It is *closed*
once a fact consumes it, which can come later than the resolution. Resolution is recorded once — first write wins, like
an answer ([./asks.md](./asks.md)) — and the holding runner then writes the ordinary transition
([../work/transitions.md](../work/transitions.md)) referencing the decision: the runner still advances the chunk. Until
a closing fact references a runner-configured gate, the runner's plain completion out of that node-step — one naming no
decision — is refused, whether the gate is still waiting or already resolved: only the transition naming the decision
moves on, and only to the resolved choice. A decision closes by one of:

- the holding runner's transition — the ordinary case;
- a migration record, when the chosen choice migrates cross-graph — a migration writes no transition
  ([../work/migration.md](../work/migration.md));
- an escalation, when that migration's target is unresolvable;
- an operator's restart, whose move off the gate closes it — no choice is invented for the runner to transition along. A
  restart closes a decision a person already resolved but the runner has not yet moved on, so no runner later acts on
  that resolution.

The chunk ending — `stopped` or `done` — closes a decision too. A decision closed undecided, by a restart or by the
chunk ending, leaves the open list, and resolving it is refused.
