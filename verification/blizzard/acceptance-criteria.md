# What proves the MVP acceptance criteria (`bzh:matrix-acceptance-criteria`)

The MVP acceptance journey's thirteen criteria are exercised end to end by named methods in the
[matrix](../blizzard.md). Which method carries which:

| Criteria                                       | Proven by                                                                                     |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 1 — pass-through                               | `blizzard:journey`'s every-chunk work-item read, and `blizzard:e2e`'s own pass-through test   |
| 2, 3, 4 — exactly-once, zombie fencing, kill-9 | `blizzard:crash-sweep` plus the invariant checker                                             |
| 6, 7, 9, 11, 12                                | `blizzard:e2e`'s scenarios and `blizzard:journey`                                             |
| 13 — delivery-conflict reconcile               | the component-tier partial-land test, plus `blizzard:journey`'s clean multi-repo grouped land |
