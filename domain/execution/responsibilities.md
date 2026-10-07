# Responsibilities

Which party owns each piece of execution, and what a runner's registry entry reports. Spoke of the
[execution hub](../execution.md).

The hub orchestrates the fleet's work: it owns chunks, graphs, artifacts, and the registry, and it grants work. A runner
executes work on its own machine, bound to one prepared workspace: it claims chunks, acquires environments, drives
workers through node-steps, and reports the facts. All contact is runner-initiated; the hub never reaches into a
runner's machine.

The hub is designed to hold references to code, never code, and holds conversation only as the transcript lane's capped
segments — rule `bzh:never-code`, owned by [../artifacts/never-code.md](../artifacts/never-code.md).

The hub adds every runner: it mints the runner's id when an operator adds it, and a runner has no identity before that,
nor any way to create one. The id never changes, and it is the runner's identity everywhere — every route, every fact
the runner authors, every operator action. The runner's name is its own and display-only: not unique, keyed on by
nothing. A registration that declares no name, or a blank one, keeps the name the hub holds; its capabilities are
superseded on every registration, even when empty. A runner added but never registered is reported as never connected,
with no capabilities, which is not the same as offline. Until its first registration a runner claims nothing; after it,
the runner keeps its id and name across a restart even while the hub is unreachable.

A runner's registry entry derives everything observable, never stored flags: liveness from its most recent contact, each
brake from the newest fact in its own stream — rule `bzh:facts-not-status`, owned by
[../../architecture/system-shape/store-facts.md](../../architecture/system-shape/store-facts.md). Whether the runner is
retired derives the same way, from its newest lifecycle fact ([retirement.md](./retirement.md)).

The entry also reports its own capabilities: every coding-harness binding the runner can execute right now, one member
per harness id, each carrying that harness's observed version, the tier ids it can resolve, and an availability state
the runner computed about itself — a missing binary, an incompatible or unmapped configuration, an unknown harness
version, a failed provider authentication, a failed conformance selftest, or an incompatible harness version (one the
binding does not admit, or classifies as blocking) all withhold it, never reported as a reason to the hub, only as the
flag itself. A version is unknown where a binding declares the versions it supports and the runner could not observe
one, or where a binding that also classifies the versions it admits could not classify the one observed. Availability is
the same kind of fact the brakes above are: a runner's own assertion, superseded whole on its next registration, never a
condition the hub derives from other rows or from a capability's absence over time.

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
a lapsed condition; a miss for any other reason sets no condition — including a reason outside the set the hub knows,
which the hub still accepts as a miss and reports without a named reason. What the board shows of the entry — the lapsed
notice in place of the bars, a named miss reason on a row with no sample — is its own presentation. A runner that has
declared no roster at all uses the roster-less fallback instead: a member stands while its sample passes the staleness
gate, or independently while a lapsed-credential miss newer than it does, with the same surviving-sample rule once
admitted either way. Either way there is never a fabricated zero, and the collection stays advisory: neither granting a
chunk nor anything else the hub decides reads it. How old counts as too old to still show is a board presentation
matter, not stated here.
