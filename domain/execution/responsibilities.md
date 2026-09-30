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
[../../architecture/system-shape/store-facts.md](../../architecture/system-shape/store-facts.md). Whether the runner is
retired derives the same way, from its newest lifecycle fact ([retirement.md](./retirement.md)).

The entry also reports its own capabilities: every coding-harness binding the runner can execute right now, one member
per harness id, each carrying that harness's observed version, the tier ids it can resolve, and an availability state
the runner computed about itself — a missing binary, an incompatible or unmapped configuration, an unknown harness
version, a failed provider authentication, or a failed conformance selftest all withhold it, never reported as a reason
to the hub, only as the flag itself. A version is unknown where a binding declares the versions it supports and the
runner could not observe one, or where a binding that also classifies the versions it admits could not classify the one
observed; it withholds exactly as an incompatible one does. Availability is the same kind of fact the brakes above are:
a runner's own assertion, superseded whole on its next registration, never a condition the hub derives from other rows
or from a capability's absence over time.

The entry also reports subscription usage, keyed off the runner's own declared roster: at registration a runner declares
its subscription roster — slug, name, and provider — and the next registration replaces the whole roster, the same way
capabilities does. While a roster is declared, the entry carries exactly one member per declared slug, whatever the age
of its sample: a never-sampled or long-stale slug is still a member. Each member is reported under its own identity — a
runner-unique slug and an operator-facing name — carrying its newest reported sample, with the time that sample was
taken, and its newest reported miss, with the miss's own reason. A slug no longer declared is no longer a member, even
though its sampled and missed reports persist and resume the moment it is redeclared. A lapsed credential takes
precedence: when a subscription's newest miss is a lapsed credential newer than its newest (or absent) sample, that
condition is set on the entry, and a surviving sample's own fields stay on the entry alongside it — only a slug that has
never sampled at all carries no windows with the condition. A fresh sample, or a later miss for any other reason, clears
a lapsed condition; a miss for any other reason sets no condition. What the board shows of the entry — the lapsed notice
in place of the bars, a named miss reason on a row with no sample — is its own presentation. A runner that has declared
no roster at all uses the roster-less fallback instead: a member stands while its sample passes the staleness gate, or
independently while a lapsed-credential miss newer than it does, with the same surviving-sample rule once admitted
either way. Either way
there is never a fabricated zero, and the collection stays advisory: neither granting a chunk nor anything else the hub
decides reads it. How old counts as too old to still show is a board presentation matter, not stated here.
