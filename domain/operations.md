# Operational visibility (`bzh:operational-event-log`)

Operational visibility is two operator-visible feeds over the same facts, read side by side: the severity-ranked **event
log**, carrying only the failures a human must act on, and the pure-recency **activity feed** of everything recent —
situational awareness rather than triage. This file is definitional — a taxonomy of event kinds and how they surface
(`canon:rule-shape` §File kinds) — and part of the domain model at [./index.md](./index.md).

## The event log

The log is the hub's durable, append-only, typed, severity-ranked record of operationally-significant runner and worker
failures — the subset an operator must act on, not a mirror of every state delta. The hub owns the log, recording each
event and re-broadcasting it live; a failure the runner detects reaches it as a durable fact the runner reports.

Each event carries a severity (`info` | `warning` | `critical`), a noun-verb kind name, the runner/chunk/lease/node it
concerns where present, a human-legible message, and an open detail payload. Each event links back to its chunk and,
where one exists, the worker transcript. The log reads newest-and-most-severe first — critical before warning before
info, newest within a band — and is filterable by severity, runner, or chunk.

The severity vocabulary is closed: the log ranks by it, so a value outside the three sorts below every row and no filter
reaches it — a fourth severity buries its own event.

### Event kinds

| Kind                          | Severity   | Meaning                                                                                                                                                   |
| ----------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `needs-human`                 | `critical` | A standing open escalation                                                                                                                                |
| `worker-lost`                 | `critical` | Retries are exhausted; the attempt is lost to a human                                                                                                     |
| `hub-node-unroutable-outcome` | `critical` | A hub node produced an outcome its graph authors no edge for, so the chunk re-polls it until someone authors one — announced per node visit, not per poll |
| `attempt-failed`              | `warning`  | An attempt died and a retry will run                                                                                                                      |
| `command-failed`              | `warning`  | A captured spawn, git-push, or environment-prep command failed, carrying the command and its stderr tail                                                  |
| `work-item-close-failed`      | `warning`  | A closure attempt failed; a later sweep retries it                                                                                                        |
| `attempt-abandoned`           | `info`     | Given up because the chunk moved on (reassigned or detached), not because the work failed                                                                 |
| `work-item-closed`            | `info`     | A landed chunk's work item was closed at its own source ([./work/chunk.md](./work/chunk.md))                                                              |

An escalation ([./humans/escalation.md](./humans/escalation.md)) remains its own fact under its own supersession rule;
the log does not re-model it — every currently-open escalation projects as a `needs-human` critical event, one row in
one surface. The per-attempt `worker-lost` event and the standing `needs-human` projection are distinct, complementary
kinds — the terminal failure is not double-counted.

A deliberately deferred failure — a runner that told its operator it will start no processes — surfaces nothing.

## The activity feed

The activity feed is reconstructed fresh from the durable facts the domain already keeps — transitions, questions, gate
decisions, runner pauses; no separate log is written for it. It is bounded: 24 hours by default, at most the 200 newest
rows.

Four things produce no activity-feed row:

- direct chunk edits — in-place mutation, with no durable fact behind it;
- reorders of the `not_ready` list or the `ready` queue ([./work/ranking.md](./work/ranking.md)) — per-chunk rows
  carrying no news;
- runner registration and heartbeats — no durable fact, and muted liveness noise;
- a runner's subscription-usage sample — rate-limit telemetry for its registry row, not fleet activity.

## See also

- [./work.md](./work.md) — the transitions and statuses the activity feed reconstructs from.
- [./execution.md](./execution.md) — leases, epochs, and the reap/advance failure paths events hang off.
- [./humans.md](./humans.md) — escalation and takeover: the human entries behind a `needs-human` event.
