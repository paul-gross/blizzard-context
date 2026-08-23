# Takeover

A person may enter a held chunk's session interactively; the entry and exit are recorded facts. Spoke of the
[human-entry hub](../humans.md). Ordinarily the chunk is already parked `needs_human` and there is no live attempt to
displace. A **forced** entry into a chunk still being worked is allowed too: it kills the live worker and fences that
attempt's epoch, so the displaced worker's late submission bounces (`bzh:epoch-fencing` in
[execution.md](../execution.md)) — and, since nothing failed and nothing was invited, the chunk keeps deriving `running`
rather than becoming `needs_human`. It is refused, rather than forced, when that attempt has already submitted its
outcome: a fence minted behind a queued submission would never take effect.

- **Entering through the wrapped takeover verb, when the escalation carries one ([escalation.md](./escalation.md)),
  records the takeover fact with the daemon before it resumes anything** — so no loop step can respawn or judge the held
  session while a person holds it. That same fact is also what lets the resumed session's own verbs (`attach`, `ask`,
  `artifact …`) reach the runner: it authorizes them against the reference lease it names, active or already closed,
  rather than minting or reopening a lease of its own.
- **No attempt runs during a takeover** — the chunk keeps whatever condition it was in, with human-in-session detail,
  until it is explicitly requeued or the chunk itself ends. An operator's restart
  ([work/restart.md](../work/restart.md)) is the one move that can be *recorded* against a chunk in this state, and it
  deliberately does not take effect: the hub keeps no takeover state to refuse it with, so the runner holding the
  session defers the teardown instead — indefinitely, while the person works on at the now-stale epoch. Ending the
  takeover is what lets the move land.
- **Hand-back is ordinarily explicit**: the person requeues the chunk. The one exception is the chunk ending — stopped
  or done — while a takeover is still open: nothing infers a *person* is done, but the hub's own terminal fact closes
  the takeover fact regardless, the same shape an escalation's own hub-ends-it closer ([escalation.md](./escalation.md))
  already uses.
