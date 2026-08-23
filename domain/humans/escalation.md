# Escalation

A chunk parks `needs_human` when the system runs out of moves; the escalation stands until something supersedes it.
Spoke of the human-entry hub, [../humans.md](../humans.md).

## What raises an escalation

A runner escalates when a worker's retries are exhausted, when it dies without a verdict past the retry cap, or when its
spend cap is reached. The hub itself escalates when a migrating choice's target graph fails to resolve, or when a node's
bounce cap is crossed.

## The commands an escalation carries

A present wrapped takeover verb guarantees the raw resume command is present as well; the converse does not hold — the
raw command can appear alone, and either or both can be missing. The wrapped verb exists only when a runner composed the
escalation while holding a resumable session for the parked lease and still committed to its working environment(s). A
hub-authored escalation always lacks the wrapped verb: the hub has no runner runtime to compose one from. Composing the
wrapped verb also needs the runner's own location, but any runner new enough to compose it always knows that, so
location is never a distinct reason the verb is missing.

A stored-history escalation predates the wrapped verb — written by an older runner, or already open when the verb
arrived; the hub deploys continuously while runners redeploy by hand, so this skew is real and an open escalation
persists until superseded. Such a row reads the wrapped verb back empty while its raw command is a genuinely runnable
resume string; the board then renders the raw command as the primary copyable command.

## The parked session's identity

Beside either command the escalation carries the parked session's identity — its declared session and the model and
effort it actually ran under — read back from what ran, never re-derived, so the operator lands in the configuration the
fleet was using. A session predating that identity record carries none of it, and the command stays bare rather than
guessing.

## What each origin carries

- **Escalated before any worker session existed** — retries exhausted, or death with no session recorded: the escalation
  carries neither command and there is nothing for a takeover to enter.
- **Environments released while the session survived** — neither command exists, both being composed from a held
  workdir, yet a real session still stands behind the lease: unlike the no-session case, there is something for a
  takeover to enter.
- **Bounce cap crossed** — the escalation carries neither command but never releases the runner's hold on the chunk, so
  any existing session carries over unchanged, and that prior state, not the escalation, decides whether takeover is
  possible.
- **Cross-graph target unresolvable** — reached through a worker's own live transition, the escalation carries operator
  guidance in place of the raw command — which graph to mint before requeuing, not how to resume — and the session
  behind it is real and reachable through the ordinary takeover check; reached instead through a human gate's resolved
  choice, no worker ran ([./gates.md](./gates.md)), so no such session guarantee holds.

## Whether a takeover can enter

A present wrapped verb is the supported takeover entry point ([./takeover.md](./takeover.md)). But whether takeover is
possible is independent of what commands the escalation carries: entering a session checks directly whether a runner
still holds the chunk with a session behind its most recent lease, never the escalation's contents — an escalation
carrying nothing can still be takeable.

## Supersession

An escalation closes by supersession, never resolution — no resolved fact exists to write. What supersedes one:

- a requeue making the chunk leasable again;
- the next attempt's lease minted on the chunk;
- an operator's restart ([../work/restart.md](../work/restart.md)) handing the work back at its own fresh epoch;
- the chunk ending, stopped or done.

The chunk-ending arm exists because an ended chunk never mints another lease on the escalating runner — without it such
escalations would stand forever. The runner-side close lags the hub's: the escalating runner learns of the supersession
on its next reconciliation — after a redeploy, if it is too old to sweep — and only then drops the chunk from its own
list and panel.

## Projection into the operational event log

An open escalation also appears as one `needs-human` event in the unified operational event log
([../operations.md](../operations.md)), projected at read time.
