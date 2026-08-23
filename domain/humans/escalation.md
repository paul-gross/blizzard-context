# Escalation

A chunk parks `needs_human` when the system runs out of moves, and stands until something supersedes it. Spoke of the
[human-entry hub](../humans.md). A **runner** escalates when a worker's retries are exhausted, it dies without a verdict
past the retry cap, or its spend cap is reached; the **hub** itself escalates when a migrating choice's target graph
fails to resolve, or when a node's bounce cap is crossed.

- **A present wrapped takeover verb always means the raw resume command is present too, but not the other way around** —
  an escalation can carry the raw command without the wrapped verb, and either or both can be missing. The wrapped verb
  is present only when the escalation was composed by a **runner** that held a resumable session for the parked lease
  and had already committed to the environment(s) it was working in. (The runner must also know its own location to
  point the command back at, but that is structurally guaranteed for any runner new enough to compose the verb — its
  config loader always resolves the runtime dir — so the code's guard on it is defensive, never a distinct reason the
  verb goes missing.)
- **Whether a takeover is actually possible is a separate question from whether the escalation carries a composed
  command.** Entering a session ([takeover.md](./takeover.md)) checks the real thing directly — does a runner still hold
  this chunk, with a session behind its most recent lease — never what the escalation itself carries. An escalation
  carrying neither command can still be takeable on that basis; carrying nothing only means nothing was composed for
  display.
- **The genuinely distinct reasons the wrapped verb can be missing:**
  - **Hub-authored** — the hub itself escalates (cross-graph-unresolvable, or a node's bounce cap crossed); it has no
    runner runtime to compose a wrapped command from, so the wrapped verb is always missing here. A
    cross-graph-unresolvable escalation reached through a worker's own live transition carries operator guidance in
    place of the raw command instead — which graph to mint before requeuing, not how to resume a session — and the
    session behind it is real, reachable through the ordinary takeover check above. Reached instead through a human
    gate's resolved choice, no worker ran ([gates.md](./gates.md)) and no such guarantee holds. A bounce-cap escalation
    carries neither command, but — unlike cross-graph-unresolvable — never releases the runner's hold on the chunk, so
    whatever session already existed carries over unchanged; whether a takeover is possible is decided by that prior
    state, not by this escalation.
  - **No session was ever parked** — the runner escalates before spawning a worker session at all (retries exhausted, or
    it died with no session ever recorded). The escalation carries neither command, and there is genuinely nothing for a
    takeover to enter.
  - **Its environments were released while its session survived** — an escalation composed after the chunk's
    environments were handed back. Both commands are composed from a held workdir, so neither exists here while a real
    session still stands behind the lease: unlike *no session was ever parked* above, there **is** something for a
    takeover to enter, and the ordinary check — not what this escalation carries — decides whether entering it succeeds.
  - **Stored history** — the escalation row predates the wrapped verb: written by an older runner, or already open when
    the wrapped verb arrived (the hub deploys continuously while runners redeploy by hand, so this skew window is real
    and an open escalation persists until superseded). Such a row reads the wrapped verb back empty while its raw
    command is a genuinely runnable resume string; the board falls back to rendering that raw command as the primary
    copyable command.
- Beside either command, the escalation carries the parked session's own identity — which declared session it belonged
  to, and the model and effort it actually ran under — read back from what the session ran, never re-derived, so the
  operator lands in the configuration the fleet was using rather than whichever one a fresh resolution would produce
  now. A session that predates the record simply carries none of them, and the command stays bare rather than guessing.
- A present wrapped verb is the supported entry point ([takeover.md](./takeover.md)).
- It **closes by supersession, never resolution** — there is no "resolved" fact to write. What supersedes one:
  - **A requeue**, which makes the chunk leasable again.
  - **The next attempt's lease**, whenever one is minted on that chunk.
  - **An operator's restart** ([work/restart.md](../work/restart.md)), which hands the work back the same way at its own
    fresh epoch.
  - **The chunk ending** — stopped or done: a human who finished the work outside the fleet and abandoned the chunk has
    resolved the hold, and a chunk requeued away and landed by another runner has had it resolved for them. Neither is
    ever followed by a lease mint on the escalating runner, so without this arm the escalation would stand forever.
- **The runner-side close lags the hub's**, by a tick and by a redeploy on a runner too old to sweep: the runner that
  raised the escalation learns of the supersession on its next reconciliation and only then drops the chunk from its own
  list and panel.
- An open escalation also **appears as one `needs-human` event** in the unified operational event log
  ([operations.md](../operations.md)), projected at read time — its own fact and supersession rule are unchanged; the
  log just gives `needs_human` one home alongside the other operational events rather than a separate surface.
