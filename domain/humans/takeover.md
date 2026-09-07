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
late submission bounces (`bzh:epoch-fencing`, [../execution/fencing.md](../execution/fencing.md)). After a forced entry
the chunk keeps deriving `running`, not `needs_human` — nothing failed and nothing was invited. Forced entry is refused
once the attempt has already submitted its outcome: a fence minted behind a queued submission would never take effect.

## While a person holds the session

No attempt runs during a takeover while the runner still holds the session's lease — which is why a forced entry leaves
the displaced worker's lease open rather than closing it. Where the escalation already closed the lease, on the ordinary
parked entry, the guarantee lasts exactly as long as the park: supersede that park at the hub and the held workdir goes
to a fresh attempt. The takeover contributes no condition of its own: the chunk goes on deriving from its own facts, and
carries human-in-session detail exactly while the takeover is open.

An operator's restart ([../work/restart.md](../work/restart.md)) recorded against a taken-over chunk lands in full — the
hub keeps no takeover state to refuse it — and supersedes any park with it. Against a still-open lease the runner defers
the teardown indefinitely while the person works at the now-stale epoch, and ending the takeover lets the re-entry
follow; against a lease the escalation already closed, nothing defers it.

## Ending

A takeover ends when the person leaves the interactive session. A chunk ending — stopped or done — while a takeover is
open closes the takeover fact through the hub's own terminal fact, though nothing infers a person is done.

Hand-back is a separate step, and explicit: the person requeues the chunk through the runner holding it
([../execution/recovery.md](../execution/recovery.md)), clearing the `needs_human` hold — a forced entry, which parks
nothing, has no such hand-back: the verb refuses a chunk that is not `needs_human`. The order is fixed: the holding
runner's requeue is refused while a takeover is open, so the session ends first and the hand-back follows. The hub's
requeue carries no such refusal, and supersedes the park; neither requeue is ever what ends a takeover.
