# Humans in the loop (`bzh:human-entries`)

Where people enter blizzard's loop, and the two parked conditions they produce.
Definitional — a taxonomy of the human entry points (`canon:rule-shape` §File kinds).
Part of the [domain model](./index.md).

The default posture is human-**on**-the-loop: the default graph has no human touchpoints — agents verify and merge to main.
Every human entry is either **opt-in** (asks, gates) or **exceptional** (escalation, takeover); adding and removing gates is the dial between reviewing every step and supervising outcomes.

| Entry | Who initiates | Parks the chunk as | Resolved by |
|-------|---------------|--------------------|-------------|
| Ask | The worker, mid-step | `waiting_on_human` | The first answer; the session resumes around it |
| Gate decision | The workflow (a human-judged node) or runner configuration | `waiting_on_human` | A person picking one of the choices; the resolving transition follows |
| Escalation | The system, on exhausted failure | `needs_human` | Supersession — a requeue makes the chunk leasable again, or the chunk ends; there is no resolution fact |
| Takeover | A person, entering a held session | Nothing of its own — the chunk keeps the condition it was already in, plus human-in-session detail | Explicit hand-back — requeue — or the chunk ending while still held |

The two parked conditions differ by cause: `waiting_on_human` is **invited** input — the model expects a person and stops the reap clock; `needs_human` is **failure** — the system ran out of moves and a person must act.
Both derive from open facts, never stored flags ([work.md](./work.md) §Statuses).

## Ask and answer

A worker that needs input asks a durable question — free-form, or with options a board or bot renders as buttons — and the chunk parks.

- **The reap clock stops** while the question is open: a chunk waiting on a person is not stalled.
- **Exactly one answer ever exists.** The first answer wins; later would-be answerers are told who won and what they said.
- **The session resumes around the answer** — the dormant agent session continues with the answer delivered into it, and the resume restarts the reap clock.
- **The delivery is itself a fact, and the question carries it.** Answered and delivered are distinct derived states: answered says a person decided, delivered says the resume actually ran and the agent heard. A question row surfaces both, so the return trip is visible to whoever answered rather than inferred from the chunk moving.

## Gate decision

A **decision** is a gate's parking row: a durable multiple-choice ask written where a worker-judged node would have written its transition, carrying the step's artifacts so the deciding human sees what they are judging.

- **The choices are the node's judgement choices** ([graphs.md](./graphs.md)) — what the board and chat bot render as buttons.
- **Pending derives**: a decision no resolving fact references is open, and the chunk derives `waiting_on_human` from it — no live lease while parked. The resolving fact is normally the transition the holding runner writes (below); when the resolved choice migrates cross-graph it is the migration record instead — or, if that migration's target is unresolvable, the escalation — since a migration writes no transition ([work.md](./work.md) §Migration).
- **Resolution is recorded once** — first write wins, like an answer — and the holding runner then writes the ordinary transition referencing the decision: the runner still advances the chunk.
- **Gates arrive two ways**: structurally, as a human-judged node in the graph; or by **runner configuration** selecting node names — human sign-off added to an existing workflow without editing any graph. At a human-judged node a runner-submitted transition is rejected; human sign-off cannot be bypassed.

## Escalation

A chunk parks `needs_human` when the system runs out of moves — a **runner** escalates when a worker's retries are exhausted, it dies without a verdict past the retry cap, or its spend cap is reached; the **hub** itself escalates when a migrating choice's target graph fails to resolve, or when a node's bounce cap is crossed.

