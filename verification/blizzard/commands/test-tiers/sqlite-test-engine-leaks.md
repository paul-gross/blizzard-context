# `blizzard:sqlite-test-engine-leaks` detail (`bzh:matrix-sqlite-test-engine-leaks`)

<!-- rumdl-disable MD001 -->

The parallel-suite proof spoke of [`../test-tiers.md`](../test-tiers.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the command inventory.

### blizzard:sqlite-test-engine-leaks

Run `uv run pytest -n auto` from the blizzard repo root on Linux with procfs available. Retain the revision, exit
status, actual worker roster, and each worker's terminal inspection and, for workers that ran tests, last-test teardown
and inspection results. The proof passes when the command exits zero, every worker that ran tests has a passing
last-test teardown and a zero deleted-open file inspection, and every worker reports zero deleted-open files under its
own basetemp at terminal inspection. An idle worker has no last-test boundary to inspect. Missing or crashed workers are
not clean evidence. Each inspection runs inside its worker after relevant fixture finalizers; the terminal inspection
also follows pytest temporary-directory housekeeping. A controller-only or post-worker-exit scan cannot establish the
claim.

The guard also checks that test-owned SQLite handles are released before their still-existing store paths are removed;
it does not forbid unrelated live files. Cleanup runs on all platforms, but procfs inspection is Linux-only.
