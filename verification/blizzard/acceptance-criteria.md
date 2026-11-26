# What proves the MVP acceptance criteria (`bzh:matrix-acceptance-criteria`)

The MVP acceptance journey's claims are exercised end to end by named methods in the [matrix](../blizzard.md). Which
method carries which:

| Claim                                                                                                                                                              | Proven by                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| A worker reads its chunk's work items through the hub pass-through                                                                                                 | `blizzard:journey`'s every-chunk work-item read, and `blizzard:service-test`'s pass-through case |
| Exactly-once claim and delivery, zombie fencing of a reaped lease, and recovery from `kill -9` at every step boundary                                              | `blizzard:crash-sweep` plus the invariant checker                                                |
| Escalation to `needs_human` with a working takeover command, ask and answer, the review-fail loop, the live board with its queue shaping, and human gate decisions | `blizzard:service-test`'s fleet specs, `blizzard:ui`, and `blizzard:journey`                     |
| Delivery-conflict reconcile                                                                                                                                        | the component-tier partial-land test, plus `blizzard:journey`'s clean multi-repo grouped land    |
