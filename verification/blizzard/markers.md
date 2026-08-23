# The markers a matrix row carries (`bzh:matrix-markers`)

The `P3`–`P7` and **Gap** annotations the [matrix](../blizzard.md) rows and the spokes beside this one carry — what each
names, and when to write one.

## Phase markers

A phase marker dates the row against blizzard's bootstrap:

- **P3** — the service manifests.
- **P4** — the `blizzard-mock` fleet.
- **P5** — the `blizzard` scaffold.
- **P6** — the walking-skeleton acceptance loop.
- **P7** — the feature build: engine completeness (review + fail cycle, escalation, heartbeats, store-and-forward,
  fencing), the board and fleet ops, then the running-daemon service tier and the kill-9 crash sweep — all real as of
  wave 4.

## Gap markers

Every matrix row states a live command; none carries a Gap marker. Should a new row again precede its code, restore the
bootstrap convention: state the intended command, mark **Gap (phase N)**, and drop the marker in the change that lands
the method.

One Gap stands against the inventory rather than any single row: the tag `release` workflow's full-suite tiers reuse the
push-verified multi-repo setup but have not yet been exercised under a real `v*` tag.
