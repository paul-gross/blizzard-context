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

Requeue names two operations. The hub's supersedes the escalation and releases the route, returning the chunk to the
queue for the next claimant. The holding runner's own — the hand-back after a takeover
([../humans/takeover.md](../humans/takeover.md)) — keeps route, environments, and tenure, re-attempting the current node
in place against its existing retry budget.

## Detach

Detach is an operator's forcible release of a chunk from its runner: it releases the route and supersedes nothing, so
the chunk re-derives on its remaining facts — ready only when nothing else holds it — and the next claim's epoch floor
fences the old runner out.

Detach **ends** the chunk rather than parking it: the worker is killed and the session is discarded, not resumable — the
inverse of a per-chunk pause's park, which keeps the same session for a later resume ([./pause.md](./pause.md)). A
pinning test for the worker-killed half of this is
`blizzard/tests/test_runner_detach.py::test_pull_abandons_a_live_detached_chunk`.

## Reassignment

Reassignment moves a held chunk to another runner — the supported exception to stickiness. A new environment can be
rebuilt for the new holder. Work not yet pushed as a commit does not survive the move.
