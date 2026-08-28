# Angular workspace command detail (`bzh:matrix-command-web`)

Full per-method detail for the [`../../blizzard.md`](../../blizzard.md) Commands rows that verify the Angular workspace
— what each command runs, what it asserts, and what it cannot see. Read [`../../blizzard.md`](../../blizzard.md) first
for the short command and the method-id inventory; [`../commands.md`](../commands.md) routes to the other methods'
detail.

Each method's `### <method-id>` section lives in the spoke below that owns it, split on whether the claim can be
evaluated without a browser.

## Routing

| File                                         | Read when…                                                                                                                                        |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`static-checks.md`](./web/static-checks.md) | …you are running `web:lint`, `web:typecheck`, `web:client-drift`, or `web:structural-gate` — the checks that read the source and need no browser. |
| [`shell-sweep.md`](./web/shell-sweep.md)     | …you are running `web:shell-sweep`, or adding a `*.shell-sweep.spec.ts` — the real-Chromium method and the roster every spec is checked against.  |
