# Retirement

What an operator's retirement of a runner stops, what it keeps, and how it is reversed. Spoke of the
[execution hub](../execution.md).

Retirement is a recorded, reversible fact about a runner, never a deletion: the registration and every fact attributed
to the runner survive, so historical views keep naming it. It is independent of the runner brakes in
[pause.md](./pause.md). Retiring a host retires every runner under it this way ([hosts.md](./hosts.md)).

## What retirement stops

A retired runner's credential is dead, it is hidden from the default fleet views, and the hub refuses its registration,
its contact, and its claims outright, keyed on its id. A claim refusal reuses the paused-claim denial shape, so an older
runner reads it as one.

Human federation through the retired runner's IdP client stops too. Once the redirect URI matches one the runner
registered, the hub refuses the retired runner distinctly; an unknown client or an unregistered redirect URI keeps the
one undifferentiated refusal, so the retired case is told apart only by a caller who already knows a registered URI.

## Holdings

A runner holding chunks cannot be retired plainly: the hub refuses, naming each held chunk and its environments. A
forced retirement records the fact first, so new claims are refused from that instant, and then releases every route the
runner still holds through the same release detach uses; each chunk re-derives `ready`. Repeating the retirement
finishes any release that was interrupted, and releases a claim that slipped in after the holdings check.

A retirement acts only on itself. Once the runner is reinstated, a retirement still under way, or one repeated by an
operator who saw the runner before the reinstatement, is refused: it revokes no token the runner was enrolled with since
and releases no chunk it claimed since, and repeating it decides again on the runner as it now stands.

A chunk at a terminal status is no holding, whatever route it still carries: it neither refuses a plain retirement nor
is released by a forced one, which leaves it untouched.

A retired runner process that is still running is refused by the hub, so it never observes the release; its local
worktrees stay held until the process is stopped.

## Reinstatement

Reinstatement finishes the retirement it reverses, then records the reversal: a chunk the retirement left held — one a
retirement stopped before its releases left behind — is released first, as the retirement would have, and re-derives
`ready`. A reinstatement decided on a retirement since reversed or repeated is refused. The runner is unenrolled —
reinstating revokes any token it still carries, in the same step as the reversal — and must be enrolled afresh;
enrolling a retired runner is refused, so there is one lever back. A runner still under a retired host is refused
reinstatement; released from that host, it can be reinstated, and stands alone ([./hosts.md](./hosts.md)).

## Token revocation

An operator can revoke a runner's token without retiring it: the runner stays added and unenrolled until enrolled
afresh. Every revoked token stays refused for good, even after re-enrollment. Re-enrolling an enrolled runner rotates
its token the same way: the token it replaces is recorded revoked, the one minted when the runner was added included, so
a rotated-out token is refused too; two rotations at once still leave every replaced token revoked. A retired runner
still carrying a token — an enrollment that raced its retirement — can have that token revoked the same way; a runner
holding no token has nothing to revoke. A revocation decided on a runner since retired or reinstated is refused, and
revokes nothing; so is an enrollment decided on a runner since retired or reinstated, which mints and revokes nothing.
Enrolling afresh after reinstatement stays legal.
