# `blizzard:harness-check` detail (`bzh:matrix-tier-harness-check`)

<!-- One flat `###` section per method id — the shape this file's sibling spokes share. -->
<!-- rumdl-disable MD001 -->

The harness-check spoke of the test-tier hub [`../test-tiers.md`](../test-tiers.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### blizzard:harness-check

`mise run playwright -- --project=harness --project=harness-auth --project=harness-runner --project=harness-actions`
runs the Playwright harness's own proof: its fixtures, its clients (including held and released host environments), its
profiles, and the test-owned mock hub and runner host. Run it after changing anything under `tests/harness/`, before
trusting a service or UI spec that rides the changed fixture.
