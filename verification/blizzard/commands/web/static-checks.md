# Angular static-check command detail (`bzh:matrix-command-web-static`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` headings, test/spec-filename code spans, and `npm run` script names are machine-checked — keep each verbatim, inside its own section. -->

The detail spoke for the Angular checks that need no browser — the AOT compile, generated-client drift, the structural
gate, and the bundle-composition check — under the Angular workspace hub, [`../web.md`](../web.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### web:lint

`npm run lint` in `web/` (`ng lint`, eslint over all four Angular projects). Carries a `max-lines` ceiling — the
~400-line cap, `skipBlankLines`/`skipComments` both off — over every `.ts` file each project's own config reads (spec
files at an 800-line ceiling instead, a runaway guard rather than design pressure). No architecture doc declares the
number itself; in practice the files it has caught were also
[`../../../../architecture/frontend-structure/containers.md`](../../../../architecture/frontend-structure/containers.md)
`bzh:frontend-container-presentational` splits, since an oversized component is often evidence of merged
container/presentational concerns, but the ceiling now reaches every `.ts` file this config reads, not only components.
Also carries a `no-restricted-syntax` rule over `ExportAllDeclaration` in `projects/*/src/lib/*/index.ts` —
[`../../../../architecture/frontend-structure/disjoint-diffs.md`](../../../../architecture/frontend-structure/disjoint-diffs.md)
`bzh:frontend-disjoint-diffs`'s ban on a sub-barrel `export *`, scoped so fleet's own `public-api.ts` stays legal.

### web:typecheck

`npm run build` in `web/` — a real AOT compile of both Angular apps, the type check `web:unit-test`'s esbuild-based
vitest never performs. Run it after adding or narrowing a required field on a shared interface, or changing an exported
signature: the construction sites such a change breaks stay green under every other web tier.

### web:client-drift

`npm run generate:client` in `web/` — openapi-ts codegen from `openapi/{hub,runner}.openapi.json` — then failing on any
unstaged diff in `web/`; owner [`../../../../standards/frontend.md`](../../../../standards/frontend.md), rule
`bzh:generated-client`. The Python half regenerates the specs via `uv run blizzard-export-openapi --out-dir openapi` and
fails the same way on an unstaged diff in `openapi/`. The diff is working tree against index, not `HEAD` — a
regeneration already `git add`ed passes.

### web:structural-gate

`npm run structural-gate` in `web/` (`web/scripts/structural-gate.js`) — a real-timer sweep over the specs the `test`
script (`npm run test`) actually runs, failing any `setTimeout`/`setInterval` whose delay is a non-zero integer literal
— a literal delay is a real second spent inside the merge gate, and a window guessed rather than chosen. A delay held in
a variable or expression is outside the pattern; `setTimeout(…, 0)` is the macrotask-flush idiom, deliberately
unmatched; and `*.shell-sweep.spec.ts` specs are out of scope — a real-Chromium frame wait is `web:shell-sweep`'s
method. A genuinely time-driven spec is named with its reason in `REAL_TIMER_EXEMPT_FILES` — today only
`demo-director.spec.ts`, whose waits poll a real router harness at the kiosk tour's measured cadence. Because the tree
is clean of the real-timer shape today, the gate first runs a fixture self-test — `assertRealTimerDetectorWorks`,
must-catch and must-pass shapes — and refuses to run if the detector stops classifying (rule
`bzh:case-pins-its-own-name`).

The same script also sweeps the kit floor
([`../../../../architecture/frontend-structure/kit.md`](../../../../architecture/frontend-structure/kit.md)
`bzh:frontend-kit-floor`): a component `.css` outside `fleet/lib/kit/` declaring one of the kit's own retired chrome
classes (`KitPanel`'s `.panel`/`.p-hdr`/`.p-body`/`.lbl`, `KitAsyncState`'s `.status` and its hand-rolled precursors
`.none`/`.hint`/`.rest`) as a standalone rule, or a component `.html` outside the kit hand-rolling `KitFactList`'s own
`<dl class="kv">` grid. A site that should not convert is named with its reason in `KIT_FLOOR_EXEMPT_SITES`, the
`REAL_TIMER_EXEMPT_FILES` idiom. Its own fixture self-test, `assertKitFloorDetectorWorks`, runs alongside
`assertRealTimerDetectorWorks` before either sweep does.

