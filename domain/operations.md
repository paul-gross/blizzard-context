# Operational visibility (`bzh:operational-event-log`)

Operational visibility is two operator-visible feeds over the same facts, read side by side: the **event log**, carrying
only the failures a human must act on, and the **activity feed** of everything recent — situational awareness rather
than triage. Both read newest first. This file is definitional — a taxonomy of event kinds and how they surface
(`canon:rule-shape` §File kinds) — and part of the domain model at [./index.md](./index.md).

## The event log

The log is the hub's durable, append-only, typed record of operationally-significant runner and worker failures — the
subset an operator must act on, not a mirror of every state delta. The hub owns the log, recording each event and
re-broadcasting it live; a failure the runner detects reaches it as a durable fact the runner reports.

Each event carries a severity (`info` | `warning` | `critical`), a noun-verb kind name, the runner/chunk/lease/node it
concerns where present, a human-legible message, and an open detail payload. Each event links back to its chunk. The log
reads newest first across every severity, each row keeping its severity, and is filterable by severity, runner, or
chunk.

Both vocabularies are closed: the hub refuses an `event.recorded` fact whose kind is not in §Event kinds, or whose
severity is not the one that kind declares.

The log is bounded, at most 200 rows per read, the filters applied first and the cap after recency ordering — it keeps
the newest rows, whatever their severity. The route caps below the hub's general list maximum.

### Event kinds

| Kind                           | Severity   | Meaning                                                                                                                                                                                                                                                                                             |
| ------------------------------ | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `needs-human`                  | `critical` | A standing open escalation                                                                                                                                                                                                                                                                          |
| `worker-lost`                  | `critical` | Retries are exhausted; the attempt is lost to a human                                                                                                                                                                                                                                               |
| `owner-unresolvable`           | `critical` | An existing session's recorded harness owner is unknown or unavailable to this runner; the chunk escalates rather than resuming under a substitute                                                                                                                                                  |
| `no-acceptable-harness`        | `critical` | A fresh mint's every acceptable harness is unknown, unavailable, or resolves no authored tier; the chunk escalates rather than minting under the runner default. On retry (`via=requeue`), the failed owner is outside the current acceptable set; the chunk escalates rather than switching owners |
| `hub-node-unroutable-outcome`  | `critical` | A hub node produced an outcome its graph authors no edge for, so the chunk re-polls it until someone authors one — announced per node visit, not per poll                                                                                                                                           |
| `attempt-failed`               | `warning`  | An attempt died and a retry will run                                                                                                                                                                                                                                                                |
| `command-failed`               | `warning`  | A captured spawn, git-push, or environment-prep command failed, carrying the command and its stderr tail                                                                                                                                                                                            |
| `work-item-close-failed`       | `warning`  | A closure attempt failed, and a later sweep retries it; or found the item gone at its source, which retires the closure unretried                                                                                                                                                                   |
| `transcript-truncated`         | `warning`  | A transcript segment stopped shipping content — recorded on the segment itself as well, never silent                                                                                                                                                                                                |
| `transcript-sidechain-dropped` | `warning`  | A transcript segment observed unlinked sidechain turns it cannot attribute, latched so it warns once per (segment, agent)                                                                                                                                                                           |
| `worker-context-warned`        | `warning`  | A worker session's context tokens crossed the configured warn line — reported once per lease, on its first crossing                                                                                                                                                                                 |
| `trace-export-failed`          | `warning`  | A daemon's trace export failed after a success; its cursor holds and its sweep retries with backoff — announced once per outage                                                                                                                                                                     |
| `trace-window-skipped`         | `warning`  | A daemon's trace cursor jumped forward, carrying the skipped window so it can be replayed                                                                                                                                                                                                           |
| `trace-config-rejected`        | `warning`  | Tracing was configured in a way the daemon cannot honor, naming the setting; that daemon serves with tracing off                                                                                                                                                                                    |
| `egress-write-failed`          | `warning`  | A fact-egress pass failed after a success — a missing or unwritable directory, a full disk, a name collision, a row the format cannot hold — carrying the cause; its cursor holds and its sweep retries with backoff, announced once per outage                                                     |
| `egress-config-rejected`       | `warning`  | The export was configured in a way the hub cannot honor — Parquet without its install extra, naming it; the hub serves with the export off                                                                                                                                                          |
| `attempt-abandoned`            | `info`     | Given up because the chunk moved on (reassigned or detached), not because the work failed                                                                                                                                                                                                           |
| `work-item-closed`             | `info`     | A landed chunk's work item was closed at its own source ([./work/chunk.md](./work/chunk.md))                                                                                                                                                                                                        |
| `trace-export-recovered`       | `info`     | A daemon's first trace export to succeed after a failure                                                                                                                                                                                                                                            |
| `egress-write-recovered`       | `info`     | The first fact-egress pass to succeed after a failure                                                                                                                                                                                                                                               |
| `egress-cursor-reset`          | `info`     | An operator moved a fact-egress dataset's cursor, carrying the dataset, the position it left, the one it moved to, and whether the window between was skipped or repeated — a reset to the position it already stands at reads as repeated                                                          |

