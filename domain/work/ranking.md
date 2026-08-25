# Ranking

An operator's explicit order over each of the two lists an unacquired chunk rests in — `not_ready` and `ready`
([./statuses.md](./statuses.md)) — recorded as position facts. Spoke of the [work hub](../work.md); the invariant below
is written in the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

Ranking exists wherever a chunk can be reordered by hand: the `not_ready` list's order decides which resting work an
operator promotes next, the `ready` queue's decides which unclaimed work a runner claims next. Reordering touches
neither promotion nor acquisition itself — it only orders what is already resting in one list or the other.

## A chunk's rank

A chunk's position in its list is its newest recorded explicit position, falling back — for a chunk never explicitly
positioned — to the instant it entered that list: the promotion instant for the `ready` queue, the mint instant for the
`not_ready` list, since `not_ready` membership begins at mint. The fallback is a point in real time, so a chunk resting
long unordered still sorts by when it arrived, not arbitrarily.

## Each list ranks within itself (`bzh:ranking-is-per-list`)

**Rule.** The `not_ready` list and the `ready` queue rank independently, never as one interleaved order: an operator's
reorder names chunks from one list only, and one naming a chunk from each is refused.

**Why.** A mint instant and a promotion instant do not measure the same thing — falling back across lists would sort a
chunk that has rested unordered a long time against one just promoted by two incomparable clocks, an ordering with no
meaning to an operator ranking either list.

**Detect.** A reorder that accepts chunk ids without also requiring they share one list's status.

**Do.** Resolve a reorder's candidate chunks against the one list it names before ranking; refuse a reorder mixing
chunks from both.

**Don't.** Merge the two lists' explicit positions into one shared order, or let a reorder for one list silently
reposition a chunk that belongs to the other.

## Promotion after rank

Promotion always lands a chunk at the tail of the `ready` queue — after every chunk the queue already ranks, however the
queue was last ordered — never mid-queue and never ahead of an explicit position an operator set before the promotion. A
queue reorder that ran before a promotion is never undone by it.

## See also

- [./statuses.md](./statuses.md) — `not_ready` and `ready`, and what moves a chunk from one to the other.
- [../operations.md](../operations.md) — a reorder produces no activity-feed row, in either list.
