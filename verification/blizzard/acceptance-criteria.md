# The MVP acceptance criteria (`bzh:matrix-acceptance-criteria`)

Which of the [matrix](../blizzard.md)'s methods exercises which acceptance criterion.

The MVP acceptance journey's thirteen criteria are exercised end to end by named methods: criteria 2/3/4 (exactly-once,
zombie fencing, kill-9) by `blizzard:crash-sweep` + the invariant checker; 6/7/9/11/12 by `blizzard:e2e`'s scenarios and
`blizzard:journey`; 1 (pass-through) by `blizzard:journey`'s every-chunk work-item read and `blizzard:e2e`'s own
pass-through test; and 13 (delivery-conflict reconcile) by the component-tier partial-land test plus
`blizzard:journey`'s clean multi-repo grouped land.
