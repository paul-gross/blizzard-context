# Wire timestamps

The rule an instant is held to wherever it crosses a boundary — store column, domain comparison, API response, TS
consumer. Each rule follows the slot skeleton owned by `winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Instants are UTC-aware end to end (`bzh:utc-instants`)

**Rule.** Instants are **UTC-aware end to end**: store columns use `UtcDateTime` so reads and writes are aware; domain
comparisons coerce with `as_utc`; every wire timestamp is serialized with `iso_utc`, so the string always carries an
explicit offset. A naive datetime never crosses a boundary.

**Why.** A naive ISO string is silently reinterpreted in the reader's local zone — `Date.parse` treats an offset-less
stamp as *local* time, so a UTC-5 browser reads a stamp five hours in the future, and any defensive clamp on the reader
side masks that as fresh. The offset is what makes an instant mean the same thing on both ends of the wire.

**Scope.** Spans four layers, one mechanism each: the store column (`UtcDateTime`, a `TypeDecorator` over `DateTime` —
normalizes on write, re-attaches `UTC` on read), the domain comparison (`as_utc`, idempotent — kept even once every
column is `UtcDateTime`-typed, because a domain function's inputs aren't guaranteed to have come through the store), the
wire edge (`iso_utc` at serialization), and the frontend consumer (a derived age must never clamp a large negative value
to a confident zero — fall through to the source-of-truth boolean the backend already derived instead of guessing on the
reader's clock).

**Detect.** A raw `.isoformat()` in an API edge; a `DateTime` column not typed `UtcDateTime`; a `datetime.fromisoformat`
result that isn't coerced before a comparison or before landing in a store write; a frontend clamping a negative age to
zero without a bound.

**Do.** `iso_utc(x)` at the edge; `UtcDateTime` on the column; `as_utc` before comparing; a bounded tolerance on the
frontend (a few tens of seconds of benign clock skew reads as "now"; anything past that falls through to the hub-derived
liveness boolean, never a confident `0s`).

**Don't.** `x.isoformat()` on a store-sourced datetime — sqlite drops the tzinfo and the wire will lie;
`Math.max(0, age)` on the frontend — it turns a five-hour-stale runner into "seen 0s ago".

## See also

- [`./persistence.md`](./persistence.md) — `bzh:sql-portable`, the portable-SQL constraint `UtcDateTime` (a plain
  `TypeDecorator` over `DateTime`) stays inside.
- [`./python.md`](./python.md) — the toolchain (`ruff`, `pyright`, `pytest`) this rule's fitness test
  (`tests/test_wire_timestamps.py`) runs under.
- [`../architecture/clean-architecture.md`](../architecture/clean-architecture.md) — `bzh:domain-core`, why `as_utc`
  stays at the domain comparison site rather than being deleted once the store is typed.
- [`./frontend.md`](./frontend.md) — `bzh:frontend-formatters`, the frontend consumer's one owner:
  `ageMs`/`formatAge`/`formatSeenAgo` (`fleet/lib/when.ts`) implement this rule's bounded-skew-then-fall-through clause
  once for every relative-age render.
