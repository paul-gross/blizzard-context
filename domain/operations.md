# Operational visibility (`bzh:operational-event-log`)

The hub's durable, severity-ranked record of the operationally-significant failures that happen to runners and workers.
Definitional — a taxonomy of the operational event kinds and how they surface (`canon:rule-shape` §File kinds).
Part of the [domain model](./index.md).

The failures that cost the most are the least visible: a worker that exits without recording a completion, a chunk stalled behind a dead process, a spawn/push/attach command that failed on a missing environment var. A chunk's *status* says a chunk is stuck; it does not say **why**. The **operational event log** is the surface that does.

Operational visibility is **two** distinct, operator-visible feeds over the same underlying facts, not one — each answering a different question. The **operational event log** (this section onward) surfaces only the failures a human must act on, severity-ranked. The **activity feed** ([below](#the-activity-feed)) is a pure-recency history of everything recent across the fleet, for at-a-glance situational awareness rather than triage.

## What it is

A durable, append-only, **typed and severity-ranked** series of the operationally-significant things that happen to runners and workers — not a mirror of every state delta, but the subset an operator must act on. The **hub owns it**: the runner detects a failure and reports it as a durable fact; the hub records it into the log and re-broadcasts it live. Each event carries a **severity** (`info` | `warning` | `critical`), a **kind** (its `noun-verb` name), the runner/chunk/lease/node it concerns where those exist, a human-legible message, and an open `detail` payload. Like every fact in the system it is never mutated once written and carries no mutable state of its own — the log *is* the history.

The severity vocabulary is **closed**, and closed the hard way: the log ranks by it, so a value outside the three sorts below every ordinary row and no severity filter reaches it — an emitter inventing a fourth buries its own event rather than adding a band.

## The kinds

The runner surfaces failures at the single point every failed attempt already funnels through, and at each command it captures; the hub adds the ones only it is positioned to see:

| Kind | Severity | When |
|------|----------|------|
| `attempt-failed` | `warning` | An attempt died and another will run (a retry) |
| `worker-lost` | `critical` | Retries are exhausted — the attempt is lost to a human |
| `attempt-abandoned` | `info` | The attempt was given up because the chunk moved on (reassigned/detached), not because the work failed |
| `command-failed` | `warning` | A captured spawn / git-push / environment-prep command failed, carrying the command and its stderr tail |
| `needs-human` | `critical` | A standing open escalation (see below) |
| `hub-node-unroutable-outcome` | `critical` | A hub node produced an outcome its graph authors no edge for — nothing routes, so the chunk re-polls that same outcome until someone authors one. Announced once per node visit, not once per poll |
| `work-item-closed` | `info` | A landed chunk's work item was closed at its own source ([work.md](./work.md) §Chunk) |
| `work-item-close-failed` | `warning` | That closure attempt failed; a later sweep retries it |

A deliberately-deferred failure — a runner that has told its operator it will start no processes — surfaces **nothing**: the failure is deferred, not an outcome to act on.

## Escalation is one kind, not a separate surface

An **escalation** ([humans.md](./humans.md) §Escalation) is still its own fact with its own supersession rule; the operational log does **not** re-model it. Instead the read **unifies** the two: every currently-open escalation projects into the feed as a `needs-human` / `critical` event, so `needs_human` is one row in one surface rather than a place an operator has to look separately. The granular per-attempt events (`worker-lost` records *this attempt died*) and the standing escalation projection (*retries are now exhausted*) are complementary, distinct kinds — the terminal failure is not double-counted.

## How the operational log is read

The log surfaces **newest-and-most-severe first** (critical before warning before info, newest within a band), filterable by severity / runner / chunk. It is read as a whole, rides the fleet's existing live-event spine so an open board updates without polling, and each event links back to its chunk and — where one exists — the worker transcript. It is a **visibility** surface: it makes failures legible in-product; it does not repair the underlying failure modes.

## The activity feed

The **activity feed** is the fleet's second operator-visible feed: a reconstructed, recency-ordered history of recent chunk and runner activity, read fresh from the same durable facts the rest of the domain already keeps (transitions, questions, gate decisions, runner pauses) — no separate log is written for it.

Where the operational event log ranks by severity, the activity feed orders strictly by **pure recency** — newest first, with no severity axis at all. It exists to answer "what just happened across the fleet", not "what needs my attention", and the two feeds are read side by side rather than one subsuming the other.

The feed is bounded, not a full history: by default the last **24 hours**, capped at the most recent **200** rows.

Not every fact the domain records produces a row. Four things are structurally excluded:

- **A direct chunk edit** — an in-place field mutation records no durable fact behind it, so there is nothing to reconstruct an entry from.
- **A ready-queue reorder** — it writes one row per moved chunk with no per-row news of its own; the reorder as a whole is not activity an operator needs surfaced row-by-row.
- **A runner's registration or heartbeat** — these record no durable fact either, and — being routine liveness noise already flooding the live feed — are muted rather than reproduced in a surface meant for legibility.
- **A runner's own subscription-usage sample** — durably recorded, like the reorder above, but rate-limit telemetry rather than fleet activity: it belongs to the runner's registry row, where its current utilization is read, not to a history of what happened.

## See also

- [humans.md](./humans.md) — escalation and takeover, the human entries a `needs-human` event stands for.
- [execution.md](./execution.md) — leases, epochs, and the reap/advance failure paths the events hang off.
- [work.md](./work.md) — the transitions and statuses the activity feed reconstructs its rows from.
