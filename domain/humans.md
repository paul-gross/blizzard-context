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
| Escalation | The system, on exhausted failure | `needs_human` | Supersession — requeue makes the chunk leasable again; there is no resolution fact |
| Takeover | A person, entering a parked session | Stays `needs_human`, with human-in-session detail | Explicit hand-back — requeue |

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

A chunk parks `needs_human` when the system runs out of moves — a **runner** escalates when a worker's retries are exhausted or it dies without a verdict past the retry cap; the **hub** itself escalates when a migrating choice's target graph fails to resolve, or when a node's bounce cap is crossed.

- **A present wrapped takeover verb always means the raw resume command is present too, but not the other way around** — a present raw command does not mean the wrapped verb is, and either or both can be empty. The wrapped verb is present only when the escalation was composed by a **runner** that held a resumable session for the parked lease, had already committed to the environment(s) it was working in, and knew its own location to point the command back at.
- **There are three genuinely distinct ways the wrapped verb can be missing** (and, in two of them, the raw command too):
  - **Cross-graph-unresolvable** — the hub declines a migrating choice whose target graph doesn't resolve. No wrapped verb (the hub has no runner runtime to compose one from), and the raw field holds operator guidance instead of a runnable command — which graph to mint before requeuing, not how to resume a session. The session behind it is real, though: the escalation follows directly from a worker's own live submission, so the parked session is still reachable through the ordinary takeover fallback — the escalation's own fields just don't advertise it.
  - **Runner-composed, own location unconfigured** — the runner held a resumable session and had committed to its environment(s), but had nowhere to point the wrapped command at. The raw command composes normally; the wrapped one stays empty.
  - **No session-bearing lease at all** — a **bounce-cap** escalation (the hub's own node-level retry accounting; never a worker's session) and a runner escalating before any session was ever parked both land here. Both fields are empty, and there is nothing for a takeover to enter.
- Beside either command, the escalation carries the parked session's own identity — which declared session it belonged to, and the model and effort it actually ran under — read back from what the session ran, never re-derived, so the operator lands in the configuration the fleet was using rather than whichever one a fresh resolution would produce now. A session that predates the record simply carries none of them, and the command stays bare rather than guessing.
- A present wrapped verb is the supported entry point (§Takeover below).
- It **closes by supersession, never resolution**: requeueing makes the chunk leasable again, and the next attempt's lease is what closes the escalation — there is no "resolved" fact to write.
- An open escalation also **appears as one `needs-human` event** in the unified operational event log ([operations.md](./operations.md)), projected at read time — its own fact and supersession rule are unchanged; the log just gives `needs_human` one home alongside the other operational events rather than a separate surface.

## Takeover

A person may enter a parked chunk's session interactively; the entry and exit are recorded facts.

- **Entering through the wrapped takeover verb, when the escalation carries one (§Escalation above), records the takeover fact with the daemon before it resumes anything** — so no loop step can respawn or judge the held session while a person holds it.
- **No lease exists during a takeover** — the chunk stays `needs_human`, with human-in-session detail, until it is explicitly requeued.
- **Hand-back is explicit**: the person requeues the chunk; nothing infers that a human is done.

## See also

- [./work.md](./work.md) — the statuses these entries derive and the transition a resolved decision becomes.
- [./execution.md](./execution.md) — the lease kept dormant while a chunk parks, and the reap clock these entries stop.
