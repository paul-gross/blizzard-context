# Logging

How blizzard code emits diagnostics. Follows the slot skeleton owned by `winter-canon:/rule-shape.md`
(`canon:rule-shape`).

## Structured logging with structlog (`bzh:structlog-logging`)

**Rule.** All logging goes through **structlog**, with the output renderer selected by configuration — a **JSON
renderer** when agents, services, or CI consume the logs, a **human console renderer** (colored key-value) for
interactive runs, defaulting by TTY detection and overridable by config/env. One call-site convention regardless of the
renderer: pass structured fields as key-value pairs, never interpolated into the message string. Three names are
structlog's own call kwargs and can never be field keys: `event` (the message itself), `exc_info`, and `stack_info`.
Passing one — and `event=` is the natural name for a hook or SSE field — raises `TypeError` at the call site, typically
on an already-degraded failure path where the log was the diagnostic. Name the field for its domain instead
(`hook_event=`, `event_type=`). The level conventions:

- **ERROR** — a wrapped exception at the boundary that transforms it, logged **once** at the wrap site (the injected
  error factory, [../architecture/repository-access.md](../architecture/repository-access.md)) and never re-logged by
  callers.
- **WARNING** — a recoverable condition the caller continued past (a skipped item, a missing optional config).
- **INFO** — a major lifecycle event (`reconcile started`, `chunk delivered`): one line per event, not per item.
- **DEBUG** — per-item traces (per-chunk step, per-repo action), opt-in via log level.

No `print()` in daemon or service code — use the injected reporter for user-facing output and the logger for
diagnostics; `print()` belongs in CLI top-level glue only.

**Why.** Structured fields let the JSON and console renderers, the dashboard, and CI all render the same event without
parsing a message string, and TTY-selected rendering means one call-site serves both an agent reading JSON and a human
reading a console — the intelligence lives in the renderer, not the call. Logging a wrapped error once at the boundary
keeps a crash trace to a single record instead of one duplicate per layer it passed through.

**Detect.** A `logging.getLogger` / stdlib-logging call or a second logging library used instead of structlog;
structured data interpolated into the message string (`f"failed cwd={cwd} exit={code}"`) rather than passed as fields; a
catch-log-rethrow that logs an error already logged at its wrap site; a structlog call passing `event=`, `exc_info=`, or
`stack_info=` as a data field; `print()` in daemon or service code.

**Do.** `log.info("chunk delivered", chunk_id=chunk.id, repo=repo.name)` — the event as the message, the context as
fields; renderer chosen by config.

**Don't.** `log.info(f"chunk {chunk.id} delivered to {repo.name}")` — the fields are now trapped in the string, and no
consumer can filter on them.
