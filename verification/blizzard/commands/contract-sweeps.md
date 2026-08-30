# Contract and restatement sweep detail (`bzh:matrix-command-contracts`)

<!-- the `###` sections below are machine-parsed by `blizzard-context:/scripts/check-registry-drift.py`'s `_sections(text, "###")` — at `##` it reads no sections at all. -->
<!-- rumdl-disable MD001 -->
<!-- The `###` headings, test-filename code spans, and `mise run` task names are machine-checked — keep them verbatim, in their sections. -->

These sweeps gate a shape rather than a behavior. Read [`../../blizzard.md`](../../blizzard.md) first for the short
command and the method-id inventory; [`../commands.md`](../commands.md) routes to the other methods' detail.

### blizzard:sse-contract

`mise run sse-contract` gates the SSE frame shape against the golden corpus `contracts/sse/`: `manifest.json`,
`README.md`'s forward-compatibility policy, and one `<kind>.json` per frame kind. The corpus is two self-contained
scopes — hub at `contracts/sse/`'s top level (`blizzard.hub.events.broker`), runner at `contracts/sse/runner/`
(`blizzard.runner.events.broker`) — each with its own `manifest.json`, framing constants, and reserved open-of-stream
comment. Each scope asserts its own closure: the on-disk kind set, the `manifest.json` kind list, that daemon's Python
`EVENT_TYPES` tuple, and its TS event-type tuple must all be equal.

Both suites read the same physical goldens — no per-side copy — so moving a golden reddens the side that has not caught
up, and changing a side's shape without moving the golden reddens that side. Each drives both scopes; no runner-only
test module or spec basename exists — the method's surface is exactly these two files:

- The Python half, `tests/test_sse_contract.py` (`blizzard:component-test`), drives the real `EventBroker.publish_*`
  helper per case and asserts `json.loads(event.data) == payload`, then validates the same golden against its
  `blizzard.wire.sse` model (`extra="forbid"`) and round-trips it losslessly.
- The board half, `web/projects/fleet/src/lib/sse/sse-contract.spec.ts` (`web:unit-test`), feeds every golden — framed
  exactly as its owning daemon frames it — through a stubbed `fetch` into the real `SseService`/`FetchEventSource`
  byte-stream reader and asserts on what reaches `SseHandle.events`.

Per-scope compile-time frame-field-spec descriptors — `HUB_FRAME_FIELD_SPECS` off `fleet-live.ts`'s exported per-kind
interfaces, `RUNNER_FRAME_FIELD_SPECS` off `runner-events.ts`'s — stop compiling when an interface field is renamed or
dropped, and at runtime cross-check each golden's key set against its scope's spec. The compile-time half holds only
because each slot is authored through the spec's own exactness helper: a bare `Record<Keys<T>, true>` degrades to `{}`
when a kind has no fields in that slot, and TypeScript excess-property-checks nothing against `{}`, so a stale key there
would otherwise compile clean.

The runner scope carries a third assertion the hub scope has no counterpart for: each case of a kind that carries a
`cause` is named for that cause and must actually carry it. Four runner kinds' cases are key-set-identical, so the
key-set check alone cannot tell one from another and the case name would pin nothing
([`../evidence.md`](../evidence.md), `bzh:case-pins-its-own-name`).

`blizzard:manual-sse-probe` remains the method for what only a live socket proves — framing and timing, not field shape
— over either daemon's stream.

### blizzard:cli-contract

`uv run pytest tests/test_cli_surface_contract.py` gates the `blizzard hub` and `blizzard runner` command trees against
the golden corpus `contracts/cli/`: one `<root>.json` per root group, each holding every command node recursively
reached from it — its full path, help text, short help, and its parameters' spellings, kinds, types, and required/hidden
flags, in declaration order.

Both the corpus and the live tree the test diffs it against are built by the same walker, `blizzard.tools.cli_surface`,
over plain `click` introspection (`click.Group.commands`, `click.Command.params`) — no invocation, no I/O. `build()`
recurses a root group into a nested `path`/`help`/`short_help`/`params`/`commands` shape; `export()` writes `hub.json`
and `runner.json` from it, and `uv run python -m blizzard.tools.cli_surface` is the regeneration entry point after a
deliberate CLI change. A command's raw `.help` is `inspect.cleandoc`'d the same way click's own renderer does, so the
corpus is not the interpreter-version-dependent artifact a docstring literal's compile-time dedent (3.13+) versus its
absence (earlier) would otherwise make it.

The guard is a pure equality check with no forward-compatibility carve-out — unlike the SSE corpus's consumer-tolerance
policy, an unknown field or a reordered parameter is exactly the drift this method exists to catch, ahead of the CLI's
decomposition into by-concept packages: the surface must render identically at every step of that move.

### blizzard:restatement-sweep

The check fails on a census fact (`scripts/restated-invariants.json`) stated at an undeclared site (`new`), a declared
site no longer observed (`stale`), a declared non-owner site carrying no reason, or a designated owner not stating its
fact ([`../../../standards/one-prose-home.md`](../../../standards/one-prose-home.md)). The full command —
`mise run restatement-check` for short:

```bash
uv run python scripts/restated_invariants.py check --strict --owners --context-root ../blizzard-context src tests docs README.md web/projects ../blizzard-mock/src
```

Local-only via `--context-root`: `../blizzard-mock` is already a CI sibling, but `../blizzard-context` is checked out
nowhere in CI, and an unresolved `--context-root` refuses a green rather than skipping silently.

Refresh a `new`/`stale` finding with `measure --write-sites`, which rewrites `sites[]` to the observed tree — never by
hand — plus a `reason` on any new non-owner site. `measure --write-sites` refuses a partial scan (a file skipped as
unreadable or unparsable) unless `--force`; `check` instead reports a skipped file as an informational `skipped` finding
without failing, so a clean verdict claims only the scanned files.
