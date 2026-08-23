# Logging (`bzh:structlog-logging`)

How blizzard code emits diagnostics, in the Rule/Why/Detect/Do/Don't slot skeleton owned by
`winter-canon:/rule-shape.md` (`canon:rule-shape`).

## Rule

All logging goes through structlog, and — regardless of renderer — one call-site convention holds: pass structured
fields as key-value pairs, never interpolated into the message string, where no consumer can filter on them.

## Why

Structured fields let every consumer render the same event without parsing the message string, and TTY-selected
rendering means one call site serves agents reading JSON and humans reading a console.

## Levels

| Level     | Convention                                                                                                                                                                                                                                                                                                                                |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DEBUG`   | Per-item traces, opt-in via log level.                                                                                                                                                                                                                                                                                                    |
| `INFO`    | A major lifecycle event ("reconcile started", "chunk delivered"): one line per event, not per item.                                                                                                                                                                                                                                       |
| `WARNING` | A recoverable condition the caller continued past.                                                                                                                                                                                                                                                                                        |
| `ERROR`   | A wrapped exception at the boundary that transforms it, logged once at the wrap site (the injected error factory, [../architecture/repository-access.md](../architecture/repository-access.md)) and never re-logged or catch-log-rethrown by callers — once at the boundary keeps a crash trace to one record, not a duplicate per layer. |

## Renderers

The output renderer is selected by configuration: a JSON renderer for agents, services, and CI, a colored key-value
console renderer for interactive runs — defaulting by TTY detection and overridable by config or env.

## Reserved field keys

Three names are structlog's own call kwargs and can never be field keys: `event` (the message itself), `exc_info`, and
`stack_info`; passing one raises `TypeError` at the call site, typically on an already-degraded failure path where the
log was the diagnostic. `event=` is the natural name for a hook or SSE field; name the field for its domain instead
(`hook_event=`, `event_type=`).

## Detect

- Structured data interpolated into the message string instead of passed as fields.
- A catch-log-rethrow that re-logs an error already logged at its wrap site.
- A stdlib `logging.getLogger`, or a second logging library beside structlog.
- A `print()` in daemon or service code: the injected reporter owns user-facing output and the logger owns diagnostics;
  `print()` belongs in CLI top-level glue only.

## Do

`log.info("chunk delivered", chunk_id=chunk.id, repo=repo.name)` — the event as message, the context as fields.

## Don't

`log.info(f"chunk {chunk.id} delivered to {repo.name}")` — the same event with its context buried in the string, where
no consumer can filter on it.
