# Stay on public surfaces (`bzh:service-public-surfaces`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity. The sections after the
skeleton — what a runner spec reads, the stopped-store specimens the store folder admits, the per-run template, and a
worker's credential — are the contract the Rule slot requires, not skeleton drift.

## Rule

Build test state through public hub surfaces. Only a `fresh-hub` test whose subject is the store may inspect store
files, before the daemon starts or after it stops. Never seed with `tool:mock-data`. A runner spec reads the host
through its HTTP, socket, and stream surfaces; only `service/runner/store/` opens a runner store (`node:sqlite`) or
touches the disk (`node:fs`), before the host starts or after it stops, by the table and column names
`contracts/store/runner.json` declares.

## Why

A daemon service test must prove the wire and its actual effects; mutating a live store behind the daemon evades both
the public contract and concurrent isolation.

## Detect

`tests/eslint.config.mjs` rejects `node:child_process`, `node:http`, `node:https`, `node:net`, and `node:sqlite` in
every service spec, and `node:fs` in `service/runner/` and `service/fleet/`; `service/runner/store/` is the one folder
that admits `node:sqlite` and `node:fs`. Review mock-data invocations and the store-access timing; no static gate proves
them or the test's subject.

## Do

Create a repository, issue, or chunk through the fixture's hub client and observe it through the same surface.

## Don't

Insert rows directly into a shared hub's store to prepare an HTTP assertion.

## A runner spec reads routes, not its host's directory

Outside `service/runner/store/`, a runner spec never reads the host's own directory: not the worker stdout files, not
the harness-config snapshot, not the host's store. What a worker did is read from a route of the runner, or from the
world the mock fleet wrote into, through a reader on `runnerHost`. A value no route serves is added to the runner's
local API in the change that ports the test that needs it.

## Stopped-store specimens

In `service/runner/store/`, a directory's lock is held by a second real host: the subject's `data/host.lock` is a
symbolic link to that started host's lock file, and the refusal names that host's `runnerHost.pid`. A pre-host daemon is
the harness's `preHostDaemon` counterpart, and a directory no verb builds comes from the `scratchDirs` fixture, which
starts no mock hub. A directory a verb under test initialized boots through `runnerHosts.create({ runnerDir })`, which
leaves the directory to its owner. A spec reads a running host's file list, host file, and `.env`, never its store, and
reads a store's currentness through `blizzard-runner host --check`.

## Templates and cold initialization

Every hub stack, shared or fresh, and every runner host starts from a per-run template the harness built once with the
real `init` of each daemon: the hub restores its durable files, and the runner host copies the migrated `data/host.db`
before its own `blizzard-runner init` runs. A shared hub has no cold option; a spec that needs a cold hub declares
`fresh-hub` and takes `test.use({ coldInit: true })`, beside `runnerStarted` and `runnerDir`, as does a runner-host spec
whose subject is what `init` produces. `FreshHub.reset()` always runs `init` cold.

## A worker's credential

A call made as a worker carries the spawn credential the mock harness recorded — the `BLIZZARD_*` lease token, lease id,
and runner URL its runner exported — never a token the test mints, which proves a credential no worker holds.
