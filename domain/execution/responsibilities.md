# Responsibilities

Which party owns each piece of execution. Spoke of the [execution hub](../execution.md).

The hub orchestrates the fleet's work: it owns chunks, graphs, artifacts, and the registry, and it grants work. A runner
executes work on its own machine, bound to one prepared workspace: it claims chunks, acquires environments, drives
workers through node-steps, and reports the facts. All contact is runner-initiated; the hub never reaches into a
runner's machine.

The hub never holds code, and holds conversation only as the transcript lane's capped segments — rule `bzh:never-code`,
owned by [../artifacts/never-code.md](../artifacts/never-code.md).

A runner's registry entry derives everything observable, never stored flags: liveness from its most recent contact, each
brake from the newest fact in its own stream — rule `bzh:facts-not-status`, owned by
[../../architecture/system-shape/store-facts.md](../../architecture/system-shape/store-facts.md).

The entry also reports the usage of every provider subscription the runner declares — its rate-limit utilization in each
of the provider's reset windows — under that subscription's own identity: a runner-unique slug, an operator-facing name,
and its newest sample with the time it was taken. Every member passes its own staleness gate on its own sample, so a
subscription never sampled, or whose newest sample is stale, is simply absent from the collection — never a fabricated
zero, and never a reason to omit any other. The collection is advisory: neither granting a chunk nor anything else the
hub decides reads it.
