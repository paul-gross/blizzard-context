# Angular static-check command detail (`bzh:matrix-command-web-static`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` headings, test/spec-filename code spans, and `npm run` script names are machine-checked — keep each verbatim, inside its own section. -->

The checks over the Angular workspace that need no browser — the AOT compile, generated-client drift, and the structural
gate. Spoke of the [Angular workspace hub](../web.md).

Read [`../../../blizzard.md`](../../../blizzard.md) first for the short command and the method-id inventory;
[`../../commands.md`](../../commands.md) routes to the other methods' detail.

### web:typecheck

`npm run build` in `web/` — a real AOT compile of both Angular apps, the type check `web:unit-test`'s esbuild-based
vitest never performs. Run it after any change that adds or narrows a required field on a shared interface, or that
changes an exported function or method signature: the construction sites those changes break stay green under every
other web tier.

### web:client-drift

`npm run generate:client` in `web/` — openapi-ts codegen from `openapi/{hub,runner}.openapi.json` — then fail on any
unstaged diff in `web/` ([`../../../../standards/frontend.md`](../../../../standards/frontend.md),
`bzh:generated-client`). The check is a working-tree-vs-index `git diff`, not working-tree-vs-`HEAD` — a regeneration
already `git add`ed passes. The Python half regenerates the specs via `uv run blizzard-export-openapi --out-dir openapi`
and fails the same way on an unstaged diff in `openapi/`.

### web:structural-gate

`npm run structural-gate` in `web/` (`web/scripts/structural-gate.js`); every check in it is live.

One check is a `max-lines` ceiling — the ~400-line cap — over every Angular component file
([`../../../../architecture/frontend-structure.md`](../../../../architecture/frontend-structure.md),
`bzh:frontend-container-presentational`), with no exemptions — `MAX_LINES_EXEMPT_FILES` is empty.

The other check is a real-timer sweep over the specs the `test` target actually runs, failing a
`setTimeout`/`setInterval` whose delay is a non-zero integer literal — a real second spent inside the merge gate, and a
window guessed rather than chosen. Its boundaries: a delay held in a variable or expression is outside the pattern;
`setTimeout(…, 0)` is the macrotask-flush idiom and deliberately unmatched; and `*.shell-sweep.spec.ts` is out of scope,
since a real-Chromium frame wait is `web:shell-sweep`'s method. A genuinely time-driven spec is named in
`REAL_TIMER_EXEMPT_FILES` with its reason — today only `demo-director.spec.ts`, whose waits poll a real router harness
at the kiosk tour's own measured cadence. The tree is clean of the real-timer shape today, so the check carries a
fixture self-test (`assertRealTimerDetectorWorks`, must-catch and must-pass shapes) that refuses to run the gate at all
if the detector stops classifying (`bzh:case-pins-its-own-name`); the `max-lines` check fires on real files and needs no
equivalent.
