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

The entry also reports subscription usage as the runner samples it: one member for each provider subscription the runner
has sampled, reporting that subscription's rate-limit utilization across the provider's reset windows. Each member is
reported under its own identity — a runner-unique slug and an operator-facing name — carrying only its newest sample,
with the time that sample was taken. A member stands only while that sample passes the staleness gate, so one whose
newest sample has aged out falls away. A subscription the entry does not report is simply absent — never a fabricated
zero, and never a reason to omit any other. Sampling is the whole of what the hub knows here: it holds no list of what
the runner declares, so a subscription declared but never sampled and one never declared at all are the same absence to
it. The collection is advisory: neither granting a chunk nor anything else the hub decides reads it.
