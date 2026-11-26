# Throttling

What holds a runner back from starting work without anyone braking it, and what lets it go again. Spoke of the
[execution hub](../execution.md).

Before each tick's claims, and before every step or continuation of a parked session, a runner asks its gate whether to
start, and the gate answers from readings, never from a flag anyone set. A reading that turns restrictive stops further
claims from the next tick, while every step, a claimed chunk's first included, still asks before it starts. The breakers
answer first: a runner's brakes ([./pause.md](./pause.md)) refuse outright, and only past them is a throttle asked. A
throttle declines rather than refuses, and lifts of itself once its reading changes. The throttles, asked in this order
— the floor, then each the operator configures:

- The subscription floor.
- A pace against a window's elapsed share: the window the operator names, or with none named the longest one the sample
  reports.
- A utilization line.
- A budget of spend over a trailing window against a dollar ceiling.
- A schedule.

A continuation of a step already begun answers to the floor alone. An escalation asks the breakers alone.

## An exhausted subscription holds back every runner spending it (`bzh:subscription-floor-reach`)

A subscription's exhaustion holds back every runner of the host spending it and no other — a runner on another
subscription, or on none, is not held back by it — and lifts for all of them together when it clears. No runner's brake
is engaged by it, and nothing a person does is needed to lift it, though a person may. The limit belongs to the plan and
carries its own expiry: every runner spending it would meet it on its next start, a runner paid from another plan has no
reason to stop, and a fact that expires should not wait for someone to clear it.

## What holds the floor, and when each hold lifts

Two facts hold a subscription's floor, and each lifts on its own terms:

- A usage-limit mark: a harness met the plan's limit part-way through a step. When the mark lifts, the held-back runners
  claim again and the lease that met the limit wakes.
- An exhausted window: the newest sample shows one of the plan's windows at 100 percent, whether or not any harness has
  met the limit.

A runner spending no subscription has a floor of its own, held only by its own mark.

A mark's expected reset is the one its harness named. A mark naming none takes the soonest pending reset among the
windows the newest sample shows exhausted, when that sample was taken at or after the mark; with no such sample it
expects its reset 30 minutes after it was made.

Whether a sample can confirm the plan open decides how a mark lifts. A mark on a sampled subscription, expecting a reset
its harness named or a sample supplied, lifts on the first of these:

- A sample shows the window the limit was met in turned over into a later period and under 100 percent, whether or not
  the expected reset has come. A sample under 100 percent in the period the limit was met in lifts nothing, and a mark
  naming no window is never lifted ahead of its reset.
- The expected reset has passed, and a sample taken since shows every window in a period still running. A window that
  sample shows exhausted in its new period then holds as an exhausted window, under its own reset.
- An hour past the expected reset, when no sample has lifted it by either of the above. A sample still reporting the
  passed period is no evidence either way: it does not lift the mark sooner, and it does not hold it past the hour.

A mark no sample can confirm lifts at its expected reset, on the clock alone and with no further hour: one on a
subscription the host does not sample, one on a runner spending no subscription, and one expecting its reset on the
30-minute fallback.

An exhausted window holds until a newer sample shows it under 100 percent — in the same period or a later one: with no
harness having met a limit, the newest reading is all there is to go on — and otherwise until an hour past the window's
reset: a sample still reporting the passed period does not hold it past that hour. It stands apart from any mark: a mark
lifting on the clock leaves a window the newest sample shows exhausted holding still.

An operator may clear a hold; a cleared hold holds a runner back again only on a mark or a newly exhausted window after
the clear. The clear names what the floor belongs to: a subscription's floor is cleared by naming the subscription, and
a clear naming a runner that spends one is refused, so nobody lifts a whole plan believing they lifted one machine. A
runner spending none has its own floor cleared by naming the runner.

## Sampling ahead of the cadence

Two things ask the host to sample a subscription it samples without waiting out its cadence:

- A fresh mark, so the reported usage catches up with what a harness just found.
- A standing hold whose expected reset has passed with no sampling attempt since, so the floor is confirmed open.

Each asks once: the request stands only until a sampling attempt newer than the mark, or newer than the passed reset, is
made. An attempt counts whether or not it yielded a sample, so a failed attempt satisfies the request and sampling falls
back to its cadence, never retrying every tick.

## Holding or giving back a chunk the gate holds back

A runner holding a chunk its gate holds back keeps the claim and waits. Two settings, independent and each defaulting to
hold, have it give the claim back to the queue; [./recovery.md](./recovery.md) §Release owns what that release is and
what it leaves behind.

- On a decline: the gate declined the chunk's next step — the floor, or a throttle the operator configures. A brake or
  the chunk's own pause is no decline, and releases nothing.
- On a usage limit: a usage limit parked the chunk's step part-way, and the floor still declines its continuation. A
  chunk waiting on a person — paused by an operator, or parked on an open ask — is never given back, and a parked step
  whose floor has opened is woken, not released.

A release the hub refuses, or cannot be reached to grant, leaves the chunk held exactly as hold would.

[./hosts.md](./hosts.md) §Subscriptions states what a subscription is and how the host samples it, and
[../../architecture/crash-correctness/runner.md](../../architecture/crash-correctness/runner.md) §The usage-limit mark
states how the mark and the park hold across a crash.
