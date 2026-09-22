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

The entry also reports subscription usage as the runner samples it: one member for each provider subscription the runner
has sampled, reporting that subscription's rate-limit utilization across the provider's reset windows. Each member is
reported under its own identity — a runner-unique slug and an operator-facing name — carrying only its newest sample,
with the time that sample was taken. A member stands only while that sample passes the staleness gate, so one whose
newest sample has aged out falls away. A sampler that produces nothing reports a miss instead, carrying only its reason;
one reason, a lapsed credential, is itself a member: a subscription whose newest lapsed miss is newer than its newest
sample — or that was never sampled at all — stands with that condition and no windows, for as long as the miss itself
passes the same staleness gate, and a fresh sample clears it. A miss for any other reason changes nothing the hub shows.
A subscription the entry does not report is simply absent — never a fabricated zero, and never a reason to omit any
other. Samples and misses are the whole of what the hub knows here: it holds no list of what the runner declares, so a
subscription declared but never attempted and one never declared at all are the same absence to it. The collection is
advisory: neither granting a chunk nor anything else the hub decides reads it.
