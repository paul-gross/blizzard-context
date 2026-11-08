# Call through clients (`bzh:service-clients-only`)

Slot skeleton: `canon:rule-shape` (`winter-canon:/rule-shape.md`), at file-per-rule granularity. The sections after the
skeleton name the client surfaces a spec calls through — the contract the Rule slot requires, not skeleton drift.

## Rule

Send every daemon call through the harness clients, never raw `fetch` or a hand-built full URL. Add a missing route to
the appropriate client rather than bypassing it.

## Why

Clients supply tenant headers, authentication and response failure diagnostics consistently across shared hubs.

## Detect

`tests/eslint.config.mjs` rejects `fetch` in specs; a literal daemon URL or direct request context is a reviewable
signature that lint alone does not cover.

## Do

Use the fixture's `api`, `fleet`, or `forge` client for its corresponding surface, and in `runnerTest` the mock-hub
client on `mockHub` and the runner clients from `runnerHostClient`, `runnerStream`, and a `runnerHost`'s own `runners`
and `api`.

## Don't

Assemble `http://localhost:${port}/api/...` in a spec.

## The hub world's clients

The `federation` client drives a sign-in bounce from a browser at a runner host to the hub and back, holding the
runner's cookies and the hub's in separate contexts, since both answer on `127.0.0.1` and cookies ignore the port. To
act as anyone but the tenant's admin, use `user.api`, a person's `api` from `people`, or the `as:` option of `cli` and
`events.open`; a call made as a worker carries the credential [`./surfaces.md`](./surfaces.md) §A worker's credential
names.

## A runner host's handle

Beyond its clients, a `runnerHost` carries:

- `cli(args)` — runs the real `blizzard-runner` on its directory; a non-zero exit is a result, not a throw.
- `reconfigure`, `clearHubTokens`, `renameRunner` and `removeStore` — edit its stopped directory, never a file by hand.
- The `runnerOtlp` option and `host.otlp` — the option exports its telemetry to a test-owned sink, and `host.otlp` reads
  its spans, sum data points, and log records.
- `socketApi` — answers its shared routes (`health`, `exportTelemetry`) over its Unix socket as well, so a spec loops
  over both transports without importing `node:http` or `node:net`.
- The `runnerWinterTrap` option and `winterInvoked()` — the option puts a `winter` that records its invocation first on
  every host's `PATH`, a `runnerEnv.PATH` beside it refused, and `winterInvoked()` reports it.
- `mockSessions()` and `opencodeExports()` — read what the mock fleet wrote into the world the fixture minted: the mock
  harness's session records in the workspace, and the `mock-opencode` export documents under the host's own transcripts
  root.
- A runner's client — names each route a spec reads (`leases`, `leaseUsage`, `leaseTranscript`, `transcriptSegments`,
  `dashboard`, `heartbeat`), so a spec reaches no route through `raw`.

## Origins, and what a worker pushed

A host reads a branch head in its world's bare origins with `originHead(repo, branch)`, so a spec proves a worker's push
without running `git`; `originTree`, `originLog` (optionally by path) and `originFile` take that branch, or the sha
`originHead` answers, and read the pushed tree, history and file text, each `undefined` for a repo, ref or path that is
not there. The `runnerOnForge` option names forge repositories made before the host is, and `${forgeOrigins}` in
`runnerConfig` is the directory of the forge's bare repositories, `<owner>/<name>.git` below it, so a host whose
repository is the forge's own lands what a worker pushes.

A fleet test that drives delivery passes its `repository()` result to
`runnerHosts.create({ runnerRepositories: { [repo.name]: repo.origin! } })` before minting the graph: the host then
clones that mock-forge origin and its `originHead`, `originTree`, `originLog`, `originFile`, and `originMessage` read
the same bare git truth the forge merges. The default minted toy origins remain for runner-only tests. The `secondForge`
fixture starts a separate test-owned mock forge, with its own client and bare origins, and stops it when the test ends.
Register its repositories through the hub API and pass their actual origins to `runnerHosts.create`.

## The egress fixture

A `fresh-hub` test whose `hubConfig` names `${egress}` as `egress.directory` reads the files the hub exports, in the
format `egress.format` names (NDJSON by default), through the `egress` fixture:

- `query` and `recipe` — run the docs' own DuckDB load and the dictionary's views once a manifest names the dataset:
  `steps` and `invocations` through `<dataset>_newest`, `events` through `events_current` and `events_by_version`.
- `exports(dataset)` — asks once whether a manifest names the dataset.
- `rowTexts(dataset)` and `documents()` — render every copy of every row as text, and give the text of the manifests and
  schemas, so a scan that a value never left needs no file read of its own.
- `copies` — renders every copy of every `steps` or `invocations` row in the shape both formats share, so a test picks
  the newest copy itself and compares NDJSON with Parquet; a read may bind the dataset to the live passes' files or to a
  backfill's alone.
- `at(directory, format)` — reads another directory, such as a restart's second export.

`freshHub.start(overlay)` hosts the stopped hub again with a configuration merged over its file and checked as
`hubConfig` is, so one hub's record is exported under a second format; an unsound overlay is refused before anything is
written.

## A pasteable command

For a pasteable escalation command, call `runnerHost.shell(command, input)`: the handle executes the command as printed,
feeds the input to stdin, and uses the host's isolated, mock-fenced environment. A spec never spawns it.
