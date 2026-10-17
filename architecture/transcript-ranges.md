# Invocation transcript ranges (`bzh:invocation-transcript-ranges`)

Read when defining which invocation's turns a worker or judge may consume. For the crash behavior of the marker and its
advances, see [`./crash-correctness/transcripts.md`](./crash-correctness/transcripts.md#invocation-boundaries).

## Rule

Choose the boundary by the range being read: the judge's own range starts at `current_start` (the newest advance, or the
marker when there is none), while the worker range's end cap uses the judge's original marker.

## Why

A fresh judge elicitation must not consume the previous elicitation's turns, but advancing its start must not extend the
worker's range into judge turns.

## Boundary storage

`invocation_boundaries` (`blizzard/src/blizzard/runner/store/schema.py`) holds an invocation's true start:
`start_position`, `start_unreadable`, and `opened_at` are written once and never updated. A judge park or
overload-backoff resume reuses the standing judge marker for its fresh elicitation, so each such move is an append-only
fact in `invocation_boundary_advances` (`InvocationBoundaryStore.record_boundary_advance`) rather than a rewrite.

Each advance is keyed by the superseded elicitation's identity, `iso_utc(first_launched_at)`, and is a check-then-insert
over `(lease_id, generation, kind, superseded_invocation)`.

## Detect

A worker range capped by `current_start`, or a judge range starting at the original marker despite a recorded advance.

## Do

With a judge marker at position 8 and its newest advance at 12, the worker range ends at 8 and the judge range starts at
12.

## Don't

Use 12 as the worker range's end cap in that example: turns from the judge's earlier elicitation enter the worker range.
