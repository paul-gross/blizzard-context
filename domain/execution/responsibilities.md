# Responsibilities

Which party owns each piece of execution, and what a runner's registry entry reports. Spoke of the
[execution hub](../execution.md).

The hub orchestrates the fleet's work: it owns chunks, graphs, artifacts, and the registry, and it grants work. A runner
executes work on its own machine, bound to one prepared workspace: it claims chunks, acquires environments, drives
workers through node-steps, and reports the facts. All contact is runner-initiated; the hub never reaches into a
runner's machine.

The hub never holds code, and holds conversation only as the transcript lane's capped segments — rule `bzh:never-code`,
owned by [../artifacts/never-code.md](../artifacts/never-code.md).

A runner's registry entry derives everything observable, never stored flags: liveness from its most recent contact, each
brake from the newest fact in its own stream — rule `bzh:facts-not-status`, owned by
[../../architecture/system-shape/store-facts.md](../../architecture/system-shape/store-facts.md).

The entry also reports its own capabilities: every coding-harness binding the runner can execute right now, one member
per harness id, each carrying that harness's observed version, the tier ids it can resolve, and an availability state
the runner computed about itself — a missing binary, an incompatible or unmapped configuration, a failed provider
authentication, or a failed conformance selftest all withhold it, never reported as a reason to the hub, only as the
flag itself. Availability is the same kind of fact the brakes above are: a runner's own assertion, superseded whole on
its next registration, never a condition the hub derives from other rows or from a capability's absence over time.

The entry also reports subscription usage, keyed off the runner's own declared roster: at registration a runner declares
its subscription roster — slug, name, and provider — and the next registration replaces the whole roster, the same way
capabilities does. While a roster is declared, the entry carries exactly one member per declared slug, whatever the age
of its sample: a never-sampled or long-stale slug is still a member. Each member is reported under its own identity — a
runner-unique slug and an operator-facing name — carrying its newest reported sample, with the time that sample was
taken, and its newest reported miss, with the miss's own reason. A slug no longer declared is no longer a member, even
though its sampled and missed reports persist and resume the moment it is redeclared. A lapsed credential still takes
precedence over a stale sample: a subscription whose newest lapsed miss is newer than its newest sample — or that was
never sampled at all — stands with that condition and no windows, and a fresh sample clears it. Only the newest miss per
slug is kept, so a later miss for any other reason clears a lapsed condition the same way a fresh sample does — the
reason itself renders nothing. A runner that has declared no roster at all keeps today's fallback instead: one member
per sampled slug, standing only while that sample passes the staleness gate. Either way there is never a fabricated
zero, and the collection stays advisory: neither granting a chunk nor anything else the hub decides reads it. How old
counts as too old to still show is a board presentation matter, not stated here.