- **A present wrapped takeover verb always means the raw resume command is present too, but not the other way around** — an escalation can carry the raw command without the wrapped verb, and either or both can be missing. The wrapped verb is present only when the escalation was composed by a **runner** that held a resumable session for the parked lease and had already committed to the environment(s) it was working in. (The runner must also know its own location to point the command back at, but that is structurally guaranteed for any runner new enough to compose the verb — its config loader always resolves the runtime dir — so the code's guard on it is defensive, never a distinct reason the verb goes missing.)
- **Whether a takeover is actually possible is a separate question from whether the escalation carries a composed command.** Entering a session ([§Takeover](#takeover) below) checks the real thing directly — does a runner still hold this chunk, with a session behind its most recent lease — never what the escalation itself carries. An escalation carrying neither command can still be takeable on that basis; carrying nothing only means nothing was composed for display.
- **There are four genuinely distinct reasons the wrapped verb can be missing:**
  - **Hub-authored** — the hub itself escalates (cross-graph-unresolvable, or a node's bounce cap crossed); it has no runner runtime to compose a wrapped command from, so the wrapped verb is always missing here. A cross-graph-unresolvable escalation reached through a worker's own live transition carries operator guidance in place of the raw command instead — which graph to mint before requeuing, not how to resume a session — and the session behind it is real, reachable through the ordinary takeover check above. Reached instead through a human gate's resolved choice, no worker ran ([§Gate decision](#gate-decision) above) and no such guarantee holds. A bounce-cap escalation carries neither command, but — unlike cross-graph-unresolvable — never releases the runner's hold on the chunk, so whatever session already existed carries over unchanged; whether a takeover is possible is decided by that prior state, not by this escalation.
  - **No session was ever parked** — the runner escalates before spawning a worker session at all (retries exhausted, or it died with no session ever recorded). The escalation carries neither command, and there is genuinely nothing for a takeover to enter.
  - **Its environments were released while its session survived** — an escalation composed after the chunk's environments were handed back. Both commands are composed from a held workdir, so neither exists here while a real session still stands behind the lease: unlike *no session was ever parked* above, there **is** something for a takeover to enter, and the ordinary check — not what this escalation carries — decides whether entering it succeeds.
  - **Stored history** — the escalation row predates the wrapped verb: written by an older runner, or already open when the wrapped verb arrived (the hub deploys continuously while runners redeploy by hand, so this skew window is real and an open escalation persists until superseded). Such a row reads the wrapped verb back empty while its raw command is a genuinely runnable resume string; the board falls back to rendering that raw command as the primary copyable command.
- Beside either command, the escalation carries the parked session's own identity — which declared session it belonged to, and the model and effort it actually ran under — read back from what the session ran, never re-derived, so the operator lands in the configuration the fleet was using rather than whichever one a fresh resolution would produce now. A session that predates the record simply carries none of them, and the command stays bare rather than guessing.
- A present wrapped verb is the supported entry point (§Takeover below).
- It **closes by supersession, never resolution** — there is no "resolved" fact to write. Two things supersede one. Requeueing makes the chunk leasable again, and the next attempt's lease closes it. **The chunk ending** also closes it — stopped or done: a human who finished the work outside the fleet and abandoned the chunk has resolved the hold, and a chunk requeued away and landed by another runner has had it resolved for them. Neither is ever followed by a lease mint on the escalating runner, so without this arm the escalation would stand forever. A runner that raised the escalation learns the stop on its next reconciliation and mirrors it locally, so its own list and panel drop the chunk too — meaning the runner-side close lags the hub's by a tick, and by a redeploy on a runner too old to sweep.
- An open escalation also **appears as one `needs-human` event** in the unified operational event log ([operations.md](./operations.md)), projected at read time — its own fact and supersession rule are unchanged; the log just gives `needs_human` one home alongside the other operational events rather than a separate surface.

## Takeover

A person may enter a held chunk's session interactively; the entry and exit are recorded facts.
Ordinarily the chunk is already parked `needs_human` and there is no live attempt to displace.
A **forced** entry into a chunk still being worked is allowed too: it kills the live worker and fences that attempt's epoch, so the displaced worker's late submission bounces (`bzh:epoch-fencing` in [execution.md](./execution.md)) — and, since nothing failed and nothing was invited, the chunk keeps deriving `running` rather than becoming `needs_human`.
It is refused, rather than forced, when that attempt has already submitted its outcome: a fence minted behind a queued submission would never take effect.

- **Entering through the wrapped takeover verb, when the escalation carries one (§Escalation above), records the takeover fact with the daemon before it resumes anything** — so no loop step can respawn or judge the held session while a person holds it. That same fact is also what lets the resumed session's own verbs (`attach`, `ask`, `artifact …`) reach the runner: it authorizes them against the reference lease it names, active or already closed, rather than minting or reopening a lease of its own.
- **No attempt runs during a takeover** — the chunk keeps whatever condition it was in, with human-in-session detail, until it is explicitly requeued or the chunk itself ends.
- **Hand-back is ordinarily explicit**: the person requeues the chunk. The one exception is the chunk ending — stopped or done — while a takeover is still open: nothing infers a *person* is done, but the hub's own terminal fact closes the takeover fact regardless, the same shape an escalation's own hub-ends-it closer (§Escalation above) already uses.

## See also

- [./work.md](./work.md) — the statuses these entries derive and the transition a resolved decision becomes.
- [./execution.md](./execution.md) — the lease kept dormant while a chunk parks, and the reap clock these entries stop.
