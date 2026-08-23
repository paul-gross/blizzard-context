# The hub/runner responsibility split

- **The hub** orchestrates the fleet's work: it owns chunks, graphs, artifacts, and the registry, and it grants work. It
  never holds code, and holds conversation only as the transcript lane's capped segments (`bzh:never-code` in
  [artifacts.md](../artifacts.md)); it never reaches into a runner's machine.
- **A runner** executes work on its own machine, bound to one prepared workspace: it claims chunks, acquires
  environments, drives workers through node-steps, and reports the facts. All contact is runner-initiated — the hub
  pushes nothing into a dev box.

A runner's registry entry derives everything observable: liveness derives from its most recent contact, and each brake
from the newest fact in its own stream — never stored flags (`bzh:facts-not-status` in
[../architecture/system-shape/store-facts.md](../../architecture/system-shape/store-facts.md)).
