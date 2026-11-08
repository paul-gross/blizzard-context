# Configure through a profile (`bzh:service-config-is-a-profile`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity. The sections after the
skeleton — hub profiles, their environment fences, the runner's harnesses, bundles and stubs, host overlays, a stopped
host's reconfiguration, and subscription samples — are the contract the Rule slot requires, not skeleton drift.

## Rule

A hub-wide setting rides a test profile or a fresh hub, never a test that changes a shared hub in place.

## Why

A setting changed mid-run alters the behavior of concurrent tests on that hub.

## Detect

Review writes to hub-wide config within a spec and profile declarations under tests/service/hub/; the project discovery
in `tests/playwright.config.ts` provides the profile boundary, not a lint ban on config calls. The harness refuses
`hubConfig` or `hubEnv` below `fresh-hub`, a `hubEnv` name a profile owns, and a `profile.toml` under `service/runner/`
or `service/fleet/`.

## Do

Put a hub-wide variant in its own profile, or request a one-off case with
`test.use({ isolation: 'fresh-hub', hubConfig, hubEnv })`. A test that needs people belongs under the `auth` profile; a
test whose subject is the login throttle takes a `fresh-hub` with the throttle left on.

## Don't

Toggle a shared hub's feature flag before an assertion and toggle it back afterward.

## Hub profiles

A hub profile lives in `service/hub/` alone. A `service/fleet/` subfolder named after a hub profile, such as
`fleet/auth/`, runs as `service-fleet-auth` on that profile's hub with one worker; every other fleet spec runs as
`service-fleet` on the default profile's hubs, and a fleet test the cross-check raises to `fresh-hub` boots the profile
its project maps to.

## Environment fences

A profile cannot carry environment, so `tests/harness/profiles.ts` names the variables a profile's hubs start with. The
`actions` profile's, the test-action and crash fences, reach its shared hubs and any fresh hub raised in its project,
across restart and reset, and no other profile's hub. A spec that needs the fence lives under `fleet/actions/`, and a
test's `hubEnv` cannot name either variable.

## Harnesses, bundles, and stubs

A harness a spec runs on is enabled through `test.use({ runnerConfig })`, as `runner[].opencode` with
`${mockBin}/mock-opencode`, never in a `runner.toml`, which binds every spec in its folder. The host always holds a
synthetic OpenCode login at its private data home, as it holds a Claude one. A spec that moves a runner between OpenCode
releases names `${opencode}` as `runner[].opencode.binary` in place of `${mockBin}/mock-opencode`: a host-owned path
holding the `runnerOpencode` release when the host is built — `1`, the default, for OpenCode 1, or a version the
engine-backed OpenCode 2 mock reports — which `runnerHost.installOpencode()` replaces in place, as an operator's upgrade
does. A published harness bundle is given with the `runnerBundle` option, whose files the fixture writes into a
test-owned directory before the host boots and which a profile names as `${bundle}`, as in
`runner[].harness.config_dir`; the case then reads what a worker received of it off the lease's transcript. A worker's
PATH stub is given with `runnerStubs` (executable scripts the profile names as `${stubs}`, as in
`runner[].worker.path_prepend`); a stub or a bundle hook appends to `${logs}/<name>`, which the case reads back with
`runnerHost.workerLog(name)`.

## Host overlays

A runner host's configuration rides a profile the same way. `runner.toml` beside the spec, or
`test.use({ runnerConfig })` over it, is a host-file overlay checked against `contracts/config/host.json` before any
process starts. `runnerEnv` adds environment to the host process, and the harness refuses any name `daemon-env.json`
pins and the mock-harness fence. A profile never sets a key the CLI or the fixture owns, such as `hub_url`, `port`, or a
runner's `id`; a layout no CLI verb produces is made by editing the documented files, never by going through a runner
class.

## Stopped configuration

A layout no verb produces after first boot is a `reconfigure` of the stopped host, never a write to its store. For an
initialized, stopped host, `prepareStopped` can replace a runner's documented-file subscription, id, or token, and the
host token in `.env`, before `restart()` boots it. Token values come from enrollment; the seam never mints one. It
refuses edits while the host runs. A store specimen opens `data/host.db` only before boot or after stop, by the table
and column names `contracts/store/runner.json` declares (`bzh:service-public-surfaces`'s Rule,
[`./surfaces.md`](./surfaces.md) §Rule).

## Subscription samples

A runner spec produces a subscription sample through the vendor counterpart, never a store write: set what the
credential reports on `vendorUsage`, `stepHost()`, then read the recorded sample off `GET /api/host/subscriptions`. Mint
one credential per subscription so the counterpart can move one without the other, and take a held window's label from
that sampled read, never a literal. A usage-limited worker's named reset places its mark in a window only when it
matches a sampled `resetsAt` to the minute, so sample first and seed the limited chunk after.
