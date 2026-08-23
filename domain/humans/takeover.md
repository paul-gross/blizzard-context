# Takeover

A takeover is a person entering a held chunk's session interactively; the entry and exit are recorded facts. Spoke of
the human-entry hub, [../humans.md](../humans.md).

Ordinarily the chunk is already parked `needs_human`, so no live attempt is displaced.

## Entering

Entering through the wrapped verb ([./escalation.md](./escalation.md)) records the takeover fact with the daemon before
anything resumes, so no loop step can respawn or judge the held session while a person holds it. The same fact
authorizes the resumed session's verbs — `attach`, `ask`, `artifact …` — against the reference lease it names, active or
closed, without minting or reopening one.

## Forced entry

A forced entry into a still-worked chunk kills the live worker and fences the attempt's epoch, so the displaced worker's
late submission bounces (`bzh:epoch-fencing`, [../execution.md](../execution.md)). After a forced entry the chunk keeps
deriving `running`, not `needs_human` — nothing failed and nothing was invited. Forced entry is refused once the attempt
has already submitted its outcome: a fence minted behind a queued submission would never take effect.

## While a person holds the session

No attempt runs during a takeover: the chunk keeps its condition plus human-in-session detail until explicitly requeued
or ended. An operator's restart ([../work/restart.md](../work/restart.md)) can be recorded against a taken-over chunk
yet deliberately takes no effect — the hub keeps no takeover state to refuse it, so the holding runner defers the
teardown indefinitely while the person works at the now-stale epoch; ending the takeover lets the move land.

## Ending

Hand-back is ordinarily explicit: the person requeues the chunk. A chunk ending — stopped or done — while a takeover is
open closes the takeover fact through the hub's own terminal fact, though nothing infers a person is done.
