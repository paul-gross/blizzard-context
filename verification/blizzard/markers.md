# Bootstrap phases and Gap markers (`bzh:matrix-markers`)

The phase and Gap annotations carried by the [matrix](../blizzard.md)'s rows and by the spokes beside this one.

## Bootstrap phases

Bootstrap phases, referenced as `P3`–`P7` throughout the matrix rows and spokes: **P3** service manifests, **P4**
`blizzard-mock` fleet, **P5** `blizzard` scaffold, **P6** the walking-skeleton acceptance loop, **P7** the feature build
(engine completeness — review + fail cycle, escalation, heartbeats, store-and-forward, fencing; the board + fleet ops;
then the running-daemon service tier and the kill-9 crash sweep, all real as of wave 4).

## Gap markers

Every matrix row states a live command; none carries a Gap marker. Should a new row again precede its code, restore the
bootstrap convention: state the intended command, mark **Gap (phase N)**, and drop the marker in the change that lands
the method.

**Gap.** The tag `release` workflow's full-suite tiers reuse the push-verified multi-repo setup but have not yet been
exercised under a real `v*` tag.