An escalation ([./humans/escalation.md](./humans/escalation.md)) remains its own fact under its own supersession rule;
the log does not re-model it — every currently-open escalation projects as a `needs-human` critical event, one row in
one surface. The per-attempt `worker-lost` event and the standing `needs-human` projection are distinct, complementary
kinds — the terminal failure is not double-counted.

A deliberately deferred failure — a runner that told its operator it will start no processes — surfaces nothing.

## The activity feed

The activity feed is reconstructed fresh from the durable facts the domain already keeps — transitions, questions, gate
decisions, runner pauses, and event-log rows; no separate log is written for it. It is bounded: 24 hours by default, at
most the 200 newest rows. The route caps below the hub's general list maximum.

A route claim is its own occurrence, distinct from a node transition. Lease-mint and usage facts can refresh chunk,
spend, and other views without adding another activity row: only the claim's route fact belongs in the feed, once. Live
frames naming the same fact share one row even when they arrive on different event types or replay; keyless loggable
occurrences remain separate. The live feed uses the same mapped chunk causes as the durable activity read, not the
latest status displayed in a chunk-change frame.

These produce no activity-feed row:

- direct chunk edits — in-place mutation, with no durable fact behind it;
- reorders of the `not_ready` list or the `ready` queue ([./work/ranking.md](./work/ranking.md)) — per-chunk rows
  carrying no news;
- runner registration and heartbeats — no durable fact, and muted liveness noise;
- a runner's subscription-usage samples and misses — rate-limit telemetry for its registry row, not fleet activity;
- a deleted chunk's facts — once a chunk is deleted, every fact of that chunk is suppressed except the deletion itself.

## Re-telling and reflecting the record

An operator can have the record told again, or reflected elsewhere, without changing it:

- **A window ending in the future is refused.** A trace replay or a fact-egress backfill names a window that must end at
  or before now; one reaching past now is refused outright, before anything is told.
- **A backfill past the live position is written anyway.** Backfill rows reaching beyond a dataset's live cursor are
  written, and the live export writes those rows again when its cursor gets there — the repetition is expected.
- **A dry run needs no destination.** A dry-run backfill or replay only counts, so it runs with the export or tracing
  turned off; a real one with nowhere to write is refused.
- **A re-derive counts only what it derived.** Re-deriving a chunk's or the fleet's transcript events reports the
  segments it actually derived: one gone by then, or whose chunk has no graph to place it on, is not counted. A
  re-derive naming a chunk or segment the hub does not hold answers with nothing derived rather than an error — it is a
  convergence trigger, not a read.
- **A transcript record's first write wins.** A re-shipped record under a key already accepted is acknowledged as
  applied without comparing its content; a runner that needs to change what it shipped ships a superseding segment.
- **Forge labels follow the annotating set.** A work source the hub annotates carries status labels on its forge items.
  The hub remembers which sources it annotates across restarts, so a source taken out of annotation has every status
  label it carries cleared once; a source removed from the hub's configuration entirely keeps its labels, with nothing
  left to clear them through. A hub that never annotated a source never clears it.

## See also

- [./work.md](./work.md) — the transitions and statuses the activity feed reconstructs from.
- [./execution.md](./execution.md) — leases, epochs, and the reap/advance failure paths events hang off.
- [./humans.md](./humans.md) — escalation and takeover: the human entries behind a `needs-human` event.
