# Recovery

What happens when a lease expires, an attempt is exhausted, or a chunk must change runner. Spoke of the
[execution hub](../execution.md).

## Reap

Reap expires a lease with no live work behind it: one minted but never spawned, or one whose worker is alive but no
longer beating. It ends the attempt — retry, or escalation on exhaustion
([../humans/escalation.md](../humans/escalation.md)) — never by itself the chunk's tenure or environments.

A worker that has exited is never reaped: its exit is its done declaration, and judging it belongs to the step that
advances the chunk. Even an error-during-execution exit is never reaped: the runner never observes exit status, so
nothing exists to branch on — the backstop is the node's declared `produces:` plus the empty-delivery refusal at
delivery time, catching what the errored exit failed to produce regardless of exit status.

An exit the harness's own provider itself reports as overloaded is neither reaped nor judged: it resumes the same
session in place after a bounded, growing wait, spending no retry — until a bounded streak of consecutive overloads on
the one lease is reached, at which point it falls through to an ordinary judged exit.

## Requeue

Requeue names two operations. The hub's supersedes the escalation and releases the route. A chunk requeued at a runner
node returns to the queue for the next claimant; one requeued at a hub-executed node is taken again by the hub's flow
driver. The hub's requeue records who requeued, and may carry their note
([../humans/asks.md#a-persons-note](../humans/asks.md#a-persons-note)). The holding runner's own — the hand-back after a
takeover ([../humans/takeover.md](../humans/takeover.md)) — keeps route, environments, and tenure, re-attempting the
current node in place against its existing retry budget, and carries no note. The runner refuses its own requeue of a
chunk that holds no environment there, since nothing on that runner could re-attempt it — that chunk is requeued at the
hub instead — and a requeue asked while one is already pending changes nothing.

## Detach

Detach is an operator's forcible release of a chunk from its runner: it releases the route and supersedes nothing, so
the chunk re-derives on its remaining facts — ready only when nothing else holds it — and the next claim's reserved
epoch fences the old runner out. Detach stays legal at `delivering` — the operator's forcible lever, as a forced
retirement is ([./retirement.md](./retirement.md)) — and is refused on a terminal chunk whose route is only its
finisher's leftover, which holds no claim to release.

Detach **ends** the chunk rather than parking it: the worker is killed and the session is discarded, not resumable — the
inverse of a per-chunk pause's park, which keeps the same session for a later resume ([./pause.md](./pause.md)).

## Release

Release is the holding runner's own giving back of a running chunk mid-graph, so that another runner — or the same one,
later — claims it from the queue. Tenure goes back as with detach: the route is freed, nothing is superseded, and no
epoch is bumped, so the chunk re-derives `ready` at its current node and the next claim's reserved epoch fences the old
holder out; the next holder enters the node cold, in fresh environments, and no retry is spent.

Release has four refusals, and each guards only who holds the chunk at which epoch: the caller does not hold the chunk's
route, the chunk is not `running`, the chunk has moved past the epoch the caller last saw, or the chunk is not the
tenant's. None judges whether letting go is wise — that is the caller's judgement, made on its own runner before it
asks. Each caller brings a reason, an open string the hub records and never interprets, so a new caller needs no change
to the release itself.

## Reassignment

Reassignment moves a held chunk to another runner — the supported exception to stickiness. A new environment can be
rebuilt for the new holder. Work not yet pushed as a commit does not survive the move.