The script also censuses every TypeScript, template, and stylesheet below `web/projects` for the retired board Top/group
contract: its type, inputs, handlers, grouping mutation facade, and test handles. Generated grouping-client symbols are
deliberately outside that census: API and CLI grouping remain supported. `assertBoardControlDetectorWorks` first
exercises each retired shape and an allowed grouping-client shape, so a clean result cannot silently be a detector that
stopped classifying (`bzh:case-pins-its-own-name`).

A separate census over the same three extensions covers the chunk detail dock's retired dependency-management UI: the
free-text prerequisite input, the Declare/Release testids, the `DependencyEvent` type, the `declareDependency`/
`releaseDependency` outputs, and the `dependency.mutations.ts` mutation wrapper's own exports
(`injectDeclareDependencyMutation`, `injectReleaseDependencyMutation`, `DependencyVars`). The generated hub API client
and the hub CLI's `chunk depend`/`chunk release-dependency` commands stay outside it — only the frontend affordance
retired, not the surface it called. `assertDockControlDetectorWorks` runs the same must-catch/must-not-false-positive
proof against every retired shape before the sweep trusts it, the same `bzh:case-pins-its-own-name` guard the
board-control census follows.

The script also sweeps every mutation hook for the two shapes
[`../../../../architecture/frontend-structure/mutations.md`](../../../../architecture/frontend-structure/mutations.md)
declares tooled. `bzh:frontend-mutation-settles-on-refresh`'s half: a `queryClient.invalidateQueries(...)` call inside a
mutation hook that is `void`-discarded rather than returned (or `Promise.all`'d and returned) from `onSuccess`/
`onSettled`. No exemption list — the shape has no legitimate exception. Its own fixture self-test,
`assertInvalidateReturnedDetectorWorks`, runs alongside the other detectors' self-tests before the sweep trusts it
(`bzh:case-pins-its-own-name`).

`bzh:frontend-pending-override`'s half: `setQueryData` anywhere in a non-spec file under `projects/`, and `onMutate`
anywhere in a file calling `injectMutation(`. `setQueryData` is scanned everywhere, not only inside the file that
defines a mutation hook, because a *consumer* of a hook (a container calling `.mutate(vars, { onMutate: ... })`, say)
can write the cache just as easily as the hook itself — scoping the scan to `injectMutation(` alone would leave every
consumer free to do it instead. `onMutate` cannot be told apart from a cache-write snapshot/rollback by a static scan
alone, so it stays scoped to a defining file, where the ambiguity actually arises; a site that keeps `onMutate` for a
non-cache side effect is named in `NO_CACHE_WRITE_EXEMPT_FILES` with a one-line reason, the same reasoned-exemption
idiom the real-timer and kit-floor sweeps use. Its own fixture self-test, `assertNoCacheWriteDetectorWorks`, proves the
exemption does real work — an exempted fixture would still be caught without it — alongside the other detectors'
self-tests before the sweep trusts it (`bzh:case-pins-its-own-name`).

### web:bundle-composition

`npm run bundle-check` in `web/` (`web/scripts/bundle-check.js`) — the tooled half of
[`../../../../architecture/frontend-structure/eager-shell.md`](../../../../architecture/frontend-structure/eager-shell.md)
`bzh:frontend-eager-shell-entry`. Builds the hub app with esbuild's own metafile (`ng build hub --stats-json`, into a
temp directory) and resolves the initial chunk from it twice. At output granularity — the output whose entry point is
`main.ts`, plus every output it reaches over a static `import-statement` edge, a `dynamic-import` edge starting a lazy
chunk instead — it prints the per-area byte breakdown (framework, CDK, each fleet area) that a bundle-size change
records. At source-file granularity, over the same metafile's module graph, it enforces the gate: a source file
reachable that eagerly that matches a forbidden pattern — the fleet `chunk-detail/`, `garden/`, `graphs/`, or
`transcripts/` sub-barrels, `@dagrejs/*`, or `@angular/cdk`'s `menu`/`overlay` bundles — fails the run, named together
with the file that imports it. Its own fixture self-test, `assertBundleCompositionDetectorWorks` — one eager import
matching a forbidden pattern, one eager import that does not, and a forbidden pattern reached only through a dynamic
import — runs before the walk is trusted (`bzh:case-pins-its-own-name`). The `initial` budget in `angular.json` is the
size backstop the same build enforces. Wired into `gate.yml`'s `frontend` job and `scripts/ci-gate.sh` beside
`web:structural-gate`.
