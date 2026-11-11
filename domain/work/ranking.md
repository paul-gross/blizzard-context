# Ranking

An operator's explicit order over each of the two lists an unacquired chunk rests in — `not_ready` and `ready`
([./statuses.md](./statuses.md)) — recorded as position facts. Spoke of the [work hub](../work.md).

Ranking exists wherever a chunk can be reordered by hand: the `not_ready` list's order decides which resting work an
operator promotes next, the `ready` queue's decides which unclaimed work a runner claims next. Reordering touches
neither promotion nor acquisition itself — it only orders what is already resting in one list or the other.

Each list is the whole tenant's: chunks of every project rest and rank in one `not_ready` list and one `ready` queue
([../projects.md](../projects.md)).

## A chunk's rank

A chunk's position in its list is its newest recorded explicit position, falling back — for a chunk never explicitly
positioned — to the instant it entered that list: the promotion instant for the `ready` queue, the mint instant for the
`not_ready` list, since `not_ready` membership begins at mint. The fallback is a point in real time, so a chunk resting
long unordered still sorts by when it arrived, not arbitrarily.

## Each list ranks within itself (`bzh:ranking-is-per-list`)

The `not_ready` list and the `ready` queue rank independently, never as one interleaved order: an operator's reorder
names chunks from one list only, and one naming a chunk from each is refused. A mint instant and a promotion instant do
not measure the same thing — falling back across lists would sort a chunk that has rested unordered a long time against
one just promoted by two incomparable clocks, an ordering with no meaning to an operator ranking either list.

A reorder of one list never repositions a chunk that belongs to the other.

## Promotion and demotion after rank

Promotion lands a chunk at the tail of the `ready` queue — after every chunk the queue already ranks, however the queue
was last ordered — unless the operator names an anchor, when it lands in that anchor's slot. A queue reorder that ran
before a promotion is never undone by it.

Demotion always stamps an explicit position in the backlog — the tail, or the named anchor's slot — so the mint-instant
fallback never ranks a demoted chunk.

## Claim order is not a third ranked list

The `ready` queue's rank is not the order a runner is offered work in. Claim order groups the same ready chunks by their
urgency's place in the tenant's set, most urgent first, keeping rank within a group
([./urgency.md](./urgency.md#claim-order), [../execution/acquisition.md](../execution/acquisition.md)). It is derived on
every read from the rank and the set's order and never stored, so no reorder writes it and `bzh:ranking-is-per-list`
still holds: the queue is ranked once, and claim order only reads it.

## See also

- [./statuses.md](./statuses.md) — `not_ready` and `ready`, and what moves a chunk from one to the other.
- [../operations.md](../operations.md) — a reorder produces no activity-feed row, in either list.
