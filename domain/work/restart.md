# Restart — an operator's forced move onto a node

Part of [work.md](../work.md), the chunk and its lifecycle.

An operator's forced move of a chunk onto a node, **now** — its own recorded fact, neither a transition nor a migration.

- **It is an event, not an intent.** Unlike a standing intended migration ([migration.md](./migration.md)), consulted at
  the chunk's next transition, a restart has already happened when the call returns: there is nothing to cancel and
  nothing to overwrite, and a second one is a second move rather than a replacement of the first.
- **It can cross graphs, and re-pinning is still migration's job.** *Where* a chunk stands is a restart's to change;
  *which* graph it is on is a migration's to record. So a restart that names another graph is **both**: one migration
  fact for the re-pin and one restart fact for the forced clean re-entry, written together in a single store
  transaction, at one instant and one epoch, with the restart the newer of the two — so the chunk stands where the
  restart put it, on the graph the migration pinned it to, and no crash can land one half without the other. Naming no
  other graph, it is the restart fact alone. Either way there is nothing to wait for: unlike an intended migration, the
  move has happened when the call returns, so a chunk standing mid-graph on a superseded mint reaches the current one
  without first running a node-step to manufacture the transition an intent would need.
- **Raising the fence is how it preempts.** The epoch the move mints belongs to [execution.md](../execution.md) §Lease
  and epoch; what follows from it here is that the displaced attempt's next state-advancing write is rejected as stale
  (`bzh:epoch-fencing`) and the holding runner tears the attempt down on its next reconciliation. Nothing relies on the
  worker having really died.
- **The claim survives it** — what a route, a tenure and its environments outlive belongs to
  [execution.md](../execution.md) §Acquisition and the route. The consequence here: the same runner re-enters the node
  with the work already on disk. A chunk with **no** claim moves just as well, and simply waits in the queue at its new
  node for whoever claims it next.
- **Artifacts already durably recorded stay recorded.** Nothing rewinds what the chunk has produced. That is a narrower
  claim than it sounds: a step's artifacts land atomically with the transition it is judged into
  ([transitions.md](./transitions.md), [artifacts.md](../artifacts.md)), so a step the move interrupts has no artifacts
  to keep — only the steps that already landed do.
- **It does not spend the node's retry budget.** A node's budget counts the attempts it *failed*, and a preempted
  attempt was superseded rather than failed — so restarting a stuck step never carries it toward `retries.exhausted`,
  and an operator cannot escalate the chunk they are rescuing by rescuing it too often.
- **The re-entry starts on a freshly minted session.** Restarting is how an operator hands a step clean context, so the
  node is entered on a new session rather than the one its declaration would have resumed, under the target node's
  currently declared configuration — the second override of the node's own `session` facet ([graphs.md](../graphs.md)
  §Node). That freshness derives from the move's own fact, so it holds for every re-entry into the forced visit, not
  only the first. Across graphs, "the target node's" means the **target graph's**: the re-entry is stamped with the
  model, effort and compaction window the graph it landed on declares, never the departed graph's.
- **Whatever parked or re-aimed the chunk is consumed with the move.** An open ask is answered — exactly one answer ever
  exists, so a person who already answered still wins — an open gate decision is closed by the move itself, and an open
  escalation is superseded exactly as a requeue supersedes one ([humans.md](../humans.md)). A cross-graph move also
  clears any standing intended migration ([migration.md](./migration.md)). Nothing may survive to re-park or re-aim the
  chunk at a node it is no longer standing on.
- **The landed node's own `executor` governs**, exactly as it does for an ordinary transition or a migration's landing
  ([graphs.md](../graphs.md) §Node).
- **Where it lands.** A named node is resolved **by name** against the graph the move lands on — the named target graph
  when it crosses, the chunk's own otherwise — the way [migration.md](./migration.md) resolves its own forced landing.
  Unnamed, the move lands on the chunk's current node: restart this step, on clean context, is the common case, and
  across graphs that same node **name** is matched onto the target, which is `auto` migration's own landing rule.
- **What it refuses**, writing nothing either way:
  - **A terminal chunk** — there is nothing to re-enter.
  - **A named node the landing graph does not carry**, and, when it crosses, **a current node name the target graph does
    not match**. The operator said where the chunk goes; an unmatched name is a mistake rather than a landing to fall
    back from, and the target's entry node is never quietly substituted for it.
  - **A chunk standing on a node its own graph does not carry**, with no node named. Rewinding it to the entry would
    discard a real position rather than resolve it; naming a reachable node is the way out. The one chunk that legally
    resolves to an entry node is one that has **not moved at all** — it stands on nowhere, and the entry of whichever
    graph it lands on is where it would have started.
  - **A target graph that is unknown, retired, or the chunk's own current pin.** The last of those is the plain
    same-graph restart, asked for with a redundant flag rather than a move to make.
- **Two conditions suppress it, and neither refuses it.** A chunk **pause** outranks it: the chunk stays parked and the
  move is honored on the tick after the pause lifts. An open **takeover** defers it indefinitely — the person is inside
  that session, and killing it out from under them is worse than leaving the move pending. The hub holds no takeover
  state to refuse the request with, so deferral at the runner is the whole mechanism, and the chunk reads as moved while
  the human works on at the stale epoch ([humans.md](../humans.md) §Takeover).
