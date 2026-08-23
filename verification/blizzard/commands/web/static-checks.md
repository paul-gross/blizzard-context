# Angular static-check command detail (`bzh:matrix-command-web-static`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` headings, test/spec-filename code spans, and `npm run` script names are machine-checked — keep each verbatim, inside its own section. -->

The detail spoke for the Angular checks that need no browser — the AOT compile, generated-client drift, and the
structural gate — under the Angular workspace hub, [`../web.md`](../web.md). Read
[`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

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

`npm run structural-gate` in `web/` (`web/scripts/structural-gate.js`); every check it carries is live. A `max-lines`
ceiling — the ~400-line cap — holds over every Angular component file with no exemptions (`MAX_LINES_EXEMPT_FILES` is
empty); owner [`../../../../architecture/frontend-structure.md`](../../../../architecture/frontend-structure.md), rule
`bzh:frontend-container-presentational`.

A real-timer sweep covers the specs the `test` script (`npm run test`) actually runs, failing any
`setTimeout`/`setInterval` whose delay is a non-zero integer literal — a literal delay is a real second spent inside the
merge gate, and a window guessed rather than chosen. A delay held in a variable or expression is outside the pattern;
`setTimeout(…, 0)` is the macrotask-flush idiom, deliberately unmatched; and `*.shell-sweep.spec.ts` specs are out of
scope — a real-Chromium frame wait is `web:shell-sweep`'s method. A genuinely time-driven spec is named with its reason
in `REAL_TIMER_EXEMPT_FILES` — today only `demo-director.spec.ts`, whose waits poll a real router harness at the kiosk
tour's measured cadence. Because the tree is clean of the real-timer shape today, the gate first runs a fixture
self-test — `assertRealTimerDetectorWorks`, must-catch and must-pass shapes — and refuses to run if the detector stops
classifying (rule `bzh:case-pins-its-own-name`). The `max-lines` ceiling fires on real files and needs no equivalent
self-test.
