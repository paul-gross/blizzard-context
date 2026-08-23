# UTC instants on the wire (`bzh:utc-instants`)

The rule an instant is held to wherever it crosses a boundary — store column, domain comparison, API response, TS
consumer — in the Rule/Why/Detect/Do/Don't slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Rule

Instants are UTC-aware end to end, and a naive datetime never crosses a boundary.

## Why

A naive ISO string is silently reinterpreted in the reader's local zone — `Date.parse` treats an offset-less stamp as
local time, so a UTC-5 browser reads it five hours in the future.

## Detect

A raw `.isoformat()` at an API edge; a `DateTime` column not typed `UtcDateTime`; a `datetime.fromisoformat` result not
coerced before a comparison or a store write. The rule's fitness test is `tests/test_wire_timestamps.py`, run under
[./python.md](./python.md)'s toolchain like any unit test.

## Do

What UTC-aware means at each boundary:

- **Store** — columns use `UtcDateTime`, a `TypeDecorator` over `DateTime` that normalizes on write and re-attaches UTC
  on read, so reads and writes are aware. `UtcDateTime` stays inside [./persistence.md](./persistence.md)'s portable-SQL
  constraint (`bzh:sql-portable`).
- **Domain** — comparisons coerce with `as_utc`, which is idempotent and is kept even once every column is
  `UtcDateTime`-typed, because a domain function's inputs are not guaranteed to have come through the store. See
  [../architecture/clean-architecture.md](../architecture/clean-architecture.md) `bzh:domain-core` for why `as_utc`
  stays at the comparison site rather than being deleted once the store is typed.
- **Wire** — every wire timestamp is serialized with `iso_utc`, so the string always carries an explicit offset.
- **TS consumer** — the frontend never clamps a large negative derived age to a confident zero: a bounded tolerance
  reads a few tens of seconds of benign clock skew as "now", and anything past that falls through to the source-of-truth
  liveness boolean the backend already derived. `ageMs`, `formatAge`, and `formatSeenAgo` in `fleet/lib/when.ts`
  implement this bounded-skew-then-fall-through clause once for every relative-age render — see
  [./frontend.md](./frontend.md) `bzh:frontend-formatters`.

## Don't

- `x.isoformat()` on a store-sourced datetime makes the wire lie, because sqlite drops the tzinfo.
- `Math.max(0, age)` on the frontend turns a five-hour-stale runner into "seen 0s ago".
