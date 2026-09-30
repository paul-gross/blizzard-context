# Retirement

What an operator's retirement of a runner stops, what it keeps, and how it is reversed. Spoke of the
[execution hub](../execution.md).

Retirement is a recorded, reversible fact about a runner, never a deletion: the registration and every fact attributed
to the runner survive, so historical views keep naming it. It is independent of the runner brakes in
[pause.md](./pause.md).

## What retirement stops

A retired runner's credential is dead, it is hidden from the default fleet views, and the hub refuses its registration,
its contact, and its claims outright, keyed on its id — so a caller with no token is refused as well. The refusal holds
under every runner-auth mode. A claim refusal reuses the paused-claim denial shape, so an older runner reads it as one.

## Holdings

A runner holding chunks cannot be retired plainly: the hub refuses, naming each held chunk and its environments. A
forced retirement records the fact first, so new claims are refused from that instant, and then releases every route the
runner still holds through the same release detach uses; each chunk re-derives `ready`. Repeating the retirement
finishes any release that was interrupted, and releases a claim that slipped in after the holdings check.

A chunk at a terminal status is no holding, whatever route it still carries: it neither refuses a plain retirement nor
is released by a forced one, which leaves it untouched.

A retired runner process that is still running is refused by the hub, so it never observes the release; its local
worktrees stay held until the process is stopped.

## Reinstatement

Reinstatement records the reversal and nothing more. The runner is unenrolled — its token was revoked when it was
retired — and must be enrolled afresh; enrolling a retired runner is refused, so there is one lever back.

## Token revocation

An operator can revoke a runner's token without retiring it: the runner stays registered and unenrolled until enrolled
afresh. Every revoked token stays refused for good, even after re-enrollment, and is refused under every runner-auth
mode rather than merely failing to resolve.
